import React from 'react';
import { AbsoluteFill, Img, random, staticFile, useCurrentFrame } from 'remotion';
import { clamp, ease, ramp } from '../lib/lib';
import { assetPath } from '../types';
import { SceneProps, Label, CUTOUT_SHADOW, enterFx, idleFx, hiddenAmount, hideFx, useFrameSize, useTheme } from './common';

// Sân khấu sống: cùng một bối cảnh đổi trạng thái theo thời gian, có không khí, mặt nước, cutout cử động.
// props: cam, focus (như Parallax), bg_filter
//   grade: [{at_s, b, s, c, h (độ), sepia, sky: [r,g,b,a], dark}] nội suy giữa các mốc
//   atmosphere: [{type: "mist"|"embers"|"firerain"|"ash"|"rain"|"snow"|"dust"|"fireflies"|"smoke"|"leaves"|"debris"|"lightning", at_s, to_s, n, color, y, x, angle}]
//     rain: mưa xiên (angle độ), snow: tuyết rơi, dust: bụi lơ lửng trong nắng, fireflies: đom đóm, smoke: khói bốc từ (x, y),
//     leaves: lá rơi, debris: đá vụn rơi từ trần (đi với quake), lightning: chớp sáng cả khung ở at_s
//   water: {poly: [[x,y]...], top, bottom, amp, boost: [{at_s, to_s, amp}]}
//   layers: [{asset | sprite: {base, clips: [{name, n, at_s, loop}]}, x, y, h, depth, at_s, to_s, enter, flip, motion, hide, unmask_s,
//             path: [{at_s, x, y}], shadow: {w, o} | false (w ≤ 3: tỷ lệ theo bề ngang cutout, lớn hơn: px), tone (CSS filter riêng, thắng tone_auto),
//             rim (true: viền sáng theo nguồn sáng), blur, wind, float (true: bay/lơ lửng, không bóng tiếp đất)}]
//   Mặc định (theme.stage, kênh tắt được): cutout đứng trên nền có bóng tiếp đất; mép cutout làm mềm 1 px (bỏ viền sáng/bẩn);
//   tone_auto (stage_prep.py ghi vào scenes.json) cân độ sáng, bão hòa, ám màu của cutout theo vùng nền dưới chân.
//   mist và smoke vẽ sau nhân vật (front: true để vẽ trước), sương tản theo chiều dọc, không thành dải ngang.
const lerp = (a: number, b: number, k: number) => a + (b - a) * k;
const FIELDS = { b: 1, s: 1, c: 1, h: 0, sepia: 0, dark: 0 } as Record<string, number>;

const gradeAt = (keys: any[], t: number) => {
  const out: Record<string, any> = { ...FIELDS, sky: [0, 0, 0, 0] };
  if (!keys?.length) return out;
  let i = 0;
  while (i < keys.length - 1 && t >= keys[i + 1].at_s) i++;
  const a = keys[i], b = keys[Math.min(i + 1, keys.length - 1)];
  const k = t < a.at_s || a === b ? (t < a.at_s ? 0 : 1) : ease(clamp((t - a.at_s) / Math.max(0.01, b.at_s - a.at_s)));
  for (const f of Object.keys(FIELDS)) out[f] = lerp(a[f] ?? FIELDS[f], b[f] ?? FIELDS[f], k);
  const sa = a.sky || [0, 0, 0, 0], sb = b.sky || [0, 0, 0, 0];
  out.sky = sa.map((v: number, n: number) => lerp(v, sb[n], k));
  return out;
};

const pathAt = (path: any[] | undefined, key: 'x' | 'y', v: number, t: number) => {
  if (!path?.length) return v;
  let i = 0;
  while (i < path.length - 1 && t >= path[i + 1].at_s) i++;
  const a = path[i], b = path[Math.min(i + 1, path.length - 1)];
  const av = a[key] ?? v;
  if (t < a.at_s || a === b) return av;
  return lerp(av, b[key] ?? v, clamp((t - a.at_s) / (b.at_s - a.at_s)));
};

const spriteSrc = (sp: any, t: number, fps: number) => {
  const clips: any[] = sp.clips;
  let c = clips[0];
  for (const x of clips) if (t >= (x.at_s || 0)) c = x;
  const raw = Math.max(0, Math.floor((t - (c.at_s || 0)) * fps));
  const i = c.loop === false ? Math.min(raw, c.n - 1) : raw % c.n;
  return staticFile(assetPath(`${sp.base}/${c.name}/${String(i).padStart(3, '0')}.webp`));
};

