import React from 'react';
import { Inked, INK, hatch, smooth, P, rng, blobPts } from './lib';

const pts = (a: number[]): P[] => {
  const o: P[] = [];
  for (let i = 0; i < a.length; i += 2) o.push([a[i], a[i + 1]]);
  return o;
};

// fur strokes following an outline
const furStrokes = (outline: P[], seed: number, len = 10) => {
  const r = rng(seed);
  let d = '';
  for (let i = 0; i < outline.length; i++) {
    const a = outline[i], b = outline[(i + 1) % outline.length];
    for (let k = 0; k < 4; k++) {
      const t = r();
      const x = a[0] + (b[0] - a[0]) * t, y = a[1] + (b[1] - a[1]) * t;
      const nx = -(b[1] - a[1]), ny = b[0] - a[0];
      const nl = Math.hypot(nx, ny) || 1;
      const l = len * (0.5 + r());
      d += `M${x.toFixed(1)},${y.toFixed(1)}l${((-nx / nl) * l + (r() - 0.5) * 4).toFixed(1)},${((-ny / nl) * l + (r() - 0.5) * 4).toFixed(1)}`;
    }
  }
  return d;
};

// ---------- small mammal (Didelphodon-like), facing right ----------
const MAM = pts([-100, -30, -72, -62, -10, -78, 50, -70, 88, -56, 122, -50, 150, -36, 164, -28, 152, -20, 122, -15, 96, -10, 60, -4, 0, 0, -60, -2, -96, -12]);
export const Mammal: React.FC<{ t: number; fear?: number }> = ({ t, fear = 1 }) => {
  const jx = Math.sin(t * 47) * 1.6 * fear, jy = Math.cos(t * 53) * 1.2 * fear;
  const breathe = 1 + Math.sin(t * 9) * 0.025;
  const d = smooth(MAM);
  return (
    <g transform={`translate(${jx},${jy})`} filter="url(#rough)">
      <path d="M-92,-14 C-140,-10 -170,10 -210,4" stroke={INK} strokeWidth={9} fill="none" strokeLinecap="round" />
      <path d="M-92,-14 C-140,-10 -170,10 -210,4" stroke="#b49a86" strokeWidth={5} fill="none" strokeLinecap="round" />
      <path d="M-50,-4 l-8,16 l12,0 M30,-2 l2,16 l10,0 M100,-12 l6,14 l9,0" stroke={INK} strokeWidth={4} fill="none" strokeLinecap="round" />
      <g transform={`scale(1,${breathe})`}>
        <Inked
          d={d}
          fill="#7a6250"
          w={3.5}
          shade={
            <>
              <ellipse cx={-10} cy={-70} rx={90} ry={20} fill="#c8ad8f" opacity={0.5} filter="url(#soft6)" />
              <ellipse cx={20} cy={0} rx={120} ry={18} fill="#2a1d14" opacity={0.6} filter="url(#soft6)" />
              <path d={furStrokes(MAM, 3, 9)} stroke={INK} strokeWidth={1.3} opacity={0.6} />
              <path d={hatch(-80, -40, 60, 0, 20, 6, 4)} stroke={INK} strokeWidth={1} opacity={0.35} />
            </>
          }
        />
      </g>
      <Inked d={smooth(blobPts(84, -64, 13, 15, 8, 0.15, 2))} fill="#a07e6c" w={3} />
      <circle cx={122} cy={-40} r={8} fill="#0e0a08" stroke={INK} strokeWidth={2} />
      <circle cx={124.5} cy={-42.5} r={2.6} fill="#fff" />
      <circle cx={161} cy={-27} r={4} fill={INK} />
      <path d="M150,-24 l26,-8 M150,-22 l28,2 M148,-20 l22,10" stroke={INK} strokeWidth={1} opacity={0.7} />
    </g>
  );
};

