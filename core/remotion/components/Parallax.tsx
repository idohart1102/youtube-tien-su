import React from 'react';
import { AbsoluteFill, Img, staticFile, useCurrentFrame } from 'remotion';
import { clamp, ease } from '../lib/lib';
import { assetPath } from '../types';
import { SceneProps, Label, CUTOUT_SHADOW, enterFx, idleFx, hiddenAmount, hideFx } from './common';

// Cảnh 2.5D kiểu Vox: ảnh nền + các lớp cutout PNG trong suốt, lớp càng gần trôi càng nhanh.
// props: cam ("in" | "out" | "left" | "right" | "up" | "down" | "rack", mặc định "in"),
//   focus: [x, y] (px, điểm zoom tới khi cam in/out, mặc định giữa khung),
//   layers: [{asset, x, y (điểm giữa-đáy, px), h (chiều cao px), depth (0 xa .. 1 gần, mặc định 0.6),
//             at_s, enter ("pop" | "rise" | "fade"), flip, drift (px tự trôi ngang),
//             motion ("breathe" | "sway" | "bob" | "walk"), hide ("silhouette" | "fog" | "blur" | "keyhole"), unmask_s}],
//   label, sub
// up/down: lia dọc ±28 px (lộ dần con vật cao). rack: nền nhòe dần trong 40% đầu cảnh, cutout giữ nét.
export const Parallax: React.FC<SceneProps> = ({ dur, asset, props }) => {
  const f = useCurrentFrame();
  const k = ease(clamp(f / dur));
  const cam = props.cam || 'in';
  const [cx, cy] = props.focus || [960, 540];
  const zoom = cam === 'in' ? 0.06 * k : cam === 'out' ? 0.06 * (1 - k) : cam === 'up' || cam === 'down' ? 0.04 : 0.02;
  const pan = cam === 'left' ? 40 - 80 * k : cam === 'right' ? -40 + 80 * k : 0;
  const tilt = cam === 'up' ? -28 + 56 * k : cam === 'down' ? 28 - 56 * k : 0;
  const rack = cam === 'rack' ? `blur(${6 * ease(clamp(f / (dur * 0.4)))}px)` : '';
  const layers: any[] = props.layers || [];
  return (
    <AbsoluteFill style={{ overflow: 'hidden' }}>
      {asset ? (
        <Img
          src={staticFile(assetPath(asset))}
          style={{ position: 'absolute', width: 1920, height: 1080, objectFit: 'cover', transformOrigin: `${cx}px ${cy}px`, transform: `scale(${1.02 + zoom}) translate(${pan}px,${tilt}px)`, filter: [props.bg_filter, rack].filter(Boolean).join(' ') || undefined }}
        />
      ) : null}
      {layers.map((l, i) => {
        const d = l.depth ?? 0.6;
        const s = 1 + zoom * (1 + 2 * d);
        const x = ((l.x ?? 960) - cx) * s + cx + pan * (1 + 1.5 * d) + (l.drift || 0) * k;
        const y = ((l.y ?? 1000) - cy) * s + cy + tilt * (1 + 1.5 * d);
        const [o, sc, dy] = enterFx(f, (l.at_s || 0) * 30, l.enter);
        const hid = hideFx(l.hide, hiddenAmount(f, l.hide, l.unmask_s));
        return (
          <Img
            key={i}
            src={staticFile(assetPath(l.asset))}
            style={{ position: 'absolute', left: x, top: y + dy, height: (l.h || 600) * s, opacity: o * hid.opacity, transformOrigin: '50% 100%', transform: `translate(-50%,-100%) ${idleFx(f, l.motion, i)} scale(${sc}) scaleX(${l.flip ? -1 : 1})`, filter: `${hid.filter} ${CUTOUT_SHADOW}`, clipPath: hid.clipPath }}
          />
        );
      })}
      {props.label ? <Label text={props.label} sub={props.sub} from={8} to={dur - 10} /> : null}
    </AbsoluteFill>
  );
};
