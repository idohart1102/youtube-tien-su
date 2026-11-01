import React from 'react';
import { useCurrentFrame } from 'remotion';
import { ramp } from '../lib/lib';
import { Svg, useTheme } from './common';

// Nét bút chú thích kiểu Vox, vẽ dần trong 0,6 giây, đặt được trên mọi cảnh qua props.annotate:
// [{type: "circle", x, y, w, h} | {type: "arrow", from: [x,y], to: [x,y]} | {type: "underline", x, y, w} | {type: "highlight", x, y, w, h}]
// mỗi mục có at_s (giây tính từ đầu cảnh), color (mặc định accent). Không chứa chữ: chữ dùng thẻ keyword.
type Item = { type: string; x?: number; y?: number; w?: number; h?: number; from?: [number, number]; to?: [number, number]; at_s?: number; color?: string };

const path = (it: Item) => {
  const { x = 960, y = 540, w = 300, h = 160 } = it;
  if (it.type === 'circle') {
    // vòng tay vẽ hơi lệch, đi quá điểm đầu một chút
    const rx = w / 2, ry = h / 2;
    const pts = Array.from({ length: 41 }, (_, i) => {
      const a = -2.2 + (i / 40) * (Math.PI * 2 + 0.5);
      const r = 1 + 0.05 * Math.sin(i * 0.9);
      return `${x + Math.cos(a) * rx * r},${y + Math.sin(a) * ry * r}`;
    });
    return `M${pts.join(' L')}`;
  }
  if (it.type === 'underline') return `M${x - w / 2},${y} Q${x},${y + 10} ${x + w / 2},${y - 4}`;
  if (it.type === 'arrow') {
    const [x0, y0] = it.from || [700, 400], [x1, y1] = it.to || [960, 540];
    const mx = (x0 + x1) / 2 - (y1 - y0) * 0.2, my = (y0 + y1) / 2 + (x1 - x0) * 0.2;
    return `M${x0},${y0} Q${mx},${my} ${x1},${y1}`;
  }
  return '';
};

export const Annotate: React.FC<{ items?: Item[]; fps: number }> = ({ items, fps }) => {
  const f = useCurrentFrame();
  const t = useTheme();
  if (!items?.length) return null;
  return (
    <Svg style={{ pointerEvents: 'none' }}>
      {items.map((it, i) => {
        const k = ramp(f, (it.at_s || 0) * fps, (it.at_s || 0) * fps + 18);
        if (k <= 0) return null;
        const c = it.color || t.palette.accent;
        if (it.type === 'highlight') {
          const { x = 960, y = 540, w = 300, h = 60 } = it;
          return <rect key={i} x={x - w / 2} y={y - h / 2} width={w * k} height={h} fill={c} opacity={0.35} />;
        }
        const d = path(it);
        let head = null;
        if (it.type === 'arrow' && k > 0.9) {
          const [x0, y0] = it.from || [700, 400], [x1, y1] = it.to || [960, 540];
          const mx = (x0 + x1) / 2 - (y1 - y0) * 0.2, my = (y0 + y1) / 2 + (x1 - x0) * 0.2;
          const a = Math.atan2(y1 - my, x1 - mx);
          const p = (da: number) => `${x1 - 34 * Math.cos(a + da)},${y1 - 34 * Math.sin(a + da)}`;
          head = <path d={`M${p(0.5)} L${x1},${y1} L${p(-0.5)}`} fill="none" stroke={c} strokeWidth={9} strokeLinecap="round" strokeLinejoin="round" />;
        }
        return (
          <g key={i} style={{ filter: 'drop-shadow(2px 3px 0 rgba(0,0,0,0.5))' }}>
            <path d={d} pathLength={1} fill="none" stroke={c} strokeWidth={9} strokeLinecap="round" strokeLinejoin="round" strokeDasharray={1} strokeDashoffset={1 - k} />
            {head}
          </g>
        );
      })}
    </Svg>
  );
};