// Mặt nước: cắt ảnh nền thành các dải ngang rồi lệch theo sóng, xuống gần máy thì lệch nhiều hơn
const Water: React.FC<{ asset: string; w: any; t: number }> = ({ asset, w, t }) => {
  const { W, H } = useFrameSize();
  const top = w.top ?? H - 300, bottom = w.bottom ?? H, step = 6;
  let amp = w.amp ?? 3;
  for (const b of w.boost || []) amp += (b.amp - amp) * ramp(t, b.at_s, b.at_s + 0.3) * (1 - ramp(t, b.to_s - 0.4, b.to_s));
  const rows: React.ReactNode[] = [];
  for (let y = top; y < bottom; y += step) {
    const near = (y - top) / (bottom - top);
    const dx = amp * (0.25 + near) * (Math.sin(y * 0.09 + t * 2.1) + 0.6 * Math.sin(y * 0.23 - t * 3.3));
    rows.push(
      <div key={y} style={{ position: 'absolute', left: 0, top: y, width: W, height: step + 1, overflow: 'hidden' }}>
        <Img src={staticFile(assetPath(asset))} style={{ position: 'absolute', left: dx, top: -y, width: W, height: H, objectFit: 'cover' }} />
      </div>
    );
  }
  const poly = (w.poly || []).map((p: number[]) => `${p[0]}px ${p[1]}px`).join(',');
  return <AbsoluteFill style={{ clipPath: poly ? `polygon(${poly})` : undefined }}>{rows}</AbsoluteFill>;
};

