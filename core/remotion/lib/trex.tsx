import React from 'react';
import { Inked, INK, hatch, smooth, P } from './lib';

const pts = (a: number[]): P[] => {
  const o: P[] = [];
  for (let i = 0; i < a.length; i += 2) o.push([a[i], a[i + 1]]);
  return o;
};
const BODY = smooth(pts([
  -720, -62, -600, -98, -480, -140, -340, -178, -200, -192, -80, -204, 40, -198, 150, -180, 230, -166, 290, -172, 330, -202,
  362, -230, 405, -242, 455, -240, 505, -224, 545, -202, 566, -182, 574, -162, 566, -146, 520, -141, 460, -134, 400, -126,
  372, -118, 360, -95, 346, -60, 330, -20, 300, 30, 250, 72, 170, 96, 80, 102, 0, 88, -60, 62, -130, 30, -250, 0, -400, -26,
  -550, -46, -660, -58,
]));
const JAW = smooth(pts([378, -128, 450, -137, 520, -143, 566, -147, 562, -130, 542, -113, 492, -100, 432, -92, 388, -92, 366, -100, 362, -116]));
const MOUTH = 'M372,-122 L560,-148 L556,-104 L370,-96 Z';
const THIGH = smooth(pts([-110, -40, -20, -66, 80, -32, 116, 50, 102, 130, 62, 200, 10, 222, -42, 206, -92, 150, -126, 60]));
const THIGH_LINE = smooth(pts([96, 10, 116, 60, 102, 130, 62, 200, 10, 222, -42, 206, -92, 150]), false);
const SHIN = smooth(pts([-38, -16, 26, -24, 48, 10, 34, 80, 14, 160, -2, 178, -30, 168, -52, 82, -58, 10]));
const META = smooth(pts([-26, -12, 16, -14, 40, 40, 62, 96, 42, 110, 18, 104, -4, 50]));
const TOES = 'M30,96 C70,92 104,100 124,110 L120,118 C96,113 64,112 30,114 Z M26,100 C4,104 -12,110 -22,118 L-16,122 C0,114 14,112 30,112 Z';
const ARM = 'M282,-20 C312,-12 326,6 322,26 L334,34 L328,38 L318,32 L322,44 L314,44 L310,30 C308,14 294,2 276,-2 Z';
const upperTeeth = () => {
  let d = '';
  for (let i = 0; i < 8; i++) {
    const x = 392 + i * 21;
    const y = -128 - i * 2;
    d += `M${x},${y} L${x + 4},${y + 13} L${x + 8},${y}Z`;
  }
  return d;
};
const lowerTeeth = () => {
  let d = '';
  for (let i = 0; i < 7; i++) {
    const x = 400 + i * 21;
    const y = -133 - i * 1.6;
    d += `M${x},${y + 4} L${x + 4},${y - 8} L${x + 8},${y + 4}Z`;
  }
  return d;
};

const Leg: React.FC<{ thigh: number; knee: number; ankle: number; far?: boolean }> = ({ thigh, knee, ankle, far }) => {
  const dark = far ? 0.55 : 0;
  const skin = far ? 'url(#trexLegFar)' : 'url(#trexLeg)';
  return (
    <g transform={`translate(0,-110) rotate(${thigh})`}>
      <g transform={`translate(35,195) rotate(${knee})`}>
        <g transform={`translate(-8,166) rotate(${ankle})`}>
          <Inked d={META} fill={skin} w={3.5} />
          <Inked d={TOES} fill={skin} w={3} />
          <path d="M120,110 L138,118 L120,120Z M-20,116 L-34,124 L-18,124Z" fill={INK} />
        </g>
        <Inked
          d={SHIN}
          fill={skin}
          w={3.5}
          shade={<><path d="M10,-30 L60,-30 L60,200 L0,200Z" fill="#2a2014" opacity={0.45} filter="url(#soft6)" /><path d={hatch(0, 40, 50, 170, 70, 7, 3)} stroke={INK} strokeWidth={1.2} opacity={0.45} /></>}
        />
      </g>
      <g>
        <clipPath id={far ? 'thighF' : 'thighN'}>
          <path d={THIGH} />
        </clipPath>
        <path d={THIGH} fill={far ? '#4d3f26' : 'url(#trexThigh)'} />
        <g clipPath={`url(#${far ? 'thighF' : 'thighN'})`}>
          <ellipse cx={-10} cy={-10} rx={70} ry={45} fill="#efdcaa" opacity={far ? 0 : 0.22} filter="url(#soft)" />
          <path d="M40,40 C120,60 120,200 40,240 L-60,240 C20,180 60,120 40,40Z" fill="#2e2214" opacity={0.5} filter="url(#soft)" />
          <path d={hatch(0, 120, 110, 230, 45, 7, 5)} stroke={INK} strokeWidth={1.3} opacity={0.45} />
          <path d={hatch(30, 140, 110, 230, -30, 8, 6)} stroke={INK} strokeWidth={1.1} opacity={0.3} />
        </g>
        <path d={THIGH_LINE} fill="none" stroke={INK} strokeWidth={4} strokeLinecap="round" />
        <path d="M-60,-20 C0,-40 60,0 80,60" fill="none" stroke={INK} strokeWidth={1.6} opacity={0.45} />
      </g>
      {dark ? <path d={THIGH} fill="#1a1208" opacity={0} /> : null}
    </g>
  );
};

