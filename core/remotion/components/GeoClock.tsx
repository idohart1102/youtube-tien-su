import React from 'react';
import { AbsoluteFill, useCurrentFrame } from 'remotion';
import { ramp, INK } from '../lib/lib';
import { SceneProps, Svg, useTheme, fontOf, agoText, tr } from './common';
import { KenBurnsBg } from './KenBurns';

// "Đồng hồ địa cầu": 46 億年 = 24 giờ. props: from_ma, to_ma, label, sub
const AGE = 4600;
const toHours = (ma: number) => ((AGE - ma) / AGE) * 24;

export const GeoClock: React.FC<SceneProps> = ({ dur, asset, props }) => {
  const f = useCurrentFrame();
  const t = useTheme();
  const { from_ma = 4600, to_ma = 66, label, sub } = props;
  const k = ramp(f, 10, Math.max(20, dur * 0.6));
  const ma = from_ma + (to_ma - from_ma) * k;
  const h = toHours(ma);
  const hh = Math.floor(h), mm = Math.floor((h - hh) * 60), ss = Math.floor(((h - hh) * 60 - mm) * 60);
  return (
    <AbsoluteFill style={{ background: t.palette.bg }}>
      <KenBurnsBg asset={asset} dur={dur} p={{ z0: 1.0, z1: 1.05, filter: 'brightness(0.55)', ...props.bg }} />
      <Svg>
        <g transform="translate(620,540) scale(2.6)">
          <circle r={120} fill="#efe2c4" stroke={INK} strokeWidth={6} />
          <circle r={108} fill="none" stroke={INK} strokeWidth={1.5} />
          {Array.from({ length: 24 }).map((_, i) => {
            const a = (i / 24) * Math.PI * 2 - Math.PI / 2;
            return <path key={i} d={`M${Math.cos(a) * 92},${Math.sin(a) * 92}L${Math.cos(a) * 104},${Math.sin(a) * 104}`} stroke={INK} strokeWidth={i % 6 ? 2 : 5} />;
          })}
          <path d="M0,0 L0,-62" stroke={INK} strokeWidth={8} strokeLinecap="round" transform={`rotate(${(h / 24) * 360})`} />
          <path d="M0,0 L0,-90" stroke={t.palette.danger || '#7a2a1a'} strokeWidth={4} strokeLinecap="round" transform={`rotate(${((h * 60) % 60) * 6})`} />
          <circle r={8} fill={INK} />
        </g>
      </Svg>
      <div style={{ position: 'absolute', left: 1040, top: 330, fontFamily: fontOf(t), color: t.palette.fg, textShadow: '3px 3px 0 #1c140e' }}>
        <div style={{ fontSize: 34, letterSpacing: 6, color: t.palette.accent }}>{tr(t, 'clock')}</div>
        <div style={{ fontSize: 120, fontWeight: 700, marginTop: 10 }}>{`${String(hh).padStart(2, '0')}:${String(mm).padStart(2, '0')}:${String(ss).padStart(2, '0')}`}</div>
        <div style={{ fontSize: 60, fontWeight: 700, marginTop: 10 }}>{agoText(t, Math.max(0, ma))}</div>
        {label ? <div style={{ fontSize: 46, marginTop: 30 }}>{label}</div> : null}
        {sub ? <div style={{ fontSize: 30, marginTop: 8, opacity: 0.85 }}>{sub}</div> : null}
      </div>
    </AbsoluteFill>
  );
};
