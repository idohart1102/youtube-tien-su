import React from 'react';
import { AbsoluteFill, Img, staticFile, useCurrentFrame } from 'remotion';
import { clamp, ease } from '../lib/lib';
import { assetPath } from '../types';
import { SceneProps, Label, useTheme, fontOf } from './common';

// Ảnh thật (hóa thạch, lớp đất, hang): giữ màu gốc, khung mảnh màu accent, dòng ghi nguồn góc dưới trái.
// Nền là chính ảnh đó làm mờ và tối đi. props: credit (bắt buộc), label, sub,
//   z (zoom cuối, mặc định 1.08: ảnh thật không được đứng yên), pan: [dx, dy] px trôi nhẹ trong cảnh,
//   region: [x, y, w, h] (0..1 theo ảnh): sơ đồ hoặc ảnh nhiều chi tiết thì phóng vào đúng vùng đang nói trong 1,2 giây đầu,
//   sweep (mặc định true khi cảnh ≥ 4 giây): một vệt sáng mảnh quét qua ảnh một lần.
//   fill: true: ảnh ngang phủ kín khung thay vì khung giữa nền mờ; dùng xen kẽ để không lặp bố cục.
export const PhotoCard: React.FC<SceneProps> = ({ dur, asset, props }) => {
  const f = useCurrentFrame();
  const t = useTheme();
  const k = ease(clamp(f / dur));
  const src = asset ? staticFile(assetPath(asset)) : undefined;
  const r = props.region as number[] | undefined;
  const rk = r ? ease(clamp(f / 36)) : 0;
  const rz = r ? Math.min(3, 1 / Math.max(r[2], r[3] * 1.4 / 1.75)) : 1; // khung 1400x800
  const z = (1 + ((props.z ?? 1.08) - 1) * k) * (1 + (rz - 1) * rk);
  const [px, py] = (props.pan as number[]) || [0, 0];
  // Đưa tâm vùng về giữa khung rồi phóng quanh tâm ảnh (translate % theo chính kích thước ảnh)
  const rx = r ? (0.5 - (r[0] + r[2] / 2)) * 100 * rk : 0, ry = r ? (0.5 - (r[1] + r[3] / 2)) * 100 * rk : 0;
  const sweepOn = props.sweep ?? dur >= 120;
  const sk = clamp((f - dur * 0.25) / 40);
  if (props.fill && src) {  // ảnh thật ngang, đủ nét: phủ kín khung (đổi kiểu trình bày, tránh lặp khung giữa nền mờ)
    return (
      <AbsoluteFill style={{ background: t.palette.bg, overflow: 'hidden' }}>
        <Img src={src} style={{ position: 'absolute', width: 1920, height: 1080, objectFit: 'cover', transform: `translate(${px * k}px,${py * k}px) scale(${z * 1.02})` }} />
        {sweepOn && sk > 0 && sk < 1 ? <AbsoluteFill style={{ pointerEvents: 'none', background: `linear-gradient(105deg, transparent ${sk * 140 - 30}%, rgba(255,245,225,0.12) ${sk * 140 - 20}%, transparent ${sk * 140 - 10}%)` }} /> : null}
        {props.label ? <Label text={props.label} sub={props.sub} from={8} to={dur - 10} /> : null}
        {props.credit ? <div style={{ position: 'absolute', left: 72, bottom: 24, fontFamily: fontOf(t), fontSize: 20, color: '#fff', opacity: 0.85, textShadow: '0 1px 6px rgba(0,0,0,0.9)' }}>{props.credit}</div> : null}
      </AbsoluteFill>
    );
  }
  return (
    <AbsoluteFill style={{ background: t.palette.bg }}>
      {src ? <Img src={src} style={{ position: 'absolute', width: 1920, height: 1080, objectFit: 'cover', filter: 'blur(28px) saturate(0.35) brightness(0.35)', transform: `scale(${1.1 + 0.04 * k}) translateX(${-20 * k}px)` }} /> : null}
      {src ? (
        <div style={{ position: 'absolute', left: 260, top: 110, width: 1400, height: 800, display: 'flex', alignItems: 'center', justifyContent: 'center', overflow: r ? 'hidden' : undefined, border: r ? `3px solid ${t.palette.accent}` : undefined }}>
          <Img src={src} style={{ maxWidth: '100%', maxHeight: '100%', objectFit: 'contain', border: r ? undefined : `3px solid ${t.palette.accent}`, boxShadow: '0 12px 40px rgba(0,0,0,0.6)', transform: `translate(${px * k}px,${py * k}px) scale(${z}) translate(${rx}%,${ry}%)` }} />
          {sweepOn && sk > 0 && sk < 1 ? <div style={{ position: 'absolute', inset: 0, pointerEvents: 'none', background: `linear-gradient(105deg, transparent ${sk * 140 - 30}%, rgba(255,245,225,0.16) ${sk * 140 - 20}%, transparent ${sk * 140 - 10}%)` }} /> : null}
        </div>
      ) : null}
      {props.label ? <Label text={props.label} sub={props.sub} from={8} to={dur - 10} /> : null}
      {props.credit ? (
        <div style={{ position: 'absolute', left: 72, bottom: 24, fontFamily: fontOf(t), fontSize: 20, color: t.palette.fg, opacity: 0.8 }}>{props.credit}</div>
      ) : null}
    </AbsoluteFill>
  );
};
