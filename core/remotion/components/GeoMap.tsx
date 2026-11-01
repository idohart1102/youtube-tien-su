import React from 'react';
import { AbsoluteFill, useCurrentFrame } from 'remotion';
import { geoMercator, geoPath, geoGraticule10 } from 'd3-geo';
import { feature } from 'topojson-client';
import world from 'world-atlas/countries-50m.json';
import { clamp, ease, ramp } from '../lib/lib';
import { SceneProps, Svg, useTheme, fontOf, tr } from './common';

// Bản đồ hiện đại dựng từ dữ liệu Natural Earth (không dùng ảnh AI). Luôn vẽ quần đảo Hoàng Sa, Trường Sa và nhãn Biển Đông khi nằm trong khung.
// Bản đồ thế giới (scale < 900) chỉ vẽ chấm đảo, không nhãn.
// props: center [lon, lat] (mặc định [108, 14]), scale (mặc định 2200), cam ("in" | "out"),
//   highlight: mã số ISO quốc gia (mặc định ["704"] = Việt Nam),
//   markers: [{lon, lat, label, at_s}], arrows: [{from: [lon, lat], to: [lon, lat], at_s}] (tối đa 3 marker, 2 mũi tên)
const LAND = feature(world as any, (world as any).objects.countries) as any;
const ISLANDS: { key: string; lon: number; lat: number; dots: [number, number][] }[] = [
  { key: 'hoangsa', lon: 112.0, lat: 16.5, dots: [[111.6, 16.5], [112.3, 16.8], [111.8, 16.2], [112.6, 16.3], [111.2, 15.8], [112.0, 16.9]] },
  { key: 'truongsa', lon: 114.3, lat: 10.0, dots: [[114.3, 10.4], [115.0, 9.6], [113.8, 9.2], [114.8, 10.8], [113.2, 8.6], [115.6, 10.2], [114.1, 8.0]] },
];

export const GeoMap: React.FC<SceneProps> = ({ dur, props }) => {
  const f = useCurrentFrame();
  const t = useTheme();
  const k = ease(clamp(f / dur));
  const zoom = props.cam === 'out' ? 1.08 - 0.08 * k : 1 + 0.08 * k;
  const proj = React.useMemo(
    () => geoMercator().center(props.center || [108, 14]).scale(props.scale || 2200).translate([960, 540]).clipExtent([[-300, -300], [2220, 1380]]),
    [props.center, props.scale],
  );
  const path = React.useMemo(() => geoPath(proj), [proj]);
  const hi: string[] = props.highlight || ['704'];
  const land = React.useMemo(() => LAND.features.map((c: any) => ({ id: String(c.id), d: path(c) || '' })).filter((c: any) => c.d), [path]);
  const grat = React.useMemo(() => path(geoGraticule10()) || '', [path]);
  const P = (lon: number, lat: number) => proj([lon, lat]) as [number, number];
  const inView = ([x, y]: [number, number]) => x > 40 && x < 1880 && y > 40 && y < 1040;
  const ink = '#2a2119';
  const label = (txt: string, x: number, y: number, size: number, o = 1, italic = false) => (
    <text x={x} y={y} fill={t.palette.fg} opacity={o} fontFamily={fontOf(t)} fontSize={size} fontWeight={600} fontStyle={italic ? 'italic' : undefined} textAnchor="middle" style={{ paintOrder: 'stroke', stroke: ink, strokeWidth: 6 }}>{txt}</text>
  );
  const sea = P(113.0, 13.6);
  const near = (props.scale || 2200) >= 900; // bản đồ thế giới: chỉ chấm đảo, không nhãn để khỏi chồng chữ
  return (
    <AbsoluteFill style={{ background: '#121820' }}>
      <Svg style={{ transform: `scale(${zoom})` }}>
        <path d={grat} fill="none" stroke={t.palette.fg} strokeOpacity={0.06} strokeWidth={1.5} />
        {land.map((c: any) => (
          <path key={c.id + c.d.length} d={c.d} fill={hi.includes(c.id) ? t.palette.accent : '#3b3128'} fillOpacity={hi.includes(c.id) ? 0.9 : 1} stroke={ink} strokeWidth={1.5} />
        ))}
        {ISLANDS.map((is) => {
          const c = P(is.lon, is.lat);
          if (!inView(c)) return null;
          return (
            <g key={is.key}>
              {is.dots.map(([lon, lat], i) => {
                const [x, y] = P(lon, lat);
                return <circle key={i} cx={x} cy={y} r={4} fill={hi.includes('704') ? t.palette.accent : t.palette.fg} />;
              })}
              {near ? label(tr(t, is.key), c[0], c[1] - 40, 26, 0.95) : null}
            </g>
          );
        })}
        {near && inView(sea) ? label(tr(t, 'biendong'), sea[0], sea[1], 34, 0.55, true) : null}
        {(props.arrows || []).slice(0, 2).map((a: any, i: number) => {
          const [x0, y0] = P(a.from[0], a.from[1]), [x1, y1] = P(a.to[0], a.to[1]);
          const g = ramp(f, (a.at_s || 0) * 30, (a.at_s || 0) * 30 + 24);
          const mx = (x0 + x1) / 2, my = Math.min(y0, y1) - Math.abs(x1 - x0) * 0.25;
          const col = t.palette.danger || t.palette.accent;
          const ang = Math.atan2(y1 - my, x1 - mx);
          const hp = (da: number) => `${x1 - 30 * Math.cos(ang + da)},${y1 - 30 * Math.sin(ang + da)}`;
          return (
            <g key={i}>
              <path d={`M${x0},${y0} Q${mx},${my} ${x1},${y1}`} pathLength={1} strokeDasharray={1} strokeDashoffset={1 - g} fill="none" stroke={col} strokeWidth={8} strokeLinecap="round" />
              {g > 0.95 ? <path d={`M${hp(0.5)} L${x1},${y1} L${hp(-0.5)}`} fill="none" stroke={col} strokeWidth={8} strokeLinecap="round" strokeLinejoin="round" /> : null}
            </g>
          );
        })}
        {(props.markers || []).slice(0, 3).map((m: any, i: number) => {
          const [x, y] = P(m.lon, m.lat);
          const g = ramp(f, (m.at_s ?? 0.5 + i * 0.5) * 30, (m.at_s ?? 0.5 + i * 0.5) * 30 + 12);
          return (
            <g key={i} opacity={g}>
              <circle cx={x} cy={y} r={12 + 30 * (1 - g)} fill="none" stroke="#FFD23F" strokeWidth={4} />
              <circle cx={x} cy={y} r={9} fill="#FFD23F" />
              {m.label ? label(m.label, x, y - 30, 32) : null}
            </g>
          );
        })}
      </Svg>
    </AbsoluteFill>
  );
};