// ---------- turtle, facing right ----------
const SHELL = pts([-92, 0, -84, -40, -44, -66, 16, -70, 66, -52, 94, -14, 90, 2, 0, 6]);
export const Turtle: React.FC<{ t: number }> = ({ t }) => {
  const head = Math.sin(t * 1.3) * 6;
  return (
    <g filter="url(#rough)">
      <Inked d="M-70,0 l-14,18 l20,0 Z M60,0 l12,18 l-20,0 Z" fill="#6a6a48" w={3} />
      <g transform={`translate(${head},0)`}>
        <Inked d={smooth(pts([80, -10, 110, -26, 140, -30, 158, -22, 152, -10, 120, -4, 88, 2]))} fill="#7c7a52" w={3} />
        <circle cx={142} cy={-22} r={3.2} fill={INK} />
      </g>
      <Inked
        d={smooth(SHELL)}
        fill="#5c5634"
        w={4}
        shade={
          <>
            <ellipse cx={-10} cy={-60} rx={60} ry={14} fill="#c9c08a" opacity={0.5} filter="url(#soft6)" />
            <path d="M-60,-30 L-30,-58 L20,-60 L55,-36 M-30,-58 L-20,-20 L30,-20 L20,-60 M-20,-20 L-60,-30 M30,-20 L55,-36 M-20,-20 L-40,0 M30,-20 L50,0" stroke={INK} strokeWidth={2.2} fill="none" />
            <path d={hatch(-90, -20, 90, 6, 20, 6, 3)} stroke={INK} strokeWidth={1} opacity={0.4} />
          </>
        }
      />
      <path d="M-92,0 C-40,8 40,8 90,2" stroke="#c9b98a" strokeWidth={6} fill="none" />
      <path d="M-92,0 C-40,8 40,8 90,2" stroke={INK} strokeWidth={2.5} fill="none" />
    </g>
  );
};

// ---------- toothed early bird, facing right; peck 0..1 ----------
export const Bird: React.FC<{ peck: number; hue?: string }> = ({ peck, hue = '#4f5a66' }) => {
  const body = pts([-60, -20, -30, -44, 10, -46, 40, -36, 52, -18, 30, 0, -20, 4, -50, -4]);
  return (
    <g filter="url(#rough)">
      <path d="M-4,0 L-10,46 L-24,52 M-10,46 L4,52 M14,0 L18,46 L6,52 M18,46 L32,52" stroke={INK} strokeWidth={3} fill="none" strokeLinecap="round" />
      <Inked d={smooth(pts([-56, -24, -100, -34, -116, -20, -96, -12, -56, -8]))} fill="#2e353c" w={3} />
      <g transform={`rotate(${peck * 70},40,-34)`}>
        <Inked d={smooth(pts([32, -40, 44, -70, 60, -86, 80, -84, 86, -70, 66, -62, 52, -36]))} fill={hue} w={3} />
        <Inked d="M82,-80 L122,-72 L84,-66 Z" fill="#c9a86a" w={2.5} />
        <path d="M92,-70 l2,4 l2,-4 M100,-70 l2,4 l2,-4 M108,-70 l2,3 l2,-3" stroke={INK} strokeWidth={1.2} fill="#fff" />
        <circle cx={72} cy={-78} r={3.4} fill={INK} />
        <circle cx={73} cy={-79} r={1} fill="#fff" />
      </g>
      <Inked
        d={smooth(body)}
        fill={hue}
        w={3.5}
        shade={
          <>
            <path d="M-50,-20 C-20,-40 20,-40 44,-26 C20,-14 -20,-6 -50,-10Z" fill="#232a31" opacity={0.7} />
            <path d="M-40,-22 L-10,-30 M-34,-16 L-4,-24 M-28,-10 L2,-18 M-22,-6 L10,-12" stroke="#c7d0d6" strokeWidth={1.4} opacity={0.6} />
            <ellipse cx={20} cy={-2} rx={40} ry={8} fill="#d8d0b8" opacity={0.6} filter="url(#soft6)" />
          </>
        }
      />
    </g>
  );
};

