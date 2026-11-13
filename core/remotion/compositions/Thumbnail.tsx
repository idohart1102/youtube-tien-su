import React from 'react';
import { AbsoluteFill, Img, staticFile } from 'remotion';
import { DEFAULT_THEME, Theme, assetPath } from '../types';
import { ThemeCtx, fontOf } from '../components/common';
import '@fontsource/noto-serif-jp/700.css';
import '@fontsource/be-vietnam-pro/800.css';
import '@fontsource/be-vietnam-pro/900.css';

// Thumbnail 1280x720: nền + chủ thể + ảnh thật (tùy chọn) + hook do hệ thống ghép chữ. Quy định: core/standard/thumbnail.md.
// Sếp 2026-11-07: viền chủ thể mảnh (mặc định 4 px), màu theo nền (outline_auto do stage_prep.py --thumb ghi), không mặc định trắng;
// vùng nền dưới chữ hook làm tối (scrim); viền chữ mảnh; ảnh thật quan trọng đặt trên khung giấy màu theo tông ảnh.
export type ThumbProps = {
  theme: Theme;
  bg?: string;
  bg_filter?: string;
  subject?: { asset: string; x: number; y: number; h: number; flip?: boolean; outline?: string; outline_auto?: string; outline_w?: number; ghost?: number; ground?: boolean; pop?: number };
  spot?: { x: number; y: number; r: number; dark?: number };
  photo?: { asset: string; x: number; y: number; w: number; h?: number; rot?: number; paper?: string; paper_auto?: string; circle?: number[]; caption?: string; tag?: string; tag_color?: string };
  lines: string[];
  text?: { x?: number; y?: number; size?: number; align?: 'left' | 'right'; color?: string; hot?: string | string[]; hot_color?: string; upper?: boolean; scrim?: number; weight?: number; stroke?: number; line_height?: number; tracking?: number };
};

const SHADOW = 'drop-shadow(0 14px 20px rgba(0,0,0,0.55))';

