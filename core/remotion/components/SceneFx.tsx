import React from 'react';
import { AbsoluteFill, useCurrentFrame } from 'remotion';
import { ramp } from '../lib/lib';
import { shakeXY, hiddenAmount, hideFx } from './common';

// Hiệu ứng cấp cảnh, bọc quanh component (dưới annotate, thẻ, badge). Mọi at_s tính từ đầu cảnh.
//   props.shake: {at_s, dur_s (mặc định 0,8), amp (px, mặc định 14)}: rung máy khi va chạm, động đất.
//   props.spotlight: {x, y, r (mặc định 260), at_s, dim (mặc định 0,7)}: làm tối cả khung, chừa 1 vòng sáng.
//   props.hide: {mode: "blur" | "fog" | "keyhole", x, y, r, unmask_s}: ẩn ảnh nền cho câu hỏi, lộ ra ở câu trả lời.
const Ring: React.FC<{ x: number; y: number; r: number; dim: number }> = ({ x, y, r, dim }) => (
  <AbsoluteFill style={{ pointerEvents: 'none', background: `radial-gradient(circle at ${x}px ${y}px, transparent ${r * 0.8}px, rgba(8,6,4,${dim}) ${r}px)` }} />
);

export const SceneFx: React.FC<{ p: Record<string, any>; lead: number; fps: number; children: React.ReactNode }> = ({ p, lead, fps, children }) => {
  const f = useCurrentFrame() - lead;
  const [dx, dy] = p.shake ? shakeXY(f, (p.shake.at_s || 0) * fps, (p.shake.dur_s ?? 0.8) * fps, p.shake.amp ?? 14) : [0, 0];
  const sp = p.spotlight;
  const hd = p.hide;
  const h = hd ? hiddenAmount(f, hd.mode, hd.unmask_s) : 0;
  const hid = hd && hd.mode !== 'keyhole' ? hideFx(hd.mode, h) : { filter: '', opacity: 1 };
  return (
    <AbsoluteFill style={{ transform: dx || dy ? `translate(${dx}px,${dy}px) scale(1.02)` : undefined }}>
      <AbsoluteFill style={{ filter: hid.filter || undefined, opacity: hid.opacity }}>{children}</AbsoluteFill>
      {sp ? <Ring x={sp.x ?? 960} y={sp.y ?? 540} r={sp.r ?? 260} dim={(sp.dim ?? 0.7) * ramp(f, (sp.at_s || 0) * fps, (sp.at_s || 0) * fps + 18)} /> : null}
      {hd?.mode === 'keyhole' && h > 0 ? <Ring x={hd.x ?? 960} y={hd.y ?? 540} r={(hd.r ?? 200) + 1800 * (1 - h)} dim={0.92 * h} /> : null}
    </AbsoluteFill>
  );
};