const Atmosphere: React.FC<{ a: any; t: number }> = ({ a, t }) => {
  const { W, H } = useFrameSize();
  const on = ramp(t, a.at_s || 0, (a.at_s || 0) + 0.5) * (a.to_s != null ? 1 - ramp(t, a.to_s - 0.4, a.to_s) : 1);
  if (on <= 0) return null;
  const n = a.n ?? 40;
  const items: React.ReactNode[] = [];
  for (let i = 0; i < n; i++) {
    const r1 = random(`${a.type}-${i}-a`), r2 = random(`${a.type}-${i}-b`), r3 = random(`${a.type}-${i}-c`);
    if (a.type === 'mist') {
      // Sương tản theo chiều dọc (spread px), mảng cao và mờ, màu trung tính: không thành dải trắng vàng nằm ngang (bài học 87)
      if (i >= (a.n ?? 16)) continue;
      const w = 600 + r1 * 600, x = ((r2 * 2400 + t * (12 + r3 * 20)) % 2500) - 500, y = (a.y ?? 520) + (r3 - 0.5) * (a.spread ?? 520) - w * 0.2;
      items.push(<div key={i} style={{ position: 'absolute', left: x, top: y, width: w, height: w * 0.45, borderRadius: '50%', background: `radial-gradient(closest-side, ${a.color || 'rgba(225,228,230,0.32)'}, transparent)`, opacity: (0.22 + r1 * 0.28) * on }} />);
    } else if (a.type === 'firerain') {
      const speed = 620 + r1 * 520, life = 2200 / speed, ph = (t * (1 / life) + r2) % 1;
      const x = r3 * (W + 580) - ph * 500, y = ph * (H + 220) - 180, len = 70 + r1 * 120;
      items.push(<div key={i} style={{ position: 'absolute', left: x, top: y, width: 2 + r2 * 2.5, height: len, borderRadius: 3, transform: 'rotate(24deg)', background: 'linear-gradient(180deg, transparent, #ff9a3c 55%, #fff1c7)', boxShadow: '0 0 12px rgba(255,140,50,0.85)', opacity: on * (0.5 + r2 * 0.5) }} />);
    } else if (a.type === 'embers') {
      const ph = (t * (0.1 + r1 * 0.16) + r2) % 1, x = r3 * W + Math.sin(t * 1.6 + i) * 22, y = H + 40 - ph * (H - 180), s = 2 + r1 * 5;
      items.push(<div key={i} style={{ position: 'absolute', left: x, top: y, width: s, height: s, borderRadius: '50%', background: '#ffb35c', boxShadow: '0 0 10px #ff7a26', opacity: on * Math.sin(ph * Math.PI) }} />);
    } else if (a.type === 'ash') {
      const ph = (t * (0.05 + r1 * 0.07) + r2) % 1, x = r3 * W + Math.sin(t * 0.8 + i) * 40, y = ph * (H + 100) - 50, s = 2 + r1 * 6;
      items.push(<div key={i} style={{ position: 'absolute', left: x, top: y, width: s, height: s, borderRadius: '50%', background: a.color || 'rgba(205,200,190,0.8)', filter: `blur(${r2 * 1.5}px)`, opacity: on * Math.sin(ph * Math.PI) }} />);
    } else if (a.type === 'rain') {
      const ang = a.angle ?? 14, speed = 1500 + r1 * 700, ph = (t * speed / (H + 300) + r2) % 1;
      const x = r3 * (W + 400) - 200 - ph * (H + 300) * Math.tan((ang * Math.PI) / 180), y = ph * (H + 300) - 200, len = 70 + r1 * 80;
      items.push(<div key={i} style={{ position: 'absolute', left: x, top: y, width: 2.5 + r2 * 1.5, height: len, transform: `rotate(${ang}deg)`, background: `linear-gradient(180deg, transparent, ${a.color || 'rgba(225,235,245,0.9)'})`, opacity: on * (0.5 + r3 * 0.45) }} />);
    } else if (a.type === 'snow') {
      const ph = (t * (0.04 + r1 * 0.05) + r2) % 1, x = r3 * W + Math.sin(t * 0.9 + i) * 30, y = ph * (H + 60) - 30, s = 3 + r1 * 6;
      items.push(<div key={i} style={{ position: 'absolute', left: x, top: y, width: s, height: s, borderRadius: '50%', background: a.color || 'rgba(245,248,252,0.9)', filter: `blur(${r2 * 1.2}px)`, opacity: on * (0.6 + r3 * 0.4) }} />);
    } else if (a.type === 'dust') {
      const x = r1 * W + Math.sin(t * (0.2 + r2 * 0.3) + i) * 60, y = (a.y ?? H * 0.45) + (r2 - 0.5) * H * 0.7 + Math.cos(t * (0.15 + r3 * 0.2) + i) * 40, s = 1.5 + r3 * 2.5;  // bụi phải kín đáo, không có quầng sáng để không giống đom đóm (Sếp 2026-11-03)
      items.push(<div key={i} style={{ position: 'absolute', left: x, top: y, width: s, height: s, borderRadius: '50%', background: a.color || 'rgba(235,228,210,0.8)', filter: `blur(${0.4 + r1 * 0.8}px)`, opacity: on * (0.18 + 0.3 * (0.5 + 0.5 * Math.sin(t * (1 + r1) + i))) }} />);
    } else if (a.type === 'fireflies') {
      const x = r1 * W + Math.sin(t * (0.5 + r2) + i * 1.7) * 80, y = (a.y ?? H * 0.6) + (r2 - 0.5) * 360 + Math.cos(t * (0.4 + r3) + i) * 50, s = 3 + r3 * 3;
      items.push(<div key={i} style={{ position: 'absolute', left: x, top: y, width: s, height: s, borderRadius: '50%', background: a.color || '#e8ff9a', boxShadow: '0 0 18px 6px rgba(220,255,140,0.6)', opacity: on * (0.25 + 0.75 * Math.max(0, Math.sin(t * (1.2 + r1 * 1.5) + i * 2.3))) }} />);
    } else if (a.type === 'smoke') {
      const ph = (t * (0.08 + r1 * 0.06) + r2) % 1, s = 80 + ph * 320, x = (a.x ?? W / 2) + (r3 - 0.5) * 80 + ph * 120 * Math.sin(i), y = (a.y ?? H * 0.6) - ph * 520;
      items.push(<div key={i} style={{ position: 'absolute', left: x - s / 2, top: y - s / 2, width: s, height: s, borderRadius: '50%', background: `radial-gradient(closest-side, ${a.color || 'rgba(215,210,200,0.6)'}, transparent)`, opacity: on * Math.sin(ph * Math.PI) }} />);
    } else if (a.type === 'leaves') {
      const ph = (t * (0.06 + r1 * 0.05) + r2) % 1, x = r3 * W + Math.sin(t * 1.4 + i) * 70 + ph * 160, y = ph * (H + 80) - 40, rot = t * (60 + r1 * 120) + i * 40;
      items.push(<div key={i} style={{ position: 'absolute', left: x, top: y, width: 14 + r2 * 8, height: 7 + r2 * 4, borderRadius: '50% 0', background: a.color || '#5f7a3a', transform: `rotate(${rot}deg) scaleY(${Math.cos(t * 3 + i)})`, opacity: on * 0.85 }} />);
    } else if (a.type === 'debris') {
      const life = 1.1 + r1 * 0.8, ph = ((t - (a.at_s || 0)) / life + r2) % 1, x = (a.x ?? W / 2) + (r3 - 0.5) * (a.w ?? W * 0.8), y = (a.y ?? 0) + ph * ph * (H + 100), s = 3 + r1 * 9;
      items.push(<div key={i} style={{ position: 'absolute', left: x, top: y, width: s, height: s * (0.6 + r2 * 0.6), background: a.color || '#6b5d4c', borderRadius: 2, transform: `rotate(${t * 300 * r3}deg)`, opacity: on * (1 - ph * 0.3) }} />);
    }
  }
  if (a.type === 'lightning') {
    const k = t - (a.at_s || 0);
    const flash = k < 0 || k > 0.7 ? 0 : Math.max(0, 1 - k / 0.12) * 0.85 + (k > 0.22 && k < 0.4 ? 0.55 * (1 - (k - 0.22) / 0.18) : 0);
    return flash > 0 ? <AbsoluteFill style={{ pointerEvents: 'none', background: a.color || 'rgba(225,235,255,1)', opacity: flash, mixBlendMode: 'screen' }} /> : null;
  }
  return <AbsoluteFill style={{ pointerEvents: 'none' }}>{items}</AbsoluteFill>;
};