export const Thumbnail: React.FC<ThumbProps> = ({ theme, bg, bg_filter, subject, photo, spot, lines, text = {} }) => {
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
  // Vùng tối dưới chữ: dải mờ dần từ phía có chữ (trên/dưới theo text.y), lệch về bên căn chữ
  const nLines = lines.length, lh = text.line_height ?? 1.08;
  const ty = text.y ?? 60, bottom = ty + nLines * size * lh + 70;
  const scrimO = text.scrim ?? 0.6;
  const side = text.align === 'right' ? 'to left' : 'to right';
  const olColor = subject ? subject.outline || subject.outline_auto || '#d9d0bd' : '';
  const olW = subject?.outline_w ?? 4;
  const paperC = photo ? photo.paper || photo.paper_auto || '#e6dccb' : '';
  return (
    <ThemeCtx.Provider value={th}>
      <AbsoluteFill style={{ background: th.palette.bg, overflow: 'hidden' }}>
        {bg ? <Img src={staticFile(assetPath(bg))} style={{ position: 'absolute', width: 1280, height: 720, objectFit: 'cover', filter: bg_filter ?? 'brightness(0.55) saturate(1.1)' }} /> : null}
        {spot ? ( // đèn rọi: tối vùng ngoài, sáng chủ thể nằm sẵn trong nền (hiện vật, xương)
          <AbsoluteFill style={{ background: `radial-gradient(circle at ${spot.x}px ${spot.y}px, rgba(255,236,200,0.18) 0px, rgba(0,0,0,0) ${spot.r * 0.6}px, rgba(0,0,0,${spot.dark ?? 0.55}) ${spot.r}px)`, mixBlendMode: 'normal' }} />
        ) : null}
        {scrimO > 0 ? (
          <AbsoluteFill style={{ background: ty < 360
            ? `linear-gradient(180deg, rgba(0,0,0,${scrimO}) 0px, rgba(0,0,0,${scrimO * 0.75}) ${bottom * 0.7}px, rgba(0,0,0,0) ${bottom + 80}px)`
            : `linear-gradient(0deg, rgba(0,0,0,${scrimO}) 0px, rgba(0,0,0,0) ${720 - ty + 80}px)` }}>
            <AbsoluteFill style={{ background: `linear-gradient(${side}, rgba(0,0,0,${scrimO * 0.35}) 0%, rgba(0,0,0,0) 70%)` }} />
          </AbsoluteFill>
        ) : null}
        {photo ? (
          <div style={{ position: 'absolute', left: photo.x, top: photo.y, padding: 12, background: paperC, transform: `translate(-50%,-50%) rotate(${photo.rot ?? -2}deg)`, boxShadow: '0 14px 34px rgba(0,0,0,0.6)' }}>
            <div style={{ position: 'relative' }}>
              <Img src={staticFile(assetPath(photo.asset))} style={{ display: 'block', width: photo.w, height: photo.h, objectFit: 'cover' }} />
              {photo.circle ? ( // khoanh đỏ [fx, fy, fr] theo tỷ lệ ảnh: chỉ đúng chi tiết đáng chú ý
                <div style={{ position: 'absolute', left: photo.circle[0] * photo.w - photo.circle[2] * photo.w, top: photo.circle[1] * (photo.h || photo.w) - photo.circle[2] * photo.w, width: 2 * photo.circle[2] * photo.w, height: 2 * photo.circle[2] * photo.w, border: '6px solid #e2342b', borderRadius: '50%', boxShadow: '0 0 0 2px rgba(0,0,0,0.5)' }} />
              ) : null}
            </div>
            {photo.tag ? <div style={{ position: 'absolute', left: -6, top: -22, padding: '4px 14px', background: photo.tag_color || '#e2342b', color: '#fff', fontFamily: fontOf(th), fontWeight: 900, fontSize: 34, letterSpacing: 1, boxShadow: '0 4px 10px rgba(0,0,0,0.5)', transform: 'rotate(-2deg)', whiteSpace: 'nowrap' }}>{photo.tag}</div> : null}
            {photo.caption ? <div style={{ fontFamily: fontOf(th), fontWeight: 800, fontSize: 30, color: '#2a2118', textAlign: 'center', paddingTop: 8, letterSpacing: 1 }}>{photo.caption}</div> : null}
          </div>
        ) : null}
        {subject ? (
          <>
            {subject.ground ? <div style={{ position: 'absolute', left: subject.x - subject.h * 0.9, top: subject.y - 34, width: subject.h * 1.8, height: 60, borderRadius: '50%', background: 'radial-gradient(closest-side, rgba(10,6,3,0.6), transparent)' }} /> : null}
            <svg width={0} height={0} style={{ position: 'absolute' }}>
              <filter id="thumb-ol" x="-5%" y="-5%" width="110%" height="110%">
                <feMorphology in="SourceAlpha" operator="dilate" radius={olW} result="d" />
                <feGaussianBlur in="d" stdDeviation="0.6" result="db" />
                <feFlood floodColor={olColor} />
                <feComposite in2="db" operator="in" result="ol" />
                <feMerge><feMergeNode in="ol" /><feMergeNode in="SourceGraphic" /></feMerge>
              </filter>
            </svg>
            <Img src={staticFile(assetPath(subject.asset))} style={{ position: 'absolute', left: subject.x, top: subject.y, height: subject.h, transform: `translate(-50%,-100%) scaleX(${subject.flip ? -1 : 1})`, filter: `url(#thumb-ol) ${subject.ghost ? `brightness(${1 - 0.55 * subject.ghost}) saturate(${1 - 0.8 * subject.ghost}) ` : ''}${subject.pop ? `brightness(${1 + 0.15 * subject.pop}) contrast(${1 + 0.15 * subject.pop}) saturate(${1 + 0.35 * subject.pop}) ` : ''}${SHADOW}`, opacity: subject.ghost ? 1 - 0.25 * subject.ghost : 1 }} />
          </>
        ) : null}
        <div style={{ position: 'absolute', left: text.align === 'right' ? undefined : text.x ?? 48, right: text.align === 'right' ? text.x ?? 48 : undefined, top: text.y ?? 60, textAlign: text.align ?? 'left', fontFamily: fontOf(th), fontWeight: text.weight ?? 800, fontSize: size, lineHeight: text.line_height ?? 1.08, letterSpacing: text.tracking ?? 0, color, WebkitTextStroke: `${text.stroke ?? 7}px #000`, paintOrder: 'stroke fill', textShadow: '0 4px 14px rgba(0,0,0,0.7)', textTransform: text.upper ? 'uppercase' : undefined, maxWidth: 1180 }}>
          {lines.map((l, i) => <div key={i}>{paint(l)}</div>)}
        </div>
      </AbsoluteFill>
    </ThemeCtx.Provider>
  );
};
