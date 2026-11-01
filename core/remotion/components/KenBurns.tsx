import React from 'react';
import { AbsoluteFill, Img, staticFile, useCurrentFrame } from 'remotion';
import { clamp } from '../lib/lib';
import { assetPath } from '../types';
import { SceneProps, Label, useTheme } from './common';

// Ảnh nền zoom/pan chậm. props: z0,z1,x0,x1,y0,y1,filter,label,sub,
// focus: [x, y] (px) = điểm zoom tới, dùng để đẩy máy vào đúng chi tiết đang annotate
export const KenBurnsBg: React.FC<{ asset?: string; dur: number; p?: Record<string, any> }> = ({ asset, dur, p = {} }) => {
  const f = useCurrentFrame();
  const t = useTheme();
  const k = clamp(f / dur);
  const { z0 = 1.05, z1 = 1.15, x0 = 0, x1 = 0, y0 = 0, y1 = 0, filter, focus } = p;
  if (!asset) return <AbsoluteFill style={{ background: t.palette.bg }} />;
  return (
    <Img
      src={staticFile(assetPath(asset))}
      style={{ position: 'absolute', width: 1920, height: 1080, objectFit: 'cover', transformOrigin: focus ? `${focus[0]}px ${focus[1]}px` : undefined, transform: `scale(${z0 + (z1 - z0) * k}) translate(${x0 + (x1 - x0) * k}px,${y0 + (y1 - y0) * k}px)`, filter }}
    />
  );
};

export const KenBurns: React.FC<SceneProps> = ({ dur, asset, props }) => (
  <AbsoluteFill>
    <KenBurnsBg asset={asset} dur={dur} p={props} />
    {props.label ? <Label text={props.label} sub={props.sub} from={8} to={dur - 10} /> : null}
  </AbsoluteFill>
);
