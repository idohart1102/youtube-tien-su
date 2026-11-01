// Ghép thumbnail cho một tập: node core/scripts/thumb.mjs <episode_dir> [thumb_spec.json]
// Mỗi mục trong spec là một phương án {name, bg, subject, lines, text}. Ra <episode>/thumb/<name>.jpg và bảng thu nhỏ 160x90 để tự kiểm.
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import yaml from 'js-yaml';
import { bundle } from '@remotion/bundler';
import { renderStill, selectComposition } from '@remotion/renderer';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
const ep = path.resolve(process.argv[2] || '');
const specPath = process.argv[3] ? path.resolve(process.argv[3]) : path.join(ep, 'thumb_spec.json');
const specs = JSON.parse(fs.readFileSync(specPath, 'utf8'));
const channel = yaml.load(fs.readFileSync(path.join(ep, '../../channel.yaml'), 'utf8'));
const theme = { ...JSON.parse(fs.readFileSync(path.join(ep, '../../theme.json'), 'utf8')), lang: channel.language, locale: channel.locale, labels: channel.lang.labels };
const pub = fs.mkdtempSync(path.join(os.tmpdir(), 'yt-thumb-'));
fs.symlinkSync(path.join(ROOT, 'assets'), path.join(pub, 'assets'), 'junction');
fs.symlinkSync(ep, path.join(pub, 'ep'), 'junction');
const serveUrl = await bundle({ entryPoint: path.join(ROOT, 'core/remotion/index.ts'), publicDir: pub });
const out = path.join(ep, 'thumb');
fs.mkdirSync(out, { recursive: true });
for (const s of specs) {
  const inputProps = { ...s, theme };
  const composition = await selectComposition({ serveUrl, id: 'Thumbnail', inputProps });
  await renderStill({ composition, serveUrl, inputProps, frame: 0, output: path.join(out, `${s.name}.jpg`), imageFormat: 'jpeg', jpegQuality: 92 });
  console.log(path.relative(ROOT, path.join(out, `${s.name}.jpg`)));
}
for (const l of ['assets', 'ep']) fs.unlinkSync(path.join(pub, l));
fs.rmdirSync(pub);