// ---------- silhouettes for distant herds ----------
export const SAUROPOD = smooth(pts([
  -380, 10, -300, -20, -200, -60, -120, -110, -40, -130, 40, -128, 100, -110, 150, -150, 190, -230, 225, -300, 250, -330, 285, -336, 300, -324, 280, -316,
  256, -296, 230, -230, 205, -150, 170, -70, 150, 0, 150, 120, 120, 120, 112, 30, 60, 20, 40, 120, 10, 120, 8, 20, -60, 20, -70, 120, -100, 120, -110, 10, -180, -10, -260, -4,
]));
export const TRICERATOPS = smooth(pts([
  -220, -40, -160, -90, -60, -120, 40, -116, 110, -100, 150, -150, 190, -190, 200, -170, 180, -120, 210, -90, 260, -110, 262, -96, 230, -70, 262, -60, 230, -40,
  200, -20, 150, 0, 140, 60, 115, 60, 108, 10, 30, 0, 20, 60, -5, 60, -10, 0, -80, 0, -90, 60, -115, 60, -120, -10, -170, -20,
]));
export const STEGOSAURUS = smooth(pts([
  -260, -10, -170, -50, -120, -110, -90, -100, -70, -150, -40, -130, -10, -170, 20, -140, 50, -160, 70, -120, 100, -120, 130, -80, 180, -50, 220, -40, 230, -26, 200, -16,
  150, -10, 130, 50, 105, 50, 100, 0, 0, 0, -10, 60, -35, 60, -40, -4, -130, -10, -200, -2,
]));

export const Silhouette: React.FC<{ d: string; fill?: string; rim?: string; flip?: boolean }> = ({ d, fill = '#2a1c22', rim = '#f2b06a', flip }) => (
  <g transform={flip ? 'scale(-1,1)' : undefined}>
    <path d={d} fill={fill} />
    <path d={d} fill="none" stroke={rim} strokeWidth={3} opacity={0.55} transform="translate(-2,-2)" />
    <path d={d} fill="none" stroke={INK} strokeWidth={3} />
  </g>
);

export const Pterosaur: React.FC<{ flap: number; fill?: string }> = ({ flap, fill = '#2a1c22' }) => {
  const k = Math.sin(flap);
  return (
    <g>
      <path d={`M0,0 C-40,${-20 - k * 30} -90,${-10 - k * 50} -140,${10 - k * 40} C-90,${0 - k * 10} -40,10 0,8 Z`} fill={fill} stroke={INK} strokeWidth={2} />
      <path d={`M0,0 C40,${-20 - k * 30} 90,${-10 - k * 50} 140,${10 - k * 40} C90,${0 - k * 10} 40,10 0,8 Z`} fill={fill} stroke={INK} strokeWidth={2} />
      <path d="M-14,4 L30,-4 L54,-14 L34,2 Z" fill={fill} stroke={INK} strokeWidth={2} />
    </g>
  );
};

