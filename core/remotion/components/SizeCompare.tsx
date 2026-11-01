import React from 'react';
import { AbsoluteFill, Img, staticFile, useCurrentFrame, delayRender, continueRender } from 'remotion';
import { assetPath } from '../types';
import { ramp, INK } from '../lib/lib';
import { SceneProps, Svg, useTheme, fontOf, CUTOUT_SHADOW } from './common';
import { KenBurnsBg } from './KenBurns';
import { creature } from './registry';

// So sánh kích thước. props.items: [{name, size_m, label, cutout}], người dùng name 'human' (size_m = chiều cao, hình bóng người làm thước).
// cutout: ảnh PNG trong suốt của sinh vật/vật thể (nhìn ngang, sát mép), rộng ảnh = size_m. Không có cutout mới vẽ hình tạm.
// Các sinh vật khác: size_m là chiều dài thân. Tỉ lệ tự tính để vật lớn nhất vừa khung.
type Item = { name: string; size_m: number; label?: string; cutout?: string };
const GROUND = 780;

const Measured: React.FC<{ item: Item; pxPerM: number; x: number; f: number; delay: number }> = ({ item, pxPerM, x, f, delay }) => {
  const ref = React.useRef<SVGGElement>(null);
  const [box, setBox] = React.useState<DOMRect | null>(null);
  const [handle] = React.useState(() => delayRender('measure ' + item.name));
  React.useLayoutEffect(() => {
    if (ref.current) setBox(ref.current.getBBox() as DOMRect);
    else continueRender(handle);
  }, [handle]);
  React.useEffect(() => {
    if (box) continueRender(handle);
  }, [box, handle]);
  const isHuman = item.name === 'human';
  const natural = box ? (isHuman ? box.height : box.width) : 1;
  const s = (item.size_m * pxPerM) / natural;
  const grow = ramp(f, delay, delay + 20);
  const ox = box ? -box.x : 0, oy = box ? -(box.y + box.height) : 0; // canh trái-đáy
  return (
    <g transform={`translate(${x},${GROUND}) scale(${s * (0.6 + 0.4 * grow)})`} opacity={grow}>
      <g ref={ref} transform={`translate(${ox},${oy})`}>{creature(item.name, f)}</g>
    </g>
  );
};

export const SizeCompare: React.FC<SceneProps> = ({ dur, asset, props }) => {
  const f = useCurrentFrame();
  const t = useTheme();
  const items: Item[] = props.items || [{ name: 'human', size_m: 1.7 }, { name: 'trex', size_m: 12 }];
  const widthM = items.reduce((s, it) => s + (it.name === 'human' ? it.size_m * 0.4 : it.size_m), 0);
  const gaps = (items.length - 1) * 0.08;
  const pxPerM = Math.min(1500 / (widthM * (1 + gaps)), 600 / Math.max(...items.map((i) => (i.name === 'human' ? i.size_m : i.size_m * 0.45))));
  let cursor = 960 - (widthM * pxPerM * (1 + gaps)) / 2;
  const xs = items.map((it) => {
    const x = cursor;
    cursor += (it.name === 'human' ? it.size_m * 0.4 : it.size_m) * pxPerM * 1.08;
    return x;
  });
  const bar = ramp(f, 30, 60);
  const biggest = items.reduce((a, b) => (b.size_m > a.size_m ? b : a));
  return (
    <AbsoluteFill>
      <KenBurnsBg asset={asset} dur={dur} p={{ z0: 1.0, z1: 1.04, filter: 'brightness(0.75)', ...props.bg }} />
      <Svg>
        <rect x={0} y={GROUND} width={1920} height={1080 - GROUND} fill={INK} opacity={0.35} />
        <line x1={0} y1={GROUND} x2={1920} y2={GROUND} stroke={INK} strokeWidth={4} />
        {items.map((it, i) => (it.cutout ? null : <Measured key={i} item={it} pxPerM={pxPerM} x={xs[i]} f={f} delay={8 + i * 10} />))}
        {/* thước đo */}
        <g opacity={bar}>
          <line x1={xs[items.indexOf(biggest)]} y1={GROUND + 50} x2={xs[items.indexOf(biggest)] + biggest.size_m * pxPerM * bar} y2={GROUND + 50} stroke={t.palette.accent} strokeWidth={6} />
          <text x={xs[items.indexOf(biggest)]} y={GROUND + 110} fill={t.palette.fg} fontFamily={fontOf(t)} fontSize={44} fontWeight={700}>
            {/\d/.test(biggest.label || '') ? biggest.label : `${biggest.label || ''} ${biggest.size_m >= 1000 ? `${(biggest.size_m / 1000).toLocaleString(t.lang === 'vi' ? 'de-DE' : 'en-US')} km` : `${biggest.size_m.toLocaleString(t.lang === 'vi' ? 'de-DE' : 'en-US')} m`}`}
          </text>
        </g>
      </Svg>
      {items.map((it, i) => {
        if (!it.cutout) return null;
        const g = ramp(f, 8 + i * 10, 28 + i * 10);
        return <Img key={i} src={staticFile(assetPath(it.cutout))} style={{ position: 'absolute', left: xs[i], bottom: 1080 - GROUND, width: it.size_m * pxPerM, opacity: g, transformOrigin: '0% 100%', transform: `scale(${0.6 + 0.4 * g})`, filter: CUTOUT_SHADOW }} />;
      })}
      {props.title ? (
        <div style={{ position: 'absolute', top: 80, width: '100%', textAlign: 'center', fontFamily: fontOf(t), fontSize: 64, fontWeight: 700, color: t.palette.fg, textShadow: '3px 3px 0 #1c140e' }}>{props.title}</div>
      ) : null}
    </AbsoluteFill>
  );
};
