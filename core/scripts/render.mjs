// Render một tập: node core/scripts/render.mjs <episode_dir> [--preview] [--no-subs]
// Ảnh tĩnh để duyệt nháp: --stills <file.json> (mảng {t, out}: giây trong video, đường dẫn jpg), nửa độ phân giải, có phụ đề
// Đọc scenes.json của tập + theme.json và channel.yaml của kênh + config/machine.yaml. Ra <episode>/render/final.mp4
import crypto from 'node:crypto';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import yaml from 'js-yaml';
import { bundle } from '@remotion/bundler';
import { renderMedia, renderStill, selectComposition } from '@remotion/renderer';
import { outputConfig, finalEncodingOptions, fileSha, configSha } from './video_output.mjs';

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
if (!preview && (scenesDoc.fps ?? outputConfig.fps) !== outputConfig.fps) {
  throw new Error('Chuẩn chung yêu cầu dựng và xuất 30 fps. Sửa scenes.json trước khi render.');
}
if (scenesDoc.format && !['16:9', '9:16'].includes(scenesDoc.format)) throw new Error('Tỷ lệ khung hình không được hỗ trợ');
const captureInputs = async () => {
  const names = ['scenes.json', 'timeline.json', 'audio/subs.clean.srt', 'audio/narration.mp3'];
  const audioDir = path.join(ep, 'audio');
  if (fs.existsSync(audioDir)) names.push(...fs.readdirSync(audioDir)
    .filter((f) => /^voice\.(mp3|wav|m4a|aac)$/i.test(f)).map((f) => `audio/${f}`));
  const inputs = Object.fromEntries(await Promise.all(names.sort().map(async (name) => [name,
    fs.existsSync(path.join(ep, name)) ? await fileSha(path.join(ep, name)) : null])));
  const music = JSON.parse(fs.readFileSync(path.join(ep, 'scenes.json'), 'utf8')).music;
  if (music) {
    const p = music.asset.startsWith('shared/') ? path.join(ROOT, 'assets', music.asset) : path.join(ep, 'assets', music.asset);
    inputs[`music:${music.asset}`] = fs.existsSync(p) ? await fileSha(p) : null;
  }
  return inputs;
};
// Khóa render: mỗi máy chỉ 1 lần render cả video (máy 16GB không chịu nổi 2 bản song song).
// Lần render thứ hai tự đợi; khóa của tiến trình đã chết thì tự gỡ. Bản xem nhanh và ảnh tĩnh không cần khóa.
const LOCK = path.join(ROOT, '.render.lock');
const alive = (pid) => { try { process.kill(pid, 0); return true; } catch (e) { return e.code === 'EPERM'; } };
if (!preview && !process.argv.includes('--stills')) {
  let told = false;
  for (;;) {
    try {
      fs.writeFileSync(LOCK, JSON.stringify({ pid: process.pid, ep: path.relative(ROOT, ep), started: new Date().toISOString() }), { flag: 'wx' });
      break;
    } catch (e) {
      if (e.code !== 'EEXIST') throw e;
      let held = null;
      try { held = JSON.parse(fs.readFileSync(LOCK, 'utf8')); } catch { /* đang ghi dở, thử lại */ }
      if (held && !alive(held.pid)) { fs.rmSync(LOCK, { force: true }); continue; }
      if (!told && held) { console.log(`Đang chờ: ${held.ep} đang render (pid ${held.pid}, từ ${held.started})`); told = true; }
      await new Promise((r) => setTimeout(r, 5000));
    }
  }
  const release = () => {
    try { if (JSON.parse(fs.readFileSync(LOCK, 'utf8')).pid === process.pid) fs.rmSync(LOCK, { force: true }); } catch { /* không còn khóa */ }
  };
  process.on('exit', release);
  for (const sig of ['SIGINT', 'SIGTERM', 'SIGHUP']) process.on(sig, () => process.exit(130));
  if (told) console.log('Đến lượt, bắt đầu render');
}
const encodingInputs = await captureInputs();
const encodingConfigSha = configSha();
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
const stillsArg = process.argv.includes('--stills') ? process.argv[process.argv.indexOf('--stills') + 1] : null;
const subs = (!preview || stillsArg) && !process.argv.includes('--no-subs') && fs.existsSync(tl) ? JSON.parse(fs.readFileSync(tl, 'utf8')).subs : undefined;
const grain = fs.existsSync(path.join(assetsDir, 'shared/textures/paper.png')) ? 'assets/shared/textures/paper.png' : undefined;
// Nhạc nền: scenes.json {"music": {"asset": "shared/music/x.mp3", "db": -19}}. Thấp hơn giọng 18-20 dB, xem core/standard/visual.md
const m = scenesDoc.music;
const music = m ? { src: m.asset.startsWith('shared/') ? `assets/${m.asset}` : `ep/assets/${m.asset}`, volume: 10 ** ((m.db ?? -19) / 20) } : undefined;
let scenes = scenesDoc.scenes;
if (preview) { // bản xem nhanh: mỗi cảnh tối đa 2 giây
  scenes = scenes.map((s) => ({ ...s, duration_s: Math.min(2, s.duration_s) }));
}
const inputProps = { fps: scenesDoc.fps || 30, format: scenesDoc.format, scenes, theme, audio: hasAudio && !preview ? `ep/${audioRel}` : undefined, music: preview ? undefined : music, grainAsset: grain, subs };

