import React from 'react';
import { AbsoluteFill, Img, staticFile, useCurrentFrame } from 'remotion';
import { clamp } from '../lib/lib';
import { assetPath } from '../types';
import { SceneProps, Label, useTheme, fontOf } from './common';

// Ảnh thật (hóa thạch, lớp đất, hang): giữ màu gốc, khung mảnh màu accent, dòng ghi nguồn góc dưới trái.
// Nền là chính ảnh đó làm mờ và tối đi. props: credit (bắt buộc), label, sub, z (zoom cuối, mặc định 1.03)
export const PhotoCard: React.FC<SceneProps> = ({ dur, asset, props }) => {
  const f = useCurrentFrame();
  const t = useTheme();
  const k = clamp(f / dur);
  const src = asset ? staticFile(assetPath(asset)) : undefined;
  return (
    <AbsoluteFill style={{ background: t.palette.bg }}>
      {src ? <Img src={src} style={{ position: 'absolute', width: 1920, height: 1080, objectFit: 'cover', filter: 'blur(28px) brightness(0.35)', transform: 'scale(1.1)' }} /> : null}
      {src ? (
        <div style={{ position: 'absolute', left: 260, top: 110, width: 1400, height: 800, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <Img src={src} style={{ maxWidth: '100%', maxHeight: '100%', objectFit: 'contain', border: `3px solid ${t.palette.accent}`, boxShadow: '0 12px 40px rgba(0,0,0,0.6)', transform: `scale(${1 + ((props.z ?? 1.03) - 1) * k})` }} />
        </div>
      ) : null}
      {props.label ? <Label text={props.label} sub={props.sub} from={8} to={dur - 10} /> : null}
      {props.credit ? (
        <div style={{ position: 'absolute', left: 72, bottom: 24, fontFamily: fontOf(t), fontSize: 20, color: t.palette.fg, opacity: 0.8 }}>{props.credit}</div>
      ) : null}
    </AbsoluteFill>
  );
};