// Mép mềm: co viền alpha 1 px rồi làm nhòe 1 px, cắt ảnh theo alpha mới: bỏ viền sáng còn sót khi tách nền
const SoftEdgeDefs = () => (
  <svg width={0} height={0} style={{ position: 'absolute' }}>
    <filter id="cutout-soft" x="-5%" y="-5%" width="110%" height="110%">
      <feMorphology in="SourceAlpha" operator="erode" radius="1" result="e" />
      <feGaussianBlur in="e" stdDeviation="1" result="b" />
      <feComposite in="SourceGraphic" in2="b" operator="in" />
    </filter>
  </svg>
);
const BEHIND = (a: any) => (a.type === 'mist' || a.type === 'smoke') && !a.front;

export const Stage: React.FC<SceneProps> = ({ dur, asset, props, lead = 0 }) => {
  const frame = useCurrentFrame();
  const st = useTheme().stage || {};
  const f = frame - lead;
  const t = f / 30;
  const k = ease(clamp(frame / dur));
  const cam = props.cam || 'in';
  const { W, H } = useFrameSize();
  const [cx, cy] = props.focus || [W / 2, H / 2];
  const zoom = cam === 'in' ? 0.06 * k : cam === 'out' ? 0.06 * (1 - k) : cam === 'up' || cam === 'down' ? 0.04 : 0.02;
  // Lia/nghiêng phải nằm trong phần ảnh dư do phóng to, nếu không mép ảnh lộ dải đen.
  // Phóng đủ để chứa độ lia (tối đa 1.15), rồi kẹp độ lia trong phần dư đó (focus sát mép thì lia ít lại).
  const maxPan = cam === 'left' || cam === 'right' ? 40 : 0, maxTilt = cam === 'up' || cam === 'down' ? 28 : 0;
  const need = (m: number, c: number, size: number) => {
    const half = Math.min(c, size - c);
    return m && half > m ? 1 / (1 - m / half) : m ? Infinity : 1;
  };
  const S = Math.min(1.15, Math.max(1.02 + zoom, need(maxPan, cx, W), need(maxTilt, cy, H)));
  const room = (v: number, c: number, size: number) => clamp(v, -(size - c) * (S - 1) / S, c * (S - 1) / S);
  const pan = room(cam === 'left' ? 40 - 80 * k : cam === 'right' ? -40 + 80 * k : 0, cx, W);
  const tilt = room(cam === 'up' ? -28 + 56 * k : cam === 'down' ? 28 - 56 * k : 0, cy, H);
  const g = gradeAt(props.grade, t);
  const filter = `brightness(${g.b}) saturate(${g.s}) contrast(${g.c}) hue-rotate(${g.h}deg) sepia(${g.sepia})`;
  const [sr, sg, sb, sa] = g.sky;
  const layers: any[] = props.layers || [];
  const atm: any[] = props.atmosphere || [];
  return (
    <AbsoluteFill style={{ overflow: 'hidden', background: '#000' }}>
      {st.soft_edge !== false ? <SoftEdgeDefs /> : null}
      <AbsoluteFill style={{ filter }}>
        <AbsoluteFill style={{ transformOrigin: `${cx}px ${cy}px`, transform: `scale(${S}) translate(${pan}px,${tilt}px)` }}>
          {asset ? <Img src={staticFile(assetPath(asset))} style={{ position: 'absolute', width: W, height: H, objectFit: 'cover', filter: props.bg_filter }} /> : null}
          {asset && props.water ? <Water asset={asset} w={props.water} t={t} /> : null}
        </AbsoluteFill>
        {atm.filter(BEHIND).map((a: any, i: number) => <Atmosphere key={'b' + i} a={a} t={t} />)}
        {sa > 0 ? <AbsoluteFill style={{ mixBlendMode: 'hard-light', background: `linear-gradient(180deg, rgba(${sr},${sg},${sb},${sa}) 0%, rgba(${sr},${sg},${sb},${sa * 0.75}) 45%, rgba(${sr},${sg},${sb},${sa * 0.3}) 75%, rgba(${sr},${sg},${sb},0) 100%)` }} /> : null}
        {layers.map((l, i) => {
          if (l.to_s != null && t > l.to_s) return null;
          const d = l.depth ?? 0.6;
          const s = 1 + zoom * (1 + 2 * d);
          const x = (pathAt(l.path, 'x', l.x ?? W / 2, t) - cx) * s + cx + pan * (1 + 1.5 * d);
          const y = (pathAt(l.path, 'y', l.y ?? H - 80, t) - cy) * s + cy + tilt * (1 + 1.5 * d);
          const [o, sc, dy] = enterFx(f, (l.at_s || 0) * 30, l.enter || 'fade');
          const out = l.to_s != null ? 1 - ramp(t, l.to_s - 0.3, l.to_s) : 1;
          const hid = hideFx(l.hide, hiddenAmount(f, l.hide, l.unmask_s));
          const src = l.sprite ? spriteSrc(l.sprite, t, 30) : staticFile(assetPath(l.asset));
          const wind = l.wind ? ` rotate(${0.7 * Math.sin(t * 1.3 + i)}deg)` : '';
          const rim = l.rim ? ' drop-shadow(3px -1px 1.5px rgba(255,205,140,0.45))' : '';
          const soft = st.soft_edge !== false && !l.sprite ? 'url(#cutout-soft)' : '';
          const tone = l.tone ?? (st.auto_tone !== false ? l.tone_auto : '');
          const fx = [soft, hid.filter, tone, l.blur ? `blur(${l.blur}px)` : '', l.hide || l.blur ? '' : CUTOUT_SHADOW].filter(Boolean).join(' ') + rim;
          // Bóng tiếp đất: mặc định cho cutout đứng trên nền (không ẩn, không nhòe, không bay); w ≤ 3 là tỷ lệ bề ngang cutout
          const lw = (l.h || 600) * (l.aspect || 1);
          const sh = l.shadow === false ? null : l.shadow || (st.ground_shadow !== false && !l.hide && !l.blur && !l.float ? { w: 0.7, o: 0.55 } : null);
          const shW = sh ? (sh.w <= 3 ? sh.w * lw : sh.w) : 0;
          return (
            <React.Fragment key={i}>
              {sh ? (
                <div style={{ position: 'absolute', left: x - (shW * s) / 2, top: y - Math.max(18, shW * 0.06) * s, width: shW * s, height: Math.max(36, shW * 0.12) * s, borderRadius: '50%', background: 'radial-gradient(closest-side, rgba(12,8,4,0.62), transparent)', opacity: o * out * (sh.o ?? 1) }} />
              ) : null}
              <Img
                src={src}
                style={{ position: 'absolute', left: x, top: y + dy, height: (l.h || 600) * s, opacity: o * out * hid.opacity, transformOrigin: '50% 100%', transform: `translate(-50%,-100%) ${idleFx(f, l.motion, i)}${wind} scale(${sc}) scaleX(${l.flip ? -1 : 1})`, filter: fx, clipPath: hid.clipPath }}
              />
            </React.Fragment>
          );
        })}
      </AbsoluteFill>
      {g.dark > 0 ? <AbsoluteFill style={{ background: `rgba(6,5,4,${g.dark})` }} /> : null}
      {atm.filter((a) => !BEHIND(a)).map((a: any, i: number) => <Atmosphere key={i} a={a} t={t} />)}
      {props.label ? <Label text={props.label} sub={props.sub} from={8} to={dur - 10} /> : null}
    </AbsoluteFill>
  );
};
