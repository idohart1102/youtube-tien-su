import React from 'react';
import { AbsoluteFill, Img, staticFile } from 'remotion';
import { DEFAULT_THEME, Theme, assetPath } from '../types';
import { ThemeCtx, fontOf } from '../components/common';
import '@fontsource/noto-serif-jp/700.css';
import '@fontsource/be-vietnam-pro/800.css';
import '@fontsource/be-vietnam-pro/900.css';

// Thumbnail 1280x720: nền + chủ thể viền trắng + hook do hệ thống ghép chữ. Quy định: core/standard/thumbnail.md.
export type ThumbProps = {
  theme: Theme;
  bg?: string;
  bg_filter?: string;
  subject?: { asset: string; x: number; y: number; h: number; flip?: boolean };
  lines: string[];
  text?: { x?: number; y?: number; size?: number; align?: 'left' | 'right'; color?: string; hot?: string | string[]; hot_color?: string; upper?: boolean; weight?: number; stroke?: number; line_height?: number; tracking?: number };
};

const WHITE = 'drop-shadow(7px 0 0 #fff) drop-shadow(-7px 0 0 #fff) drop-shadow(0 7px 0 #fff) drop-shadow(0 -7px 0 #fff) drop-shadow(0 16px 22px rgba(0,0,0,0.55))';

export const Thumbnail: React.FC<ThumbProps> = ({ theme, bg, bg_filter, subject, lines, text = {} }) => {
  const th = { ...DEFAULT_THEME, ...theme };
  const size = text.size ?? 104;
  const color = text.color ?? '#ffffff';
  const hotColor = text.hot_color ?? '#FFD23F';
  const hots = (Array.isArray(text.hot) ? text.hot : text.hot ? [text.hot] : []) as string[];
  const paint = (l: string) => {
    const h = hots.find((x) => l.includes(x));
    if (!h) return l;
    const [a, b] = l.split(h);
    return <>{a}<span style={{ color: hotColor }}>{h}</span>{b}</>;
  };
  return (
    <ThemeCtx.Provider value={th}>
      <AbsoluteFill style={{ background: th.palette.bg, overflow: 'hidden' }}>
        {bg ? <Img src={staticFile(assetPath(bg))} style={{ position: 'absolute', width: 1280, height: 720, objectFit: 'cover', filter: bg_filter ?? 'brightness(0.55) saturate(1.1)' }} /> : null}
        {subject ? <Img src={staticFile(assetPath(subject.asset))} style={{ position: 'absolute', left: subject.x, top: subject.y, height: subject.h, transform: `translate(-50%,-100%) scaleX(${subject.flip ? -1 : 1})`, filter: WHITE }} /> : null}
        <div style={{ position: 'absolute', left: text.align === 'right' ? undefined : text.x ?? 48, right: text.align === 'right' ? text.x ?? 48 : undefined, top: text.y ?? 60, textAlign: text.align ?? 'left', fontFamily: fontOf(th), fontWeight: text.weight ?? 800, fontSize: size, lineHeight: text.line_height ?? 1.08, letterSpacing: text.tracking ?? 0, color, WebkitTextStroke: `${text.stroke ?? 14}px #000`, paintOrder: 'stroke fill', textShadow: '0 6px 18px rgba(0,0,0,0.75)', textTransform: text.upper ? 'uppercase' : undefined, maxWidth: 1180 }}>
          {lines.map((l, i) => <div key={i}>{paint(l)}</div>)}
        </div>
      </AbsoluteFill>
    </ThemeCtx.Provider>
  );
};
