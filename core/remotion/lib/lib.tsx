import React from 'react';

export const INK = '#1c140e';

export const rng = (seed: number) => {
  let a = seed >>> 0;
  return () => {
    a = (a + 0x6d2b79f5) >>> 0;
    let t = a;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
};

export type P = [number, number];

// Catmull-Rom spline through points -> cubic bezier path
export const smooth = (pts: P[], closed = true, tension = 1) => {
  const n = pts.length;
  const get = (i: number) => (closed ? pts[(i + n) % n] : pts[Math.max(0, Math.min(n - 1, i))]);
  let d = `M${pts[0][0].toFixed(1)},${pts[0][1].toFixed(1)}`;
  const last = closed ? n : n - 1;
  for (let i = 0; i < last; i++) {
    const p0 = get(i - 1), p1 = get(i), p2 = get(i + 1), p3 = get(i + 2);
    const c1 = [p1[0] + ((p2[0] - p0[0]) / 6) * tension, p1[1] + ((p2[1] - p0[1]) / 6) * tension];
    const c2 = [p2[0] - ((p3[0] - p1[0]) / 6) * tension, p2[1] - ((p3[1] - p1[1]) / 6) * tension];
    d += `C${c1[0].toFixed(1)},${c1[1].toFixed(1)} ${c2[0].toFixed(1)},${c2[1].toFixed(1)} ${p2[0].toFixed(1)},${p2[1].toFixed(1)}`;
  }
  return closed ? d + 'Z' : d;
};

// irregular blob around a center
export const blobPts = (cx: number, cy: number, rx: number, ry: number, n: number, jit: number, seed: number): P[] => {
  const r = rng(seed);
  const out: P[] = [];
  for (let i = 0; i < n; i++) {
    const a = (i / n) * Math.PI * 2;
    const k = 1 + (r() - 0.5) * jit;
    out.push([cx + Math.cos(a) * rx * k, cy + Math.sin(a) * ry * k]);
  }
  return out;
};

// parallel hatch lines inside a box, angle in degrees
export const hatch = (x0: number, y0: number, x1: number, y1: number, angle: number, gap: number, seed = 1, len = 1) => {
  const r = rng(seed);
  const a = (angle * Math.PI) / 180;
  const dx = Math.cos(a), dy = Math.sin(a);
  const cx = (x0 + x1) / 2, cy = (y0 + y1) / 2;
  const R = Math.hypot(x1 - x0, y1 - y0) / 2;
  let d = '';
  for (let s = -R; s < R; s += gap * (0.7 + r() * 0.6)) {
    const px = cx - dy * s, py = cy + dx * s;
    const l = R * len * (0.6 + r() * 0.4);
    const off = (r() - 0.5) * R * 0.4;
    d += `M${(px - dx * l + dx * off).toFixed(1)},${(py - dy * l + dy * off).toFixed(1)}L${(px + dx * l + dx * off).toFixed(1)},${(py + dy * l + dy * off).toFixed(1)}`;
  }
  return d;
};

let uid = 0;
export const useId = (p: string) => React.useMemo(() => `${p}${uid++}`, []);

// Shape filled with a gradient, painterly shade inside (clipped), and a double inked outline
export const Inked: React.FC<{
  d: string;
  fill: string;
  shade?: React.ReactNode;
  w?: number;
  ink?: string;
  opacity?: number;
}> = ({ d, fill, shade, w = 4, ink = INK, opacity = 1 }) => {
  const id = useId('clip');
  return (
    <g opacity={opacity}>
      <clipPath id={id}>
        <path d={d} />
      </clipPath>
      <path d={d} fill={fill} />
      {shade ? <g clipPath={`url(#${id})`}>{shade}</g> : null}
      <path d={d} fill="none" stroke={ink} strokeWidth={w * 0.45} opacity={0.35} transform="translate(2.2,1.6)" strokeLinejoin="round" />
      <path d={d} fill="none" stroke={ink} strokeWidth={w} strokeLinejoin="round" strokeLinecap="round" />
    </g>
  );
};

export const Defs: React.FC = () => (
  <defs>
    <filter id="rough" x="-10%" y="-10%" width="120%" height="120%">
      <feTurbulence type="fractalNoise" baseFrequency="0.03" numOctaves={2} seed={4} result="n" />
      <feDisplacementMap in="SourceGraphic" in2="n" scale={6} xChannelSelector="R" yChannelSelector="G" />
    </filter>
    <filter id="soft" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation={14} />
    </filter>
    <filter id="soft6" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation={6} />
    </filter>
    <filter id="glow" x="-100%" y="-100%" width="300%" height="300%">
      <feGaussianBlur stdDeviation={30} />
    </filter>
    <radialGradient id="vignette" cx="50%" cy="50%" r="75%">
      <stop offset="55%" stopColor="#000" stopOpacity={0} />
      <stop offset="100%" stopColor="#1a0f08" stopOpacity={0.65} />
    </radialGradient>
  </defs>
);

export const clamp = (v: number, a = 0, b = 1) => Math.max(a, Math.min(b, v));
export const ease = (t: number) => {
  const x = clamp(t);
  return x * x * (3 - 2 * x);
};
export const ramp = (f: number, a: number, b: number) => ease((f - a) / (b - a));
