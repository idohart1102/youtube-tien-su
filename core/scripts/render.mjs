// Render một tập: node core/scripts/render.mjs <episode_dir> [--preview] [--no-subs]
// Đọc scenes.json của tập + theme.json và channel.yaml của kênh + config/machine.yaml. Ra <episode>/render/final.mp4
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import yaml from 'js-yaml';
import { bundle } from '@remotion/bundler';
import { renderMedia, selectComposition } from '@remotion/renderer';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
const ep = path.resolve(process.argv[2] || '');
const preview = process.argv.includes('--preview');
if (!fs.existsSync(path.join(ep, 'scenes.json'))) { console.error('Không thấy scenes.json trong', ep); process.exit(1); }

// machine.yaml chỉ gồm các dòng "key: value" đơn giản
const readYaml = (p) => Object.fromEntries(fs.readFileSync(p, 'utf8').split('\n')
  .map((l) => l.replace(/#.*$/, '').trim()).filter((l) => l.includes(':'))
  .map((l) => { const i = l.indexOf(':'); return [l.slice(0, i).trim(), l.slice(i + 1).trim().replace(/^"|"$/g, '')]; }));
const mp = fs.existsSync(path.join(ROOT, 'config/machine.yaml')) ? path.join(ROOT, 'config/machine.yaml') : path.join(ROOT, 'config/machine.example.yaml');
const machine = readYaml(mp);
const assetsDir = path.join(ROOT, 'assets');

const scenesDoc = JSON.parse(fs.readFileSync(path.join(ep, 'scenes.json'), 'utf8'));
const channel = yaml.load(fs.readFileSync(path.join(ep, '../../channel.yaml'), 'utf8'));
const theme = { ...JSON.parse(fs.readFileSync(path.join(ep, '../../theme.json'), 'utf8')), lang: channel.language, locale: channel.locale, labels: channel.lang.labels, ago: channel.lang.ago };

// public tạm: symlink assets/ và tập hiện tại (ep/) để staticFile() thấy được, không copy cả repo
const pub = fs.mkdtempSync(path.join(os.tmpdir(), 'yt-pub-'));
fs.symlinkSync(assetsDir, path.join(pub, 'assets'), 'junction');
fs.symlinkSync(ep, path.join(pub, 'ep'), 'junction');

// Audio: file Sếp gửi (audio/voice.*), tập cũ có thể còn narration.mp3
const voice = fs.existsSync(path.join(ep, 'audio')) ? fs.readdirSync(path.join(ep, 'audio')).find((f) => /^voice\.(mp3|wav|m4a|aac)$/i.test(f)) : undefined;
const audioRel = voice ? `audio/${voice}` : 'audio/narration.mp3';
const hasAudio = fs.existsSync(path.join(ep, audioRel));
// Phụ đề 1 dòng từ timeline.json (align_srt.py). Tắt: --no-subs, hoặc theme.subtitles = false
const tl = path.join(ep, 'timeline.json');
const subs = !preview && !process.argv.includes('--no-subs') && fs.existsSync(tl) ? JSON.parse(fs.readFileSync(tl, 'utf8')).subs : undefined;
const grain = fs.existsSync(path.join(assetsDir, 'shared/textures/paper.png')) ? 'assets/shared/textures/paper.png' : undefined;
// Nhạc nền: scenes.json {"music": {"asset": "shared/music/x.mp3", "db": -19}}. Thấp hơn giọng 18-20 dB, xem core/standard/visual.md
const m = scenesDoc.music;
const music = m ? { src: m.asset.startsWith('shared/') ? `assets/${m.asset}` : `ep/assets/${m.asset}`, volume: 10 ** ((m.db ?? -19) / 20) } : undefined;
let scenes = scenesDoc.scenes;
if (preview) { // bản xem nhanh: mỗi cảnh tối đa 2 giây
  scenes = scenes.map((s) => ({ ...s, duration_s: Math.min(2, s.duration_s) }));
}
const inputProps = { fps: scenesDoc.fps || 30, scenes, theme, audio: hasAudio && !preview ? `ep/${audioRel}` : undefined, music: preview ? undefined : music, grainAsset: grain, subs };

console.log('Bundling…');
const serveUrl = await bundle({ entryPoint: path.join(ROOT, 'core/remotion/index.ts'), publicDir: pub });
const browserExecutable = machine.browser_executable || null;
const composition = await selectComposition({ serveUrl, id: 'LongForm', inputProps, browserExecutable });
const out = path.join(ep, 'render', preview ? 'preview.mp4' : 'final.mp4');
fs.mkdirSync(path.dirname(out), { recursive: true });
let last = -1;
await renderMedia({
  composition, serveUrl, codec: 'h264', outputLocation: out, inputProps, browserExecutable,
  concurrency: Number(machine.render_concurrency || 4),
  scale: preview ? 0.5 : 1,
  onProgress: ({ progress }) => { const p = Math.floor(progress * 10); if (p !== last) { last = p; console.log(`render ${p * 10}%`); } },
});
for (const l of ['assets', 'ep']) fs.unlinkSync(path.join(pub, l)); // gỡ link trước, không đụng tới thư mục thật
fs.rmdirSync(pub);
console.log('Xong:', path.relative(ROOT, out), `${(composition.durationInFrames / composition.fps / 60).toFixed(1)} phút`);