// ---------- plants ----------
export const Fern: React.FC<{ size?: number; seed?: number; sway?: number; color?: string; dark?: string }> = ({ size = 1, seed = 1, sway = 0, color = '#5f7f3c', dark = '#2f4420' }) => {
  const r = rng(seed);
  const fronds = 7;
  const out: React.ReactNode[] = [];
  for (let i = 0; i < fronds; i++) {
    const a = -150 + (i / (fronds - 1)) * 120 + (r() - 0.5) * 12 + sway * (0.6 + r() * 0.5);
    const L = 160 * size * (0.7 + r() * 0.4);
    const rad = (a * Math.PI) / 180;
    const ex = Math.cos(rad) * L, ey = Math.sin(rad) * L;
    const bend = (a < -90 ? -1 : 1) * L * 0.25;
    const cx = ex * 0.5 + bend * 0.6, cy = ey * 0.5 - Math.abs(bend) * 0.2;
    let leaf = '';
    for (let k = 1; k < 12; k++) {
      const t = k / 12;
      const x = (1 - t) * (1 - t) * 0 + 2 * (1 - t) * t * cx + t * t * ex;
      const y = 2 * (1 - t) * t * cy + t * t * ey;
      const tx = 2 * (1 - t) * cx + 2 * t * (ex - cx), ty = 2 * (1 - t) * cy + 2 * t * (ey - cy);
      const tl = Math.hypot(tx, ty) || 1;
      const nx = -ty / tl, ny = tx / tl;
      const ll = 26 * size * (1 - t * 0.8);
      for (const s of [1, -1]) {
        const px = x + nx * ll * s + (tx / tl) * ll * 0.5, py = y + ny * ll * s + (ty / tl) * ll * 0.5;
        leaf += `M${x.toFixed(1)},${y.toFixed(1)}Q${((x + px) / 2 + nx * 5 * s).toFixed(1)},${((y + py) / 2 + ny * 5 * s).toFixed(1)} ${px.toFixed(1)},${py.toFixed(1)}`;
      }
    }
    out.push(
      <g key={i}>
        <path d={leaf} stroke={INK} strokeWidth={9 * size} strokeLinecap="round" fill="none" />
        <path d={leaf} stroke={i % 2 ? color : dark} strokeWidth={6 * size} strokeLinecap="round" fill="none" />
        <path d={`M0,0Q${cx},${cy} ${ex},${ey}`} stroke={INK} strokeWidth={2.5 * size} fill="none" />
      </g>,
    );
  }
  return <g>{out}</g>;
};

export const Conifer: React.FC<{ h?: number; seed?: number; color?: string; light?: string; sway?: number }> = ({ h = 600, seed = 1, color = '#2f4a32', light = '#6f8f5a', sway = 0 }) => {
  const r = rng(seed);
  const tiers = 7;
  const els: React.ReactNode[] = [];
  for (let i = 0; i < tiers; i++) {
    const y = -h * 0.35 - (i / tiers) * h * 0.62;
    const w = h * 0.22 * (1 - i / tiers) + 30;
    const sx = sway * (i / tiers), dr = 18 + r() * 14;
    const d = smooth([
      [sx - w, y + dr], [sx - w * 0.6, y - 4], [sx - w * 0.25, y - 26], [sx, y - 34], [sx + w * 0.25, y - 26],
      [sx + w * 0.6, y - 4], [sx + w, y + dr], [sx + w * 0.5, y + 10 + r() * 6], [sx, y + 16], [sx - w * 0.5, y + 10 + r() * 6],
    ] as P[]);
    els.push(
      <Inked
        key={i}
        d={d}
        fill={color}
        w={3}
        shade={
          <>
            <ellipse cx={-w * 0.3} cy={y - 16} rx={w * 0.6} ry={12} fill={light} opacity={0.7} filter="url(#soft6)" />
            <path d={hatch(-w, y, w, y + 30, 20, 6, seed + i)} stroke={INK} strokeWidth={1.2} opacity={0.4} />
          </>
        }
      />,
    );
  }
  return (
    <g>
      <Inked d={`M-14,0 L-6,${-h * 0.98} L6,${-h * 0.98} L14,0 Z`} fill="#4a3424" w={3} shade={<path d={hatch(-14, -h, 14, 0, 85, 7, seed)} stroke={INK} strokeWidth={1.2} opacity={0.5} />} />
      {els}
    </g>
  );
};

export const Cycad: React.FC<{ size?: number; seed?: number; sway?: number }> = ({ size = 1, seed = 2, sway = 0 }) => (
  <g>
    <Inked d={`M${-22 * size},0 L${-16 * size},${-90 * size} L${16 * size},${-90 * size} L${22 * size},0Z`} fill="#6a5034" w={3} shade={<path d={hatch(-30, -90 * size, 30, 0, 0, 10, seed)} stroke={INK} strokeWidth={1.5} opacity={0.5} />} />
    <g transform={`translate(0,${-90 * size})`}>
      <Fern size={size * 0.9} seed={seed} sway={sway} color="#6e8a3a" dark="#3b5222" />
    </g>
  </g>
);