console.log('Bundling…');
const serveUrl = await bundle({ entryPoint: path.join(ROOT, 'core/remotion/index.ts'), publicDir: pub });
const browserExecutable = machine.browser_executable || null;
const composition = await selectComposition({ serveUrl, id: 'LongForm', inputProps, browserExecutable });
if (!preview) {
  const [w, h] = scenesDoc.format === '9:16' ? outputConfig.portrait : outputConfig.landscape;
  if (composition.width !== w || composition.height !== h || composition.fps !== outputConfig.fps) {
    throw new Error('Composition không khớp chuẩn đầu ra chung');
  }
}
if (stillsArg) {
  const shots = JSON.parse(fs.readFileSync(stillsArg, 'utf8'));
  for (const [n, s] of shots.entries()) {
    const frame = Math.min(composition.durationInFrames - 1, Math.max(0, Math.round(s.t * composition.fps)));
    fs.mkdirSync(path.dirname(s.out), { recursive: true });
    await renderStill({ composition, serveUrl, output: s.out, frame, inputProps, browserExecutable, imageFormat: 'jpeg', jpegQuality: 80, scale: 0.5 });
    if (n % 20 === 0) console.log(`still ${n + 1}/${shots.length}`);
  }
  for (const l of ['assets', 'ep']) fs.unlinkSync(path.join(pub, l));
  fs.rmdirSync(pub);
  console.log('Xong', shots.length, 'ảnh tĩnh');
  process.exit(0);
}
const out = path.join(ep, 'render', preview ? 'preview.mp4' : 'final.pending.mp4');
fs.mkdirSync(path.dirname(out), { recursive: true });
let last = -1;
const encodeOptions = preview ? {} : finalEncodingOptions();
const encodeCommands = [];
if (!preview) {
  const override = encodeOptions.ffmpegOverride;
  encodeOptions.ffmpegOverride = (info) => {
    const args = override(info);
    encodeCommands.push({type: info.type, args});
    return args;
  };
}
// Render theo đoạn (--chunk-frames N hoặc machine.yaml render_chunk_frames): bản cuối giữ khung PNG và một bước mã hóa,
// nên Remotion ghi toàn bộ PNG ra ổ tạm trước khi mã hóa (cả tập 12 phút cần trên 150 GB). Mỗi đoạn hình (không tiếng)
// dùng đúng lệnh mã hóa đã chốt, ranh giới đoạn là bội số GOP; tiếng render 1 lần cả video (wav) rồi ghép:
// hình chép nguyên luồng, tiếng mã hóa AAC theo cấu hình. Biên nhận ghi đủ lệnh thực tế.
// Mặc định bản cuối chia đoạn 2400 khung (bài học 84); --chunk-frames 0 để tắt.
// Render lại theo đoạn (HT-11): đoạn lưu cố định ở render/chunks/ kèm mã băm nội dung (cảnh chạm khoảng đoạn kể cả cảnh vắt ranh giới
// và phần chuyển cảnh, phụ đề trong khoảng, theme, mã nguồn component đoạn đó dùng, asset, cấu hình mã hóa, phiên bản Remotion).
// Trùng mã thì dùng lại đoạn cũ. Đổi độ dài một cảnh thì mọi đoạn từ cảnh đó trở đi đổi mã và render lại. Tiếng luôn render cả bài.
const chunkArg = process.argv.includes('--chunk-frames') ? process.argv[process.argv.indexOf('--chunk-frames') + 1] : (machine.render_chunk_frames ?? 2400);
const sha = (buf) => crypto.createHash('sha256').update(buf).digest('hex');
const fileSig = (() => { const memo = new Map(); return (p) => {
  if (!memo.has(p)) memo.set(p, !fs.existsSync(p) ? 'thiếu' : fs.statSync(p).isDirectory()
    ? sha(fs.readdirSync(p, { recursive: true }).sort().map((f) => `${f}:${fs.statSync(path.join(p, f)).size}`).join('|')) : sha(fs.readFileSync(p)));
  return memo.get(p);
}; })();
const RM = path.join(ROOT, 'core/remotion');
// Băm toàn bộ mã nguồn Remotion: component import lẫn nhau (vd KenBurnsBg trong KenBurns.tsx), sửa file nào cũng render lại mọi đoạn
const SHARED = ['Root.tsx', 'index.ts', 'types.ts', ...['components', 'compositions', 'lib'].flatMap((d) => fs.readdirSync(path.join(RM, d)).sort().map((f) => `${d}/${f}`))];
const assetFile = (a) => (a.startsWith('shared/') ? path.join(assetsDir, a) : path.join(ep, 'assets', a));
const sceneAssets = (s) => { const pr = s.props || {}; const out = [s.asset];
  for (const x of [...(pr.layers || []), ...(pr.items || [])]) out.push(x.asset || x.cutout, x.sprite?.base);
  if (pr.sprite) out.push(pr.sprite.base);
  if (pr.strata_in) out.push(pr.strata_in.asset, pr.strata_in.from_asset);
  return out.filter(Boolean); };
