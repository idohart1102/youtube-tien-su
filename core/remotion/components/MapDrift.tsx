import React from 'react';
import { AbsoluteFill, useCurrentFrame } from 'remotion';
import { ramp } from '../lib/lib';
import { SceneProps, Svg, useTheme, fontOf, Label } from './common';
import { KenBurnsBg } from './KenBurns';

// Bản đồ với điểm đánh dấu và mũi tên. asset: ảnh bản đồ trong assets/maps/
// props.markers: [{x, y (0..1), label}], props.arrows: [{from:[x,y], to:[x,y]}], label, sub
export const MapDrift: React.FC<SceneProps> = ({ dur, asset, props }) => {
  const f = useCurrentFrame();
  const t = useTheme();
  const markers: { x: number; y: number; label?: string }[] = props.markers || [];
  const arrows: { from: [number, number]; to: [number, number] }[] = props.arrows || [];
  const step = Math.max(12, (dur * 0.6) / Math.max(1, markers.length + arrows.length));
  return (
    <AbsoluteFill style={{ background: t.palette.bg }}>
      <KenBurnsBg asset={asset} dur={dur} p={{ z0: 1.0, z1: 1.1, ...props.bg }} />
      <Svg>
        {arrows.map((a, i) => {
          const k = ramp(f, 10 + i * step, 10 + i * step + 30);
          const x1 = a.from[0] * 1920, y1 = a.from[1] * 1080;
          const x2 = x1 + (a.to[0] * 1920 - x1) * k, y2 = y1 + (a.to[1] * 1080 - y1) * k;
          return <line key={i} x1={x1} y1={y1} x2={x2} y2={y2} stroke={t.palette.accent} strokeWidth={8} strokeDasharray="22 14" strokeLinecap="round" />;
        })}
        {markers.map((m, i) => {
          const d = 10 + (arrows.length + i) * step;
          const k = ramp(f, d, d + 16);
          const pulse = 1 + 0.25 * Math.sin((f - d) / 6);
          return (
            <g key={i} transform={`translate(${m.x * 1920},${m.y * 1080})`} opacity={k}>
              <circle r={34 * pulse} fill={t.palette.danger || t.palette.accent} opacity={0.3} />
              <circle r={14} fill={t.palette.danger || t.palette.accent} stroke="#1c140e" strokeWidth={4} />
              {m.label ? <text x={26} y={-22} fill={t.palette.fg} fontFamily={fontOf(t)} fontSize={42} fontWeight={700} stroke="#1c140e" strokeWidth={6} paintOrder="stroke">{m.label}</text> : null}
            </g>
          );
        })}
      </Svg>
      {props.label ? <Label text={props.label} sub={props.sub} from={8} to={dur - 10} /> : null}
    </AbsoluteFill>
  );
};
