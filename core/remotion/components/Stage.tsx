import React from 'react';
import { AbsoluteFill, Img, random, staticFile, useCurrentFrame } from 'remotion';
import { clamp, ease, ramp } from '../lib/lib';
import { assetPath } from '../types';
import { SceneProps, Label, CUTOUT_SHADOW, enterFx, idleFx, hiddenAmount, hideFx } from './common';

// Sân khấu sống: cùng một bối cảnh đổi trạng thái theo thời gian, có không khí, mặt nước, cutout cử động.
// props: cam, focus (như Parallax), bg_filter
//   grade: [{at_s, b, s, c, h (độ), sepia, sky: [r,g,b,a], dark}] nội suy giữa các mốc
//   atmosphere: [{type: "mist"|"embers"|"firerain"|"ash", at_s, to_s, n, color, y}]
//   water: {poly: [[x,y]...], top, bottom, amp, boost: [{at_s, to_s, amp}]}
//   layers: [{asset | sprite: {base, clips: [{name, n, at_s, loop}]}, x, y, h, depth, at_s, to_s, enter, flip, motion, hide, unmask_s,
//             path: [{at_s, x, y}], shadow: {w, o}, tone (CSS filter riêng), rim (true: viền sáng theo nguồn sáng), blur, wind}]
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
  const top = w.top ?? 780, bottom = w.bottom ?? 1080, step = 6;
  let amp = w.amp ?? 3;
  for (const b of w.boost || []) amp += (b.amp - amp) * ramp(t, b.at_s, b.at_s + 0.3) * (1 - ramp(t, b.to_s - 0.4, b.to_s));
  const rows: React.ReactNode[] = [];
  for (let y = top; y < bottom; y += step) {
    const near = (y - top) / (bottom - top);
    const dx = amp * (0.25 + near) * (Math.sin(y * 0.09 + t * 2.1) + 0.6 * Math.sin(y * 0.23 - t * 3.3));
    rows.push(
      <div key={y} style={{ position: 'absolute', left: 0, top: y, width: 1920, height: step + 1, overflow: 'hidden' }}>
        <Img src={staticFile(assetPath(asset))} style={{ position: 'absolute', left: dx, top: -y, width: 1920, height: 1080, objectFit: 'cover' }} />
      </div>
    );
  }
  const poly = (w.poly || []).map((p: number[]) => `${p[0]}px ${p[1]}px`).join(',');
  return <AbsoluteFill style={{ clipPath: poly ? `polygon(${poly})` : undefined }}>{rows}</AbsoluteFill>;
};

const Atmosphere: React.FC<{ a: any; t: number }> = ({ a, t }) => {
  const on = ramp(t, a.at_s || 0, (a.at_s || 0) + 0.5) * (a.to_s != null ? 1 - ramp(t, a.to_s - 0.4, a.to_s) : 1);
  if (on <= 0) return null;
  const n = a.n ?? 40;
  const items: React.ReactNode[] = [];
  for (let i = 0; i < n; i++) {
    const r1 = random(`${a.type}-${i}-a`), r2 = random(`${a.type}-${i}-b`), r3 = random(`${a.type}-${i}-c`);
    if (a.type === 'mist') {
      const w = 700 + r1 * 700, x = ((r2 * 2400 + t * (16 + r3 * 26)) % 2500) - 500, y = (a.y ?? 520) + (r3 - 0.5) * 170;
      items.push(<div key={i} style={{ position: 'absolute', left: x, top: y, width: w, height: w * 0.22, borderRadius: '50%', background: `radial-gradient(closest-side, ${a.color || 'rgba(255,240,220,0.5)'}, transparent)`, opacity: (0.35 + r1 * 0.45) * on }} />);
    } else if (a.type === 'firerain') {
      const speed = 620 + r1 * 520, life = 2200 / speed, ph = (t * (1 / life) + r2) % 1;
      const x = r3 * 2500 - ph * 500, y = ph * 1300 - 180, len = 70 + r1 * 120;
      items.push(<div key={i} style={{ position: 'absolute', left: x, top: y, width: 2 + r2 * 2.5, height: len, borderRadius: 3, transform: 'rotate(24deg)', background: 'linear-gradient(180deg, transparent, #ff9a3c 55%, #fff1c7)', boxShadow: '0 0 12px rgba(255,140,50,0.85)', opacity: on * (0.5 + r2 * 0.5) }} />);
    } else if (a.type === 'embers') {
      const ph = (t * (0.1 + r1 * 0.16) + r2) % 1, x = r3 * 1920 + Math.sin(t * 1.6 + i) * 22, y = 1120 - ph * 900, s = 2 + r1 * 5;
      items.push(<div key={i} style={{ position: 'absolute', left: x, top: y, width: s, height: s, borderRadius: '50%', background: '#ffb35c', boxShadow: '0 0 10px #ff7a26', opacity: on * Math.sin(ph * Math.PI) }} />);
    } else if (a.type === 'ash') {
      const ph = (t * (0.05 + r1 * 0.07) + r2) % 1, x = r3 * 1920 + Math.sin(t * 0.8 + i) * 40, y = ph * 1180 - 50, s = 2 + r1 * 6;
      items.push(<div key={i} style={{ position: 'absolute', left: x, top: y, width: s, height: s, borderRadius: '50%', background: a.color || 'rgba(205,200,190,0.8)', filter: `blur(${r2 * 1.5}px)`, opacity: on * Math.sin(ph * Math.PI) }} />);
    }
  }
  return <AbsoluteFill style={{ pointerEvents: 'none' }}>{items}</AbsoluteFill>;
};