const globalSig = sha(JSON.stringify({ theme, grain: grain ? fileSig(path.join(assetsDir, 'shared/textures/paper.png')) : null, format: scenesDoc.format, fps: scenesDoc.fps,
  shared: SHARED.map((f) => fileSig(path.join(RM, f))), enc: encodingConfigSha, lock: fileSig(path.join(ROOT, 'package-lock.json')), subsOn: !!subs }));
const chunkHash = (a, b, total) => {
  const fps = scenesDoc.fps || 30; let start = 0; const touched = [];
  scenes.forEach((s, i) => { const from = Math.round(start * fps); start += s.duration_s; const end = Math.round(start * fps);
    const lead = i && s.transition !== 'cut' ? 12 : 0;
    if (from - lead <= b && end > a) touched.push({ s, from, end, lead, assets: sceneAssets(s).map((x) => fileSig(assetFile(x))) }); });
  const cues = (subs || []).filter((c) => c.end * fps >= a && c.start * fps <= b + 1);
  return sha(JSON.stringify({ a, b, g: globalSig, touched, cues, tail: b >= total - 150 ? total : null }));
};
const gop = outputConfig.gop;
const chunk = !preview && Number(chunkArg) > 0 ? Math.max(gop, Math.floor(Number(chunkArg) / gop) * gop) : 0;
if (chunk && chunk < composition.durationInFrames) {
  const { execFileSync } = await import('node:child_process');
  const work = path.join(path.dirname(out), 'chunks');
  fs.mkdirSync(work, { recursive: true });
  const manP = path.join(work, 'chunks.json');
  const man = fs.existsSync(manP) ? JSON.parse(fs.readFileSync(manP, 'utf8')) : {};
  const total = composition.durationInFrames;
  const parts = [], next = {};
  let reused = 0;
  for (let a = 0, i = 0; a < total; a += chunk, i++) {
    const b = Math.min(total, a + chunk) - 1;
    const h = chunkHash(a, b, total);
    const part = path.join(work, `part${String(i).padStart(3, '0')}-${h.slice(0, 12)}.mp4`);
    next[i] = { a, b, hash: h, file: path.basename(part) };
    if (man[i]?.hash === h && fs.existsSync(part)) { parts.push(part); reused++; console.log(`đoạn ${i + 1}: dùng lại (khung ${a}-${b})`); continue; }
    await renderMedia({
      composition, serveUrl, codec: 'h264', outputLocation: part, inputProps, browserExecutable,
      ...encodeOptions, muted: true, frameRange: [a, b],
      concurrency: Number(machine.render_concurrency || 4), scale: 1,
      onProgress: ({ progress }) => { const p = Math.floor(((a + progress * (b - a + 1)) / total) * 100); if (p >= last + 5) { last = p; console.log(`render ${p}%`); } },
    });
    parts.push(part);
  }
  const wav = path.join(work, 'audio.wav');
  await renderMedia({ composition, serveUrl, codec: 'wav', outputLocation: wav, inputProps, browserExecutable,
    concurrency: Number(machine.render_concurrency || 4) });
  const list = path.join(work, 'list.txt');
  fs.writeFileSync(list, parts.map((p) => `file '${p.replace(/'/g, "'\\''")}'`).join('\n') + '\n');
  const c = outputConfig;
  const mux = ['-y', '-f', 'concat', '-safe', '0', '-i', list, '-i', wav, '-map', '0:v:0', '-map', '1:a:0',
    '-c:v', 'copy', '-c:a', c.audioCodec, '-b:a', c.audioBitrate, '-ar', String(c.sampleRate), '-ac', String(c.channels),
    '-color_range', 'tv', '-colorspace', c.colorSpace, '-color_primaries', c.colorSpace, '-color_trc', c.colorSpace,
    '-movflags', '+faststart', '-use_editlist', '0', '-shortest', out];
  execFileSync('ffmpeg', ['-hide_banner', '-loglevel', 'error', ...mux], { stdio: 'inherit' });
  encodeCommands.push({ type: 'chunked-mux', args: mux, chunks: { total: parts.length, reused, rendered: parts.length - reused, frames: chunk, files: Object.values(next).map((x) => x.file) } });
  // Giữ đoạn đang dùng cho lần sửa sau, xóa đoạn cũ không còn dùng và tiếng tạm
  const keep = new Set([...Object.values(next).map((x) => x.file), 'chunks.json']);
  for (const f of fs.readdirSync(work)) if (!keep.has(f)) fs.rmSync(path.join(work, f), { force: true });
  fs.writeFileSync(manP, JSON.stringify(next, null, 1));
  console.log(`Đoạn: ${parts.length - reused} render mới, ${reused} dùng lại`);
  console.log('render 100%');
} else {
await renderMedia({
  composition, serveUrl, codec: 'h264', outputLocation: out, inputProps, browserExecutable,
  ...encodeOptions,
  concurrency: Number(machine.render_concurrency || 4),
  scale: preview ? 0.5 : 1,
  onProgress: ({ progress }) => { const p = Math.floor(progress * 10); if (p !== last) { last = p; console.log(`render ${p * 10}%`); } },
});
}
if (!preview) {
  if (configSha() !== encodingConfigSha || JSON.stringify(await captureInputs()) !== JSON.stringify(encodingInputs)) {
    throw new Error('Đầu vào/cấu hình đổi trong khi render; không thay bản final cũ.');
  }
  const final = path.join(ep, 'render', 'final.mp4');
  const qa = path.join(ep, 'qa');
  fs.mkdirSync(qa, { recursive: true });
  fs.renameSync(out, final);
  fs.writeFileSync(path.join(qa, 'encoding.json'), JSON.stringify({
    video_sha: await fileSha(final), config_sha: encodingConfigSha, inputs: encodingInputs,
    settings: outputConfig,
    commands: encodeCommands,
  }, null, 2));
}
for (const l of ['assets', 'ep']) fs.unlinkSync(path.join(pub, l)); // gỡ link trước, không đụng tới thư mục thật
fs.rmdirSync(pub);
console.log('Xong:', path.relative(ROOT, preview ? out : path.join(ep, 'render/final.mp4')), `${(composition.durationInFrames / composition.fps / 60).toFixed(1)} phút`);