// T. rex facing right, local origin at hip; ground at y≈+290
export const TRex: React.FC<{ phase: number; jaw?: number; rough?: boolean; silhouette?: string }> = ({ phase, jaw = 0, rough = true, silhouette }) => {
  const s = Math.sin(phase), c = Math.cos(phase);
  const legA = { thigh: -22 * s, knee: 28 * Math.max(0, c), ankle: 0 };
  legA.ankle = -(legA.thigh + legA.knee) * 0.85;
  const s2 = Math.sin(phase + Math.PI), c2 = Math.cos(phase + Math.PI);
  const legB = { thigh: -22 * s2, knee: 28 * Math.max(0, c2), ankle: 0 };
  legB.ankle = -(legB.thigh + legB.knee) * 0.85;
  const bob = -8 * Math.abs(Math.cos(phase));
  const g = (
    <g transform={`translate(0,${bob})`}>
      <defs>
        <linearGradient id="trexSkin" x1="0" y1="0" x2="0" y2="1" gradientUnits="objectBoundingBox">
          <stop offset="0" stopColor="#5b4a2e" />
          <stop offset="0.45" stopColor="#8a7448" />
          <stop offset="0.75" stopColor="#c9b07a" />
          <stop offset="1" stopColor="#e2cf9e" />
        </linearGradient>
        <linearGradient id="trexSkinU" x1="0" y1="-240" x2="0" y2="110" gradientUnits="userSpaceOnUse">
          <stop offset="0" stopColor="#5b4a2e" />
          <stop offset="0.4" stopColor="#86703f" />
          <stop offset="0.75" stopColor="#c4aa74" />
          <stop offset="1" stopColor="#e2cf9e" />
        </linearGradient>
        <linearGradient id="trexThigh" x1="0" y1="-110" x2="0" y2="230" gradientUnits="userSpaceOnUse">
          <stop offset="0" stopColor="#5e4c2c" />
          <stop offset="0.5" stopColor="#8a7243" />
          <stop offset="1" stopColor="#a68c5a" />
        </linearGradient>
        <linearGradient id="trexLeg" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor="#7d6a42" />
          <stop offset="1" stopColor="#56462a" />
        </linearGradient>
        <linearGradient id="trexLegFar" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor="#4d3f26" />
          <stop offset="1" stopColor="#32281a" />
        </linearGradient>
      </defs>
      {/* far side limbs */}
      <g transform="translate(-14,-6)">
        <Leg {...legB} far />
        <g transform="translate(-14,-4)">
          <Inked d={ARM} fill="#4d3f26" w={2.5} />
        </g>
      </g>
      <path d={MOUTH} fill="#5a1a14" stroke={INK} strokeWidth={3} />
      <path d="M380,-108 C440,-110 500,-116 550,-120" stroke="#a83e2c" strokeWidth={14} opacity={0.7} fill="none" />
      <Inked
        d={BODY}
        fill="url(#trexSkinU)"
        w={5}
        shade={
          <>
            {/* light from upper left */}
            <ellipse cx={-60} cy={-200} rx={380} ry={60} fill="#f6e6b8" opacity={0.4} filter="url(#soft)" />
            <ellipse cx={440} cy={-232} rx={90} ry={22} fill="#f6e6b8" opacity={0.45} filter="url(#soft6)" />
            {/* dorsal mottling */}
            {[-560, -450, -340, -230, -120, -10, 100, 200, 300].map((x, i) => (
              <path key={i} d={`M${x},${-230 + Math.abs(x) * 0.06} C${x + 30},-170 ${x + 20},-140 ${x - 6},${-110 + (i % 2) * 14}`} stroke="#33260f" strokeWidth={26 - Math.abs(i - 4) * 2.5} opacity={0.42} fill="none" filter="url(#soft6)" />
            ))}
            {/* belly / underside shadow */}
            <path d="M-500,-10 C-250,30 0,140 340,-10 L340,160 L-500,160Z" fill="#3a2a14" opacity={0.5} filter="url(#soft)" />
            <path d="M300,-140 C340,-100 350,-40 320,10 L400,40 L400,-140Z" fill="#3a2a14" opacity={0.35} filter="url(#soft)" />
            <path d={hatch(0, 40, 300, 110, 30, 8, 7)} stroke={INK} strokeWidth={1.4} opacity={0.45} />
            <path d={hatch(80, 50, 280, 110, -40, 9, 8)} stroke={INK} strokeWidth={1.1} opacity={0.3} />
            <path d={hatch(-560, -40, -260, 10, 12, 9, 9)} stroke={INK} strokeWidth={1.1} opacity={0.35} />
            <path d={hatch(310, -120, 360, -20, 70, 7, 10)} stroke={INK} strokeWidth={1.2} opacity={0.4} />
            {/* skin folds / muscle contours */}
            <path d="M262,-160 C250,-100 262,-50 300,-20" fill="none" stroke={INK} strokeWidth={2} opacity={0.55} />
            <path d="M150,-150 C175,-80 170,0 140,60" fill="none" stroke={INK} strokeWidth={1.5} opacity={0.35} />
            <path d="M330,-190 C335,-160 345,-140 362,-120" fill="none" stroke={INK} strokeWidth={1.6} opacity={0.5} />
            {[0, 1, 2, 3, 4, 5].map((i) => (
              <path key={i} d={`M${-640 + i * 90},${-74 - i * 20} c10,10 14,22 10,36`} fill="none" stroke={INK} strokeWidth={1.3} opacity={0.35} />
            ))}
            {/* skull details */}
            <path d={smooth([[470, -196], [505, -186], [528, -172], [505, -166], [478, -176]])} fill="#2c2010" opacity={0.4} />
            <path d="M410,-214 C432,-224 458,-222 478,-208" fill="none" stroke={INK} strokeWidth={4} strokeLinecap="round" />
            <path d="M398,-178 C420,-160 440,-150 470,-146" fill="none" stroke={INK} strokeWidth={1.5} opacity={0.55} />
            <path d="M520,-196 c10,4 20,12 26,22" fill="none" stroke={INK} strokeWidth={1.4} opacity={0.5} />
            {Array.from({ length: 26 }).map((_, i) => (
              <circle key={i} cx={392 + ((i * 37) % 170)} cy={-200 + ((i * 23) % 50)} r={2.2} fill={INK} opacity={0.25} />
            ))}
          </>
        }
      />
      {/* eye */}
      <ellipse cx={447} cy={-202} rx={9} ry={7} fill="#e8b23a" stroke={INK} strokeWidth={2.5} />
      <ellipse cx={448} cy={-202} rx={3} ry={6} fill={INK} />
      <circle cx={444} cy={-205} r={1.8} fill="#fff" />
      <path d="M548,-180 c4,-3 9,-2 11,1" stroke={INK} strokeWidth={3} fill="none" />
      <path d={upperTeeth()} fill="#f4ecd6" stroke={INK} strokeWidth={1.4} />
      <g transform={`rotate(${jaw * 24},375,-120)`}>
        <path d={lowerTeeth()} fill="#f4ecd6" stroke={INK} strokeWidth={1.4} />
        <Inked
          d={JAW}
          fill="#c4ac78"
          w={4}
          shade={<><path d="M360,-108 C440,-96 500,-110 566,-132 L566,-80 L360,-80Z" fill="#4a3a20" opacity={0.55} filter="url(#soft6)" /><path d={hatch(400, -112, 540, -92, 20, 6, 11)} stroke={INK} strokeWidth={1} opacity={0.4} /></>}
        />
      </g>
      <Leg {...legA} />
      <Inked d={ARM} fill="#7d6a42" w={2.5} />
    </g>
  );
  if (silhouette)
    return (
      <g filter={rough ? 'url(#rough)' : undefined}>
        <g style={{ filter: 'brightness(0.12) saturate(0.4)' }}>{g}</g>
      </g>
    );
  return <g filter={rough ? 'url(#rough)' : undefined}>{g}</g>;
};
