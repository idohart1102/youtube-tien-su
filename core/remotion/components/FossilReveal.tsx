import React from 'react';
import { AbsoluteFill, Img, staticFile, useCurrentFrame } from 'remotion';
import { clamp, ease } from '../lib/lib';
import { assetPath } from '../types';
import { SceneProps, Label, useTheme, fontOf } from './common';

// Từ hóa thạch thành sinh vật: ảnh thật, đường viền quét từ trái sang phải, rồi con vật hiện dần theo đường quét.
// props: sprite {base, clip, n}, photo {left, top, w}, x, y (giữa-đáy), h, flip, reveal_at (giây, mặc định 1,4),
//   sweep_s (mặc định 1,1), credit (bắt buộc), label, sub
const sweep = (k: number) => {
  const p = -12 + 124 * k;
  return `linear-gradient(90deg, #000 ${p - 12}%, transparent ${p}%)`;
};

export const FossilReveal: React.FC<SceneProps> = ({ dur, asset, props, lead = 0 }) => {
  const frame = useCurrentFrame();
  const t = useTheme();
  const f = frame - lead;
  const sec = f / 30;
  const at = props.reveal_at ?? 1.4;
  const len = props.sweep_s ?? 1.1;
  const line = ease(clamp((sec - at) / len));
  const body = ease(clamp((sec - at - 0.45) / len));
  const fadeLine = 1 - clamp((sec - at - len - 0.35) / 0.4);
  const ph = props.photo || { left: 110, top: -20, w: 1700 };
  const sp = props.sprite;
  const idx = String(Math.max(0, frame) % sp.n).padStart(3, '0');
  const box: React.CSSProperties = { position: 'absolute', left: props.x, top: props.y, height: props.h, transformOrigin: '50% 100%', transform: `translate(-50%,-100%) scaleX(${props.flip ? -1 : 1})` };
  return (
    <AbsoluteFill style={{ background: '#0d0a07', overflow: 'hidden' }}>
      {asset ? (
        <Img src={staticFile(assetPath(asset))} style={{ position: 'absolute', left: ph.left, top: ph.top, width: ph.w, filter: `brightness(${0.95 - 0.5 * body}) saturate(${1 - 0.6 * body})`, transformOrigin: '60% 40%', transform: `scale(${1 + 0.03 * clamp(frame / dur)})` }} />
      ) : null}
      <AbsoluteFill style={{ background: 'radial-gradient(ellipse 72% 72% at 58% 42%, transparent 55%, rgba(10,8,6,0.96) 100%)' }} />
      {body > 0 ? <Img src={staticFile(assetPath(`${sp.base}/${sp.clip}/${idx}.webp`))} style={{ ...box, WebkitMaskImage: sweep(body), maskImage: sweep(body) }} /> : null}
      {line > 0 && fadeLine > 0 ? <Img src={staticFile(assetPath(`${sp.base}/outline.webp`))} style={{ ...box, opacity: fadeLine, WebkitMaskImage: sweep(line), maskImage: sweep(line) }} /> : null}
      {props.label ? <Label text={props.label} sub={props.sub} from={lead + 8} to={dur - 10} /> : null}
      {props.credit ? <div style={{ position: 'absolute', left: 72, bottom: 24, fontFamily: fontOf(t), fontSize: 20, color: t.palette.fg, opacity: 0.8 }}>{props.credit}</div> : null}
    </AbsoluteFill>
  );
};