export const Stage: React.FC<SceneProps> = ({ dur, asset, props, lead = 0 }) => {
  const frame = useCurrentFrame();
  const f = frame - lead;
  const t = f / 30;
  const k = ease(clamp(frame / dur));
  const cam = props.cam || 'in';
  const [cx, cy] = props.focus || [960, 540];
  const zoom = cam === 'in' ? 0.06 * k : cam === 'out' ? 0.06 * (1 - k) : cam === 'up' || cam === 'down' ? 0.04 : 0.02;
  const pan = cam === 'left' ? 40 - 80 * k : cam === 'right' ? -40 + 80 * k : 0;
  const tilt = cam === 'up' ? -28 + 56 * k : cam === 'down' ? 28 - 56 * k : 0;
  const g = gradeAt(props.grade, t);
  const filter = `brightness(${g.b}) saturate(${g.s}) contrast(${g.c}) hue-rotate(${g.h}deg) sepia(${g.sepia})`;
  const [sr, sg, sb, sa] = g.sky;
  const layers: any[] = props.layers || [];
  return (
    <AbsoluteFill style={{ overflow: 'hidden', background: '#000' }}>
      <AbsoluteFill style={{ filter }}>
        <AbsoluteFill style={{ transformOrigin: `${cx}px ${cy}px`, transform: `scale(${1.02 + zoom}) translate(${pan}px,${tilt}px)` }}>
          {asset ? <Img src={staticFile(assetPath(asset))} style={{ position: 'absolute', width: 1920, height: 1080, objectFit: 'cover', filter: props.bg_filter }} /> : null}
          {asset && props.water ? <Water asset={asset} w={props.water} t={t} /> : null}
        </AbsoluteFill>
        {sa > 0 ? <AbsoluteFill style={{ mixBlendMode: 'hard-light', background: `linear-gradient(180deg, rgba(${sr},${sg},${sb},${sa}) 0%, rgba(${sr},${sg},${sb},${sa * 0.75}) 45%, rgba(${sr},${sg},${sb},${sa * 0.3}) 75%, rgba(${sr},${sg},${sb},0) 100%)` }} /> : null}
        {layers.map((l, i) => {
          if (l.to_s != null && t > l.to_s) return null;
          const d = l.depth ?? 0.6;
          const s = 1 + zoom * (1 + 2 * d);
          const x = (pathAt(l.path, 'x', l.x ?? 960, t) - cx) * s + cx + pan * (1 + 1.5 * d);
          const y = (pathAt(l.path, 'y', l.y ?? 1000, t) - cy) * s + cy + tilt * (1 + 1.5 * d);
          const [o, sc, dy] = enterFx(f, (l.at_s || 0) * 30, l.enter || 'fade');
          const out = l.to_s != null ? 1 - ramp(t, l.to_s - 0.3, l.to_s) : 1;
          const hid = hideFx(l.hide, hiddenAmount(f, l.hide, l.unmask_s));
          const src = l.sprite ? spriteSrc(l.sprite, t, 30) : staticFile(assetPath(l.asset));
          const wind = l.wind ? ` rotate(${0.7 * Math.sin(t * 1.3 + i)}deg)` : '';
          const rim = l.rim ? ' drop-shadow(3px -1px 1.5px rgba(255,205,140,0.45))' : '';
          const fx = [hid.filter, l.tone, l.blur ? `blur(${l.blur}px)` : '', l.hide || l.blur ? '' : CUTOUT_SHADOW].filter(Boolean).join(' ') + rim;
          return (
            <React.Fragment key={i}>
              {l.shadow ? (
                <div style={{ position: 'absolute', left: x - (l.shadow.w * s) / 2, top: y - 26 * s, width: l.shadow.w * s, height: 46 * s, borderRadius: '50%', background: 'radial-gradient(closest-side, rgba(12,8,4,0.62), transparent)', opacity: o * out * (l.shadow.o ?? 1) }} />
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
      {(props.atmosphere || []).map((a: any, i: number) => <Atmosphere key={i} a={a} t={t} />)}
      {props.label ? <Label text={props.label} sub={props.sub} from={8} to={dur - 10} /> : null}
    </AbsoluteFill>
  );
};