export const Reeds: React.FC<{ n?: number; seed?: number; h?: number; sway?: number; w?: number }> = ({ n = 14, seed = 3, h = 160, sway = 0, w = 200 }) => {
  const r = rng(seed);
  let d = '';
  for (let i = 0; i < n; i++) {
    const x = (r() - 0.5) * w;
    const hh = h * (0.6 + r() * 0.5);
    const lean = (r() - 0.5) * 30 + sway * (0.5 + r());
    d += `M${x.toFixed(1)},0 Q${(x + lean * 0.3).toFixed(1)},${(-hh * 0.5).toFixed(1)} ${(x + lean).toFixed(1)},${(-hh).toFixed(1)}`;
  }
  return (
    <g>
      <path d={d} stroke={INK} strokeWidth={6} fill="none" strokeLinecap="round" />
      <path d={d} stroke="#7d8f4a" strokeWidth={3} fill="none" strokeLinecap="round" />
    </g>
  );
};

// ---------- space ----------
export const Asteroid: React.FC<{ r?: number; rot?: number; seed?: number }> = ({ r = 100, rot = 0, seed = 7 }) => {
  const d = smooth(blobPts(0, 0, r, r * 0.8, 14, 0.35, seed));
  const rr = rng(seed + 1);
  const craters = Array.from({ length: 7 }).map(() => [(rr() - 0.5) * r * 1.1, (rr() - 0.5) * r * 0.9, r * (0.08 + rr() * 0.14)]);
  return (
    <g transform={`rotate(${rot})`} filter="url(#rough)">
      <Inked
        d={d}
        fill="#6b5a4c"
        w={4}
        shade={
          <>
            <ellipse cx={-r * 0.35} cy={-r * 0.35} rx={r * 0.7} ry={r * 0.5} fill="#c7ad8e" opacity={0.6} filter="url(#soft)" />
            <ellipse cx={r * 0.5} cy={r * 0.45} rx={r * 0.9} ry={r * 0.6} fill="#1d1612" opacity={0.75} filter="url(#soft)" />
            {craters.map(([x, y, s], i) => (
              <g key={i}>
                <ellipse cx={x} cy={y} rx={s} ry={s * 0.8} fill="#3a2e26" opacity={0.6} />
                <path d={`M${x - s},${y} A${s},${s * 0.8} 0 0 1 ${x + s},${y}`} stroke={INK} strokeWidth={2} fill="none" />
                <path d={`M${x - s * 0.8},${y + s * 0.4} A${s},${s * 0.8} 0 0 0 ${x + s * 0.8},${y + s * 0.4}`} stroke="#d8c0a0" strokeWidth={1.5} fill="none" opacity={0.6} />
              </g>
            ))}
            <path d={hatch(0, 0, r * 1.2, r, 40, 7, seed)} stroke={INK} strokeWidth={1.3} opacity={0.45} />
          </>
        }
      />
    </g>
  );
};

export const Earth: React.FC<{ R?: number; spin?: number; dark?: number }> = ({ R = 380, spin = 0, dark = 0.55 }) => {
  const land = [
    blobPts(-120, -80, 150, 110, 12, 0.7, 31),
    blobPts(80, 60, 110, 160, 12, 0.6, 32),
    blobPts(220, -160, 120, 80, 10, 0.6, 33),
    blobPts(-260, 140, 90, 70, 10, 0.6, 34),
    blobPts(420, 40, 130, 120, 10, 0.6, 35),
    blobPts(-450, -40, 120, 140, 10, 0.6, 36),
  ];
  return (
    <g>
      <circle r={R * 1.08} fill="#7fc4ff" opacity={0.25} filter="url(#glow)" />
      <clipPath id="earthClip">
        <circle r={R} />
      </clipPath>
      <circle r={R} fill="#1f5f8a" />
      <g clipPath="url(#earthClip)">
        <g transform={`translate(${spin},0)`}>
          {land.map((p, i) => (
            <g key={i}>
              <path d={smooth(p)} fill={i % 2 ? '#7a8a4a' : '#9a8a52'} stroke={INK} strokeWidth={2.5} />
              <path d={smooth(p)} fill="none" stroke="#c9d49a" strokeWidth={1.5} opacity={0.5} transform="translate(-3,-3)" />
            </g>
          ))}
          {[0, 1, 2, 3, 4].map((i) => (
            <path key={i} d={`M${-500 + i * 200},${-250 + i * 110} c80,-30 160,20 260,-10`} stroke="#f4f4ec" strokeWidth={18} opacity={0.6} fill="none" strokeLinecap="round" filter="url(#soft6)" />
          ))}
        </g>
        <circle cx={-R * 0.35} cy={-R * 0.35} r={R * 0.7} fill="#cfe8ff" opacity={0.18} filter="url(#soft)" />
        <circle cx={R * 0.75} cy={R * 0.35} r={R * 1.1} fill="#05080f" opacity={dark} filter="url(#soft)" />
        <path d={hatch(0, 0, R * 2, R * 2, 35, 9, 5)} stroke={INK} strokeWidth={1.2} opacity={0.22} transform={`translate(${R * 0.6},${R * 0.4})`} />
      </g>
      <circle r={R} fill="none" stroke={INK} strokeWidth={5} />
      <circle r={R + 6} fill="none" stroke="#9fd6ff" strokeWidth={4} opacity={0.5} />
    </g>
  );
};

