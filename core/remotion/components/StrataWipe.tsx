import React from 'react';
import { AbsoluteFill, Img, random, staticFile, useCurrentFrame } from 'remotion';
import { clamp } from '../lib/lib';
import { assetPath } from '../types';
import { agoText, fontOf, tr, useTheme } from './common';

// Xuyên lớp đất: dấu ấn chuyển thời đại. Đá đi qua khung hình, che cảnh cũ rồi mở ra cảnh mới.
// strata_in: {dir ("up": đi lên về hiện tại, "down": chìm xuống về quá khứ), dur_s (mặc định 1,6), asset (kết cấu đá),
//             from_asset, from_filter, counter: {from_ma, end}}
const H = 1080;
const SEGS = 3;

const edge = (seed: string, top: boolean) => {
  const pts: string[] = [];
  const n = 36;
  const total = H * SEGS + 240;
  for (let i = 0; i <= n; i++) {
    const v = random(`${seed}-${i}`) * 90;
    pts.push(`${(i / n) * 100}% ${top ? v : total - v}px`);
  }
  return pts;
};

export const StrataWipe: React.FC<{ s: any; fps: number; lead: number }> = ({ s, fps, lead }) => {
  const f = useCurrentFrame() - lead;
  const t = useTheme();
  const len = (s.dur_s ?? 1.6) * fps;
  const k = clamp(f / len);
  if (f >= len) return null;
  const e = k * k * (3 - 2 * k);
  const total = H * SEGS + 240;
  const y = s.dir === 'down' ? H - (H + total) * e : -total + (H + total) * e;
  const top = edge('t', true);
  const bottom = edge('b', false).reverse();
  const clipPath = `polygon(${[...top, ...bottom].join(',')})`;
  const covered = s.dir === 'down' ? y + total > H && y < 0 : y < 0 && y + total > H;
  const passed = s.dir === 'down' ? y < 0 : y + total > H;
  const c = s.counter;
  const ma = c ? c.from_ma * (1 - clamp((k - 0.12) / 0.7)) : 0;
  const label = c ? (ma >= 1 ? agoText(t, ma) : c.end || tr(t, 'today')) : '';
  const op = c ? clamp((k - 0.08) / 0.08) * (1 - clamp((k - 0.86) / 0.08)) : 0;
  const texture = staticFile(assetPath(s.asset || 'shared/textures/tang-da.jpg'));
  return (
    <AbsoluteFill style={{ overflow: 'hidden' }}>
      {s.from_asset && !passed && !covered ? (
        <Img src={staticFile(assetPath(s.from_asset))} style={{ position: 'absolute', width: 1920, height: 1080, objectFit: 'cover', filter: s.from_filter }} />
      ) : null}
      <div style={{ position: 'absolute', left: 0, top: y, width: 1920, height: total, clipPath }}>
        {Array.from({ length: SEGS + 1 }).map((_, i) => (
          <Img key={i} src={texture} style={{ position: 'absolute', left: 0, top: i * H - 60, width: 1920, height: H, objectFit: 'cover', filter: 'brightness(0.72) contrast(1.08)', transform: i % 2 ? 'scaleY(-1)' : undefined }} />
        ))}
      </div>
      {label ? (
        <div style={{ position: 'absolute', top: 440, left: 0, right: 0, textAlign: 'center', opacity: op }}>
          <span style={{ fontFamily: fontOf(t), fontSize: 92, fontWeight: 800, color: t.palette.fg, background: 'rgba(16,10,6,0.62)', padding: '14px 42px', borderRadius: 8, fontVariantNumeric: 'tabular-nums' }}>{label}</span>
        </div>
      ) : null}
    </AbsoluteFill>
  );
};
