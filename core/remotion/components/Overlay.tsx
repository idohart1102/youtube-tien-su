import React from 'react';
import { AbsoluteFill, Img, staticFile, useCurrentFrame } from 'remotion';
import { Svg, useTheme, fontOf, tr } from './common';
import { Cue } from '../types';

// Hạt giấy + vignette theo theme của kênh
export const Overlay: React.FC<{ grainAsset?: string }> = ({ grainAsset }) => {
  const f = useCurrentFrame();
  const t = useTheme();
  return (
    <AbsoluteFill style={{ pointerEvents: 'none' }}>
      {grainAsset && (t.grain ?? 0) > 0 ? (
        <Img src={staticFile(grainAsset)} style={{ position: 'absolute', inset: 0, width: 1920, height: 1080, mixBlendMode: 'multiply', opacity: t.grain, transform: `translate(${(f % 3) - 1}px,${((f >> 1) % 3) - 1}px) scale(1.01)` }} />
      ) : null}
      {(t.vignette ?? 0) > 0 ? (
        <Svg style={{ opacity: Math.min(1, (t.vignette as number) * 1.6) }}>
          <rect width={1920} height={1080} fill="url(#vignette)" />
        </Svg>
      ) : null}
    </AbsoluteFill>
  );
};

// Phụ đề lời đọc của cảnh (theme.subtitles = true)
export const Caption: React.FC<{ text?: string; dur: number }> = ({ text, dur }) => {
  const f = useCurrentFrame();
  const t = useTheme();
  if (!text || t.subtitles === false) return null;
  const o = Math.min(1, f / 8, (dur - f) / 8);
  return (
    <div style={{ position: 'absolute', bottom: 60, left: 160, right: 160, textAlign: 'center', opacity: Math.max(0, o) }}>
      <span style={{ fontFamily: fontOf(t), fontSize: 40, lineHeight: 1.5, color: '#fff', fontWeight: 600, background: 'rgba(16,10,6,0.55)', padding: '6px 18px', boxDecorationBreak: 'clone', WebkitBoxDecorationBreak: 'clone' }}>{text}</span>
    </div>
  );
};

// Phụ đề 1 dòng chạy theo timeline (srt). Chữ trắng không nền, viền tối mảnh để đọc được trên mọi ảnh (Sếp chốt 2026-10-28).
export const Subtitles: React.FC<{ cues: Cue[]; fps: number }> = ({ cues, fps }) => {
  const f = useCurrentFrame();
  const t = useTheme();
  const s = f / fps;
  const c = cues.find((x) => s >= x.start && s < x.end);
  if (!c) return null;
  return (
    <div style={{ position: 'absolute', bottom: 64, left: 0, right: 0, textAlign: 'center' }}>
      <span style={{ fontFamily: fontOf(t), fontSize: 40, fontWeight: 600, lineHeight: 1.25, color: '#fff', whiteSpace: 'nowrap', WebkitTextStroke: '4px rgba(0,0,0,0.85)', paintOrder: 'stroke fill', textShadow: '0 2px 10px rgba(0,0,0,0.8)' }}>{c.text}</span>
    </div>
  );
};

// Dòng ghi chú AI: chữ nhỏ góc dưới phải, ở 4 giây cuối video. Chữ lấy từ channel.yaml (lang.labels.ai_notice).
export const AiNotice: React.FC<{ total: number; fps: number }> = ({ total, fps }) => {
  const f = useCurrentFrame();
  const t = useTheme();
  const from = total - 4 * fps;
  const o = Math.max(0, Math.min(1, (f - from) / 12, (total - f) / 8));
  if (o <= 0 || !t.labels?.ai_notice) return null;
  return <div style={{ position: 'absolute', right: 40, bottom: 24, fontFamily: fontOf(t), fontSize: 20, fontWeight: 400, color: '#fff', opacity: 0.72 * o, textShadow: '0 1px 6px rgba(0,0,0,0.9)' }}>{t.labels.ai_notice}</div>;
};

// Badge mức chắc chắn: viên nhỏ góc trên phải, hiện 3 giây. props.badges: [{type, at_s}]
export const Badges: React.FC<{ items?: { type: string; at_s?: number }[]; fps: number }> = ({ items, fps }) => {
  const f = useCurrentFrame();
  const t = useTheme();
  const b = (items || []).find((x) => f >= (x.at_s || 0) * fps && f < ((x.at_s || 0) + 3) * fps);
  if (!b) return null;
  const k = f - (b.at_s || 0) * fps;
  const o = Math.max(0, Math.min(1, k / 8, (3 * fps - k) / 8));
  const col = (t.badges || {})[b.type] || t.palette.accent;
  return (
    <div style={{ position: 'absolute', top: 64, right: 72, opacity: o, fontFamily: fontOf(t), fontSize: 28, fontWeight: 600, color: '#fff', background: col, padding: '8px 20px', borderRadius: 999, letterSpacing: 1, boxShadow: '0 4px 16px rgba(0,0,0,0.4)' }}>
      {tr(t, b.type)}
    </div>
  );
};

// Thẻ keyword hoặc số liệu (≤ 6 từ), 1/3 trên màn hình. Số trong thẻ tô màu accent. props.cards: [{text, at_s, dur_s}]
export const Cards: React.FC<{ items?: { text: string; at_s?: number; dur_s?: number }[]; fps: number }> = ({ items, fps }) => {
  const f = useCurrentFrame();
  const t = useTheme();
  const c = (items || []).find((x) => f >= (x.at_s || 0) * fps && f < ((x.at_s || 0) + (x.dur_s || 3)) * fps);
  if (!c) return null;
  const len = (c.dur_s || 3) * fps, k = f - (c.at_s || 0) * fps;
  const o = Math.max(0, Math.min(1, k / 10, (len - k) / 10));
  const parts = c.text.split(/(\d[\d.,]*)/);
  return (
    <div style={{ position: 'absolute', top: 250, left: 0, right: 0, textAlign: 'center', opacity: o, transform: `translateY(${(1 - o) * 12}px)` }}>
      <span style={{ fontFamily: fontOf(t), fontSize: 64, fontWeight: 800, color: t.palette.fg, background: 'rgba(16,10,6,0.55)', padding: '10px 30px', borderRadius: 8, textShadow: '0 2px 12px rgba(0,0,0,0.6)' }}>
        {parts.map((p, i) => (/^\d/.test(p) ? <span key={i} style={{ color: t.palette.accent }}>{p}</span> : p))}
      </span>
    </div>
  );
};

