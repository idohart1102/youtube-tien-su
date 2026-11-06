// Cấu hình dùng chung; không phụ thuộc Remotion để kiểm thử lệnh mã hóa riêng.
import fs from 'node:fs';
import { createHash } from 'node:crypto';
export const configPath = new URL('../../config/video-output.json', import.meta.url);
export const outputConfig = JSON.parse(fs.readFileSync(configPath, 'utf8'));
export const fileSha = async (p) => {
  const h = createHash('sha256');
  for await (const chunk of fs.createReadStream(p)) h.update(chunk);
  return h.digest('hex');
};
export const configSha = () => createHash('sha256').update(fs.readFileSync(configPath)).digest('hex');
export function finalEncodingOptions() {
  const c = outputConfig;
  return {
    codec: c.codec, crf: c.crf, x264Preset: c.preset,
    pixelFormat: c.pixelFormat, colorSpace: c.colorSpace, imageFormat: 'png',
    audioCodec: c.audioCodec, audioBitrate: c.audioBitrate,
    // Remotion 4.0.242 chưa có gopSize/sampleRate; giữ một bước mã hóa hình
    // để các cờ dưới áp dụng cho encoder thay vì chỉ cho bước ghép.
    disallowParallelEncoding: true,
    ffmpegOverride: ({ args }) => {
      // PNG từ Chromium là RGB sRGB. Chuyển cả hàm truyền sang BT.709;
      // filter mặc định của bản Remotion này chỉ đổi ma trận, giữ TRC sRGB.
      const base = args.slice(0, -1);
      const vf = base.indexOf('-vf');
      if (vf !== -1) base.splice(vf, 2);
      const size = base[base.indexOf('-s') + 1];
      if (!/^\d+x\d+$/.test(size)) throw new Error('Không xác định được kích thước mã hóa');
      return [
      ...base,
      '-vf', 'format=pix_fmts=gbrp,zscale=matrixin=gbr:transferin=iec61966-2-1:primariesin=709:rangein=full:matrix=709:transfer=709:primaries=709:range=limited,format=pix_fmts=yuv420p',
      '-aspect', size.replace('x', '/'),
      '-profile:v', c.profile, '-g', String(c.gop), '-keyint_min', String(c.gop),
      '-sc_threshold', '0', '-bf', String(c.bframes),
      '-x264-params', 'open-gop=0:b-adapt=0:cabac=1', '-flags', '+cgop',
      '-color_range', 'tv', '-colorspace', c.colorSpace,
      '-color_primaries', c.colorSpace, '-color_trc', c.colorSpace,
      '-c:a', c.audioCodec, '-ar', String(c.sampleRate), '-ac', String(c.channels),
      '-b:a', c.audioBitrate, '-movflags', '+faststart', '-use_editlist', '0',
      args.at(-1),
    ];
    },
  };
}
