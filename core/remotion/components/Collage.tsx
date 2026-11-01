import React from 'react';
import { AbsoluteFill, Img, staticFile, useCurrentFrame } from 'remotion';
import { clamp, ramp } from '../lib/lib';
import { assetPath } from '../types';
import { SceneProps, Label, CUTOUT_SHADOW, enterFx, useTheme, fontOf, hiddenAmount, hideFx } from './common';

// Cắt dán kiểu Vox, tối đa 3 mảnh. Nền: asset (làm tối) hoặc màu nền kênh.
// props: items: [{asset, x, y (tâm, px), w (rộng px), rot (độ), at_s, photo (true = ảnh thật: khung mảnh accent + credit), credit,
//                 reveal ("wipe": lộ dần từ trái sang phải trong 0,8 giây, hợp với "trước và sau"),
//                 hide ("fog" | "blur" | "keyhole" | "silhouette" cho cutout), unmask_s}], label, sub
export const Collage: React.FC<SceneProps> = ({ dur, asset, props }) => {
  const f = useCurrentFrame();
  const t = useTheme();
  const k = clamp(f / dur);
  const items: any[] = (props.items || []).slice(0, 3);
  return (
    <AbsoluteFill style={{ background: t.palette.bg, overflow: 'hidden' }}>
      {asset ? <Img src={staticFile(assetPath(asset))} style={{ position: 'absolute', width: 1920, height: 1080, objectFit: 'cover', filter: 'brightness(0.45) blur(2px)', transform: `scale(${1.04 + 0.03 * k})` }} /> : null}
      <AbsoluteFill style={{ transform: `scale(${1 + 0.04 * k})` }}>
        {items.map((it, i) => {
          const at = (it.at_s ?? i * 0.6) * 30;
          const wipe = it.reveal === 'wipe';
          const [o, sc, dy] = wipe ? [1, 1, 0] : enterFx(f, at, it.enter);
          const rot = (it.rot ?? [-4, 3, -2][i]) * (wipe ? 1 : 0.6 + 0.4 * o);
          const p = -10 + 120 * ramp(f, at, at + 24);
          const mask = wipe ? `linear-gradient(90deg, #000 ${p - 10}%, transparent ${p}%)` : undefined;
          const hid = hideFx(it.hide, hiddenAmount(f, it.hide, it.unmask_s));
          return (
            <div key={i} style={{ position: 'absolute', left: it.x ?? 960, top: (it.y ?? 540) + dy, width: it.w || 700, opacity: o * hid.opacity, transform: `translate(-50%,-50%) rotate(${rot}deg) scale(${sc})`, maskImage: mask, WebkitMaskImage: mask }}>
              <Img
                src={staticFile(assetPath(it.asset))}
                style={it.photo
                  ? { width: '100%', display: 'block', border: `3px solid ${t.palette.accent}`, boxShadow: '0 16px 36px rgba(0,0,0,0.55)', filter: hid.filter || undefined, clipPath: hid.clipPath }
                  : { width: '100%', display: 'block', filter: `${hid.filter} ${CUTOUT_SHADOW}`, clipPath: hid.clipPath }}
              />
              {it.photo && it.credit ? <div style={{ marginTop: 8, fontFamily: fontOf(t), fontSize: 18, color: t.palette.fg, opacity: 0.8 }}>{it.credit}</div> : null}
            </div>
          );
        })}
      </AbsoluteFill>
      {props.label ? <Label text={props.label} sub={props.sub} from={8} to={dur - 10} /> : null}
    </AbsoluteFill>
  );
};
