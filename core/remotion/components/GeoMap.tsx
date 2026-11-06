import React from 'react';
import { AbsoluteFill, useCurrentFrame } from 'remotion';
import { geoMercator, geoPath, geoGraticule10 } from 'd3-geo';
import { feature } from 'topojson-client';
import world from 'world-atlas/countries-50m.json';
import { clamp, ease, ramp } from '../lib/lib';
import { SceneProps, Svg, useTheme, fontOf, tr } from './common';
import PRESETS from '../lib/map_presets.json';

// Bản đồ hiện đại dựng từ dữ liệu Natural Earth (không dùng ảnh AI). Luôn vẽ quần đảo Hoàng Sa, Trường Sa và nhãn Biển Đông khi nằm trong khung.
// Bản đồ thế giới (scale < 800) chỉ vẽ chấm đảo, không nhãn; scale < 1500 bỏ nhãn Biển Đông, nhãn đảo dời sang phải chấm.
// props: preset ("vn" | "dna" | "asia", core/remotion/lib/map_presets.json, đã qua kiểm đảo) hoặc center [lon, lat] (mặc định [108, 14]), scale (mặc định 2200), cam ("in" | "out"),
//   highlight: mã số ISO quốc gia (mặc định ["704"] = Việt Nam),
//   markers: [{lon, lat, label, at_s}], arrows: [{from: [lon, lat], to: [lon, lat], at_s}] (tối đa 3 marker, 2 mũi tên)
// Chữ tối thiểu 34 px ở khung 1080 (đọc được trên điện thoại). Nhãn đảo đặt trước, nhãn marker né nhãn đảo, né nhau và né dải phụ đề (y > 864).
const SUB_Y = 840; // đường chân chữ cao nhất được phép, dưới đó là dải phụ đề
const MIN_FONT = 34;
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
  const pre = (PRESETS as any)[props.preset || ''] || {};
  const center = props.center || pre.center || [108, 14];
  const scale = props.scale || pre.scale || 2200;
  const proj = React.useMemo(
    () => geoMercator().center(center).scale(scale).translate([960, 540]).clipExtent([[-300, -300], [2220, 1380]]),
    [center[0], center[1], scale],
  );
  const path = React.useMemo(() => geoPath(proj), [proj]);
  const hi: string[] = props.highlight || ['704'];
  const land = React.useMemo(() => LAND.features.map((c: any) => ({ id: String(c.id), d: path(c) || '' })).filter((c: any) => c.d), [path]);
  const grat = React.useMemo(() => path(geoGraticule10()) || '', [path]);
  const P = (lon: number, lat: number) => proj([lon, lat]) as [number, number];
  const inView = ([x, y]: [number, number]) => x > 40 && x < 1880 && y > 40 && y < 1040;
  const ink = '#2a2119';
  const label = (txt: string, x: number, y: number, size: number, o = 1, italic = false) => (
    <text x={x} y={y} fill={t.palette.fg} opacity={o} fontFamily={fontOf(t)} fontSize={Math.max(MIN_FONT, size)} fontWeight={600} fontStyle={italic ? 'italic' : undefined} textAnchor="middle" style={{ paintOrder: 'stroke', stroke: ink, strokeWidth: 6 }}>{txt}</text>
  );
  const sea = P(113.0, 13.6);
  const near = scale >= 800; // bản đồ thế giới: chỉ chấm đảo, không nhãn để khỏi chồng chữ
  const mid = scale < 1500; // bản đồ khu vực: nhãn Trường Sa đặt dưới chấm, bỏ nhãn Biển Đông để khỏi chồng chữ
  const side = (k: string) => (k === 'truongsa' && mid) || scale < 1000; // nhãn đảo đặt bên phải chấm
  const textW = (s: string, size: number) => s.length * size * 0.56 + 20;
  // Vị trí nhãn đảo (đặt trước): bên phải hoặc trên chấm; chạm dải phụ đề thì đưa lên trên chấm
  // Vị trí nhãn đảo: thử bên phải chấm (nâng lên nếu chạm dải phụ đề), trên, dưới; né nhãn đảo khác và chấm marker
  const pins = (props.markers || []).slice(0, 3).map((m: any) => P(m.lon, m.lat));
  const placed: number[][] = [];
  const isl = ISLANDS.map((is) => {
    const c = P(is.lon, is.lat), w = textW(tr(t, is.key), MIN_FONT);
    const right = [c[0] + 30 + w / 2, Math.min(c[1] + 10, SUB_Y)];
    const cands = (side(is.key) ? [right, [c[0], c[1] - 44]] : [[c[0], c[1] - 44], right]).concat([[c[0] - 30 - w / 2, Math.min(c[1] + 10, SUB_Y)], [c[0], c[1] + 54]]);
    const free = (q: number[]) => q[1] <= SUB_Y && !placed.some((b) => Math.abs(b[0] - q[0]) < (b[2] + w) / 2 + 8 && Math.abs(b[1] - q[1]) < 46)
      && !pins.some(([px, py]) => Math.abs(px - q[0]) < w / 2 + 16 && py > q[1] - 40 && py < q[1] + 16);
    const [x, y] = cands.find(free) || cands[0];
    placed.push([x, y, w]);
    return { is, c, x, y, w };
  });
  const fixed: number[][] = isl.filter((a) => near && inView(a.c)).map((a) => [a.x, a.y, a.w]);
  // Chấm đảo cũng là vùng cấm của nhãn marker (khung bao các chấm + lề)
  for (const a of isl) {
    if (!inView(a.c)) continue;
    const pts = a.is.dots.map(([lo, la]) => P(lo, la));
    const xs = pts.map((q) => q[0]), ys = pts.map((q) => q[1]);
    fixed.push([(Math.min(...xs) + Math.max(...xs)) / 2, (Math.min(...ys) + Math.max(...ys)) / 2 + 12, Math.max(...xs) - Math.min(...xs) + 40]);
  }
  if (near && !mid && inView(sea)) fixed.push([sea[0], sea[1], textW(tr(t, 'biendong'), MIN_FONT)]);
  return (
    <AbsoluteFill style={{ background: '#121820' }}>
      <Svg style={{ transform: `scale(${zoom})` }}>
        <path d={grat} fill="none" stroke={t.palette.fg} strokeOpacity={0.06} strokeWidth={1.5} />
        {land.map((c: any) => (
          <path key={c.id + c.d.length} d={c.d} fill={hi.includes(c.id) ? t.palette.accent : '#3b3128'} fillOpacity={hi.includes(c.id) ? 0.9 : 1} stroke={ink} strokeWidth={1.5} />
        ))}
        {isl.map(({ is, c, x: lx, y: ly }) => {
          if (!inView(c)) return null;
          return (
            <g key={is.key}>
              {is.dots.map(([lon, lat], i) => {
                const [x, y] = P(lon, lat);
                return <circle key={i} cx={x} cy={y} r={4} fill={hi.includes('704') ? t.palette.accent : t.palette.fg} />;
              })}
              {near ? label(tr(t, is.key), lx, ly, MIN_FONT, 1) : null}
            </g>
          );
        })}
        {near && !mid && inView(sea) ? label(tr(t, 'biendong'), sea[0], sea[1], MIN_FONT, 0.55, true) : null}
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
        {(() => {
          // Nhãn marker tự né nhãn đảo, né nhau và né dải phụ đề: thử trên, dưới, phải, trái; lệch khỏi chỗ mặc định thì có đường dẫn mảnh tới điểm
          const ms = (props.markers || []).slice(0, 3);
          const boxes: number[][] = fixed.map((b) => [...b]);
          return ms.map((m: any) => {
            const [x, y] = P(m.lon, m.lat);
            const w = textW(m.label || '', 36), h = 48;
            const cands = [[x, y - 30, 0], [x - w / 2 - 30, y + 12, 1], [x, y + 62, 1], [x + w / 2 + 30, y + 12, 1], [x - w / 2 - 20, y - 40, 1], [x + w / 2 + 20, y - 40, 1], [x, y - 84, 1], [x, y + 116, 1]];
            const hit = (c: number[]) => boxes.some((b) => Math.abs(b[0] - c[0]) < (b[2] + w) / 2 + 8 && Math.abs(b[1] - c[1]) < h);
            const fits = (c: number[]) => c[1] <= SUB_Y && c[1] >= 60 && c[0] - w / 2 >= 40 && c[0] + w / 2 <= 1880;
            const c = cands.find((k) => fits(k) && !hit(k)) || cands.find(fits) || cands[0];
            boxes.push([c[0], c[1], w]);
            return [c[0], c[1], c[2]];
          });
        })().map((lp: number[], i: number) => {
          const m = (props.markers || [])[i];
          const [x, y] = P(m.lon, m.lat);
          const g = ramp(f, (m.at_s ?? 0.5 + i * 0.5) * 30, (m.at_s ?? 0.5 + i * 0.5) * 30 + 12);
          return (
            <g key={i} opacity={g}>
              <circle cx={x} cy={y} r={12 + 30 * (1 - g)} fill="none" stroke="#FFD23F" strokeWidth={4} />
              <circle cx={x} cy={y} r={9} fill="#FFD23F" />
              {m.label && lp[2] ? <line x1={x} y1={y} x2={lp[0]} y2={lp[1] - 12} stroke="#FFD23F" strokeWidth={2} opacity={0.8} /> : null}
              {m.label ? label(m.label, lp[0], lp[1], 36) : null}
            </g>
          );
        })}
      </Svg>
    </AbsoluteFill>
  );
};
