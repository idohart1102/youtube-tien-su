export type Theme = {
  palette: { bg: string; fg: string; accent: string; [k: string]: string };
  font: string;
  lang?: string;
  locale?: string; // định dạng số, vd vi-VN
  labels?: Record<string, string>; // chữ cố định của kênh (channel.yaml: lang.labels)
  ago?: { min: number; mult: number; digits: number; round?: number; tpl: string }[]; // mẫu "x năm trước"
  badges?: Record<string, string>;
  grain?: number;
  vignette?: number;
  subtitles?: boolean;
};

export type Scene = {
  id: string;
  duration_s: number;
  component: string;
  asset?: string;
  props?: Record<string, any>;
  narration?: string;
  transition?: 'fade' | 'dip' | 'cut';
};

export type EpisodeProps = {
  fps: number;
  scenes: Scene[];
  theme: Theme;
  music?: { src: string; volume: number };
  audio?: string; // đường dẫn trong public, vd 'ep/audio/narration.mp3'
  grainAsset?: string; // vd 'assets/backgrounds/paper.png'
  subs?: Cue[]; // phụ đề 1 dòng từ timeline.json (align_srt.py); không có thì không chạy phụ đề
};

export type Cue = { start: number; end: number; text: string };

export const DEFAULT_THEME: Theme = {
  palette: { bg: '#1b1712', fg: '#f2e6cf', accent: '#e0a030' },
  font: 'Be Vietnam Pro',
  grain: 0.35,
  vignette: 0.4,
  subtitles: true,
};

// Asset trong scenes.json: shared/... là dùng chung (assets/shared), còn lại thuộc tập (<tập>/assets). render.mjs gắn cả hai vào public.
export const assetPath = (a: string) => (a.startsWith('shared/') ? `assets/${a}` : `ep/assets/${a}`);
