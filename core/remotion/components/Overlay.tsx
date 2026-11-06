import React from 'react';
import { AbsoluteFill, Img, staticFile, useCurrentFrame } from 'remotion';
import { Svg, useTheme, fontOf, numFontOf, tr, useFrameSize } from './common';
import { Cue } from '../types';

// Hạt giấy + vignette theo theme của kênh
export const Overlay: React.FC<{ grainAsset?: string }> = ({ grainAsset }) => {
  const f = useCurrentFrame();
  const t = useTheme();
  const { W, H } = useFrameSize();
  return (
    <AbsoluteFill style={{ pointerEvents: 'none' }}>
      {grainAsset && (t.grain ?? 0) > 0 ? (
        <Img src={staticFile(grainAsset)} style={{ position: 'absolute', inset: 0, width: W, height: H, mixBlendMode: 'multiply', opacity: t.grain, transform: `translate(${(f % 3) - 1}px,${((f >> 1) % 3) - 1}px) scale(1.01)` }} />
      ) : null}
      {(t.vignette ?? 0) > 0 ? (
        <Svg style={{ opacity: Math.min(1, (t.vignette as number) * 1.6) }}>
          <rect width={W} height={H} fill="url(#vignette)" />
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
  const { tall } = useFrameSize();
  if (!c) return null;
  return (
    <div style={{ position: 'absolute', bottom: tall ? 380 : 64, left: tall ? 70 : 0, right: tall ? 130 : 0, textAlign: 'center' }}>
      <span style={{ fontFamily: fontOf(t), fontSize: tall ? 54 : 40, fontWeight: 600, lineHeight: 1.25, color: '#fff', whiteSpace: tall ? 'normal' : 'nowrap', WebkitTextStroke: '4px rgba(0,0,0,0.85)', paintOrder: 'stroke fill', textShadow: '0 2px 10px rgba(0,0,0,0.8)' }}>{c.text}</span>
    </div>
  );
};

// Dòng ghi chú AI: chữ nhỏ góc dưới phải, ở 4 giây cuối video. Chữ lấy từ channel.yaml (lang.labels.ai_notice).
export const AiNotice: React.FC<{ total: number; fps: number }> = ({ total, fps }) => {
  const f = useCurrentFrame();
  const t = useTheme();
  const { tall } = useFrameSize();
  const from = total - 4 * fps;
  const o = Math.max(0, Math.min(1, (f - from) / 12, (total - f) / 8));
  if (o <= 0 || !t.labels?.ai_notice) return null;
  return <div style={{ position: 'absolute', right: tall ? 150 : 40, bottom: tall ? 320 : 24, fontFamily: fontOf(t), fontSize: 20, fontWeight: 400, color: '#fff', opacity: 0.72 * o, textShadow: '0 1px 6px rgba(0,0,0,0.9)' }}>{t.labels.ai_notice}</div>;
};

// Badge mức chắc chắn: viên nhỏ góc trên phải, hiện 3 giây. props.badges: [{type, at_s}]
export const Badges: React.FC<{ items?: { type: string; at_s?: number }[]; fps: number }> = ({ items, fps }) => {
  const f = useCurrentFrame();
  const t = useTheme();
  const { tall } = useFrameSize();
  const b = (items || []).find((x) => f >= (x.at_s || 0) * fps && f < ((x.at_s || 0) + 3) * fps);
  if (!b) return null;
  const k = f - (b.at_s || 0) * fps;
  const o = Math.max(0, Math.min(1, k / 8, (3 * fps - k) / 8));
  const col = (t.badges || {})[b.type] || t.palette.accent;
  return (
    <div style={{ position: 'absolute', top: tall ? 200 : 64, right: tall ? 130 : 72, opacity: o, fontFamily: fontOf(t), fontSize: 28, fontWeight: 600, color: '#fff', background: col, padding: '8px 20px', borderRadius: 999, letterSpacing: 1, boxShadow: '0 4px 16px rgba(0,0,0,0.4)' }}>
      {tr(t, b.type)}
    </div>
  );
};

// Thẻ keyword hoặc số liệu (≤ 6 từ). Số trong thẻ tô màu accent, font số liệu riêng của kênh (theme.font_numbers).
// props.cards: [{text, at_s, dur_s, pos: [x, y], anchor: [x, y]}]: pos là tâm thẻ (px), align_srt.py tự đặt ở góc trên màn hình ít đè chủ thể nhất (Sếp 2026-11-03).
// anchor: thẻ là chú thích của 1 vật thì có chấm và đường dẫn từ vật tới thẻ (scenes.json: props.card_anchor).
export const Cards: React.FC<{ items?: { text: string; at_s?: number; dur_s?: number; pos?: number[]; anchor?: number[] }[]; fps: number }> = ({ items, fps }) => {
  const f = useCurrentFrame();
  const t = useTheme();
  const { tall } = useFrameSize();
  const c = (items || []).find((x) => f >= (x.at_s || 0) * fps && f < ((x.at_s || 0) + (x.dur_s || 3)) * fps);
  if (!c) return null;
  const len = (c.dur_s || 3) * fps, k = f - (c.at_s || 0) * fps;
  const o = Math.max(0, Math.min(1, k / 10, (len - k) / 10));
  const parts = c.text.split(/(\d[\d.,]*)/);
  const lead = c.anchor && c.pos ? (
    <svg style={{ position: 'absolute', inset: 0, overflow: 'visible', opacity: o }} width="100%" height="100%">
      <line x1={c.anchor[0]} y1={c.anchor[1]} x2={c.pos[0] + (c.anchor[0] < c.pos[0] ? -1 : 1) * 40} y2={c.pos[1]} stroke={t.palette.accent} strokeWidth={3} strokeDasharray={`${o * 400} 400`} />
      <circle cx={c.anchor[0]} cy={c.anchor[1]} r={8} fill={t.palette.accent} stroke="#1c140e" strokeWidth={3} />
    </svg>
  ) : null;
  return (
    <>
    {lead}
    <div style={c.pos ? { position: 'absolute', left: c.pos[0], top: c.pos[1], whiteSpace: 'nowrap', opacity: o, transform: `translate(-50%, -50%) translateY(${(1 - o) * 12}px)` }
      : { position: 'absolute', top: tall ? 300 : 250, left: tall ? 70 : 0, right: tall ? 130 : 0, textAlign: 'center', lineHeight: tall ? 1.45 : undefined, opacity: o, transform: `translateY(${(1 - o) * 12}px)` }}>
      <span style={{ fontFamily: numFontOf(t), fontSize: c.pos ? 52 : 64, fontWeight: 800, color: t.palette.fg, background: 'rgba(16,10,6,0.55)', padding: '10px 30px', borderRadius: 8, boxDecorationBreak: 'clone', WebkitBoxDecorationBreak: 'clone', textShadow: '0 2px 12px rgba(0,0,0,0.6)' }}>
        {parts.map((p, i) => (/^\d/.test(p) ? <span key={i} style={{ color: t.palette.accent }}>{p}</span> : p))}
      </span>
    </div>
    </>
  );
};