// ---------- fossils ----------
export const FishFossil: React.FC<{ s?: number }> = ({ s = 1 }) => {
  let ribs = '';
  for (let i = 0; i < 12; i++) {
    const x = -70 + i * 11;
    ribs += `M${x},0 Q${x - 4},${-14 * s} ${x - 8},${-22 + Math.abs(i - 6) * 1.2}M${x},0 Q${x - 4},14 ${x - 8},${22 - Math.abs(i - 6) * 1.2}`;
  }
  return (
    <g stroke="#3a2a1c" fill="none" strokeLinecap="round">
      <path d={smooth(pts([-100, 0, -60, -30, 20, -32, 70, -18, 100, 0, 70, 18, 20, 32, -60, 30]))} fill="#8a6e50" opacity={0.35} stroke="none" />
      <path d="M-100,0 L80,0" strokeWidth={3.5} />
      <path d={ribs} strokeWidth={1.8} />
      <path d={smooth(pts([80, -18, 120, -10, 124, 8, 82, 16]))} strokeWidth={2.5} fill="#7a5e42" />
      <circle cx={108} cy={-2} r={5} strokeWidth={2} />
      <path d="M-100,0 L-130,-26 L-122,0 L-130,26 Z" strokeWidth={2.5} fill="#7a5e42" />
    </g>
  );
};

export const SkullFossil: React.FC = () => (
  <g stroke="#2e2014" strokeLinejoin="round" filter="url(#rough)">
    <path d={smooth(pts([-160, -20, -120, -80, -40, -100, 60, -86, 150, -50, 190, -20, 176, 0, 100, 4, 0, 10, -100, 30, -150, 20]))} fill="#d8c3a0" strokeWidth={4} />
    <path d={smooth(pts([-110, -50, -80, -70, -50, -56, -70, -30, -100, -30]))} fill="#5a4430" strokeWidth={2.5} />
    <path d={smooth(pts([-30, -60, 30, -60, 60, -40, 20, -24, -20, -30]))} fill="#5a4430" strokeWidth={2.5} />
    <path d={smooth(pts([80, -44, 120, -36, 130, -24, 96, -22]))} fill="#5a4430" strokeWidth={2} />
    <path d={smooth(pts([-120, 40, -40, 30, 60, 14, 170, 8, 160, 30, 60, 46, -60, 66, -120, 60]))} fill="#cbb48e" strokeWidth={4} />
    <path d="M-60,4 l4,14 l4,-14 M-30,6 l4,16 l4,-16 M0,8 l4,16 l4,-16 M30,8 l4,15 l4,-15 M60,6 l4,14 l4,-14 M90,6 l4,12 l4,-12 M120,6 l3,10 l3,-10" fill="#f2e6cc" strokeWidth={1.6} />
  </g>
);
