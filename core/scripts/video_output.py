"""Kiểm tra kỹ thuật tệp thật và hiệu lực báo cáo, không QC giọng/nhịp đọc."""
import hashlib
import json
import math
import re
import struct
import subprocess
from fractions import Fraction
from pathlib import Path
from paths import ROOT

CONFIG = ROOT / 'config/video-output.json'

def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()

def input_hashes(ep):
    names = ['scenes.json', 'timeline.json', 'audio/subs.clean.srt', 'audio/narration.mp3']
    audio = ep / 'audio'
    if audio.exists():
        names += ['audio/' + p.name for p in audio.iterdir()
                  if re.fullmatch(r'voice\.(mp3|wav|m4a|aac)', p.name, re.I)]
    hashes = {name: sha(ep / name) if (ep / name).exists() else None for name in sorted(names)}
    if (ep / 'scenes.json').exists():
        music = json.loads((ep / 'scenes.json').read_text()).get('music')
        if music:
            rel = music['asset']
            p = ROOT / 'assets' / rel if rel.startswith('shared/') else ep / 'assets' / rel
            hashes['music:' + rel] = sha(p) if p.exists() else None
    return hashes

def mp4_structure(video):
    """Đọc kích thước atom, không nạp mdat (dữ liệu media) vào RAM."""
    top, edits = [], False
    with Path(video).open('rb') as f:
        def walk(start, end, nested=False):
            nonlocal edits
            pos = start
            while pos < end:
                f.seek(pos)
                head = f.read(8)
                if len(head) != 8:
                    raise ValueError('MP4 thiếu đầu atom')
                size, kind = struct.unpack('>I4s', head)
                header = 8
                if size == 1:
                    raw = f.read(8)
                    if len(raw) != 8:
                        raise ValueError('MP4 thiếu kích thước atom')
                    size, header = struct.unpack('>Q', raw)[0], 16
                elif size == 0:
                    size = end - pos
                if size < header or pos + size > end:
                    raise ValueError('MP4 có kích thước atom sai')
                if not nested:
                    top.append(kind)
                if kind == b'elst':
                    edits = True
                if kind in (b'moov', b'trak', b'edts'):
                    walk(pos + header, pos + size, True)
                pos += size
        walk(0, Path(video).stat().st_size)
    return (b'ftyp' in top and b'moov' in top and b'mdat' in top
            and top.index(b'moov') < top.index(b'mdat')), edits

def encoding_problems(receipt, c):
    """CRF/preset và bitrate mục tiêu cần biên nhận lệnh, không suy từ bitrate đo được."""
    commands = receipt.get('commands', [])
    def option(args, key):
        values = [args[i + 1] for i in range(len(args) - 1) if args[i] == key]
        return values[-1] if values else None
    args_list = [r['args'] for r in commands if isinstance(r, dict)
                 and isinstance(r.get('args'), list) and all(isinstance(s, str) for s in r['args'])]
    video = [a for a in args_list if option(a, '-c:v') == 'libx264']
    audio = [a for a in args_list if option(a, '-c:a') == c['audioCodec']]
    if not video or not audio:
        return ['Thiếu biên nhận lệnh mã hóa hình/âm thanh thực tế']
    want_video = {'-crf': str(c['crf']), '-preset': c['preset'], '-profile:v': c['profile']}
    want_audio = {'-b:a': c['audioBitrate'], '-ar': str(c['sampleRate']), '-ac': str(c['channels'])}
    out = []
    if any(option(video[-1], k) != v for k, v in want_video.items()):
        out.append('Lệnh mã hóa hình không đúng CRF/preset/profile đã chốt')
    if any(option(audio[-1], k) != v for k, v in want_audio.items()):
        out.append('Lệnh mã hóa âm thanh không đúng bitrate/tần số/số kênh mục tiêu')
    return out

def inspect(ep):
    ep = Path(ep)
    video = ep / 'render/final.mp4'
    c = json.loads(CONFIG.read_text())
    problems = []
    result = {'passed': False, 'config_sha': sha(CONFIG), 'inputs': input_hashes(ep),
              'video_sha': sha(video), 'problems': problems}
    try:
        scenes = json.loads((ep / 'scenes.json').read_text())
        timeline = json.loads((ep / 'timeline.json').read_text())
        receipt = json.loads((ep / 'qa/encoding.json').read_text())
        if receipt.get('video_sha') != result['video_sha'] or receipt.get('config_sha') != result['config_sha']:
            problems.append('Biên nhận mã hóa không khớp video hoặc cấu hình')
        if receipt.get('inputs') != result['inputs']:
            problems.append('Đầu vào đã đổi sau khi render')
        if receipt.get('settings') != c:
            problems.append('Biên nhận không xác nhận đúng cấu hình mã hóa đã chốt')
        problems += encoding_problems(receipt, c)
        if scenes.get('fps', c['fps']) != c['fps']:
            problems.append('Tốc độ dựng khác chuẩn 30 fps')
        p = subprocess.run(['ffprobe', '-v', 'error', '-show_streams', '-show_format',
                            '-of', 'json', str(video)], capture_output=True, text=True, check=True)
        info = json.loads(p.stdout)
        result['probe'] = info
        vs = [s for s in info['streams'] if s['codec_type'] == 'video']
        aus = [s for s in info['streams'] if s['codec_type'] == 'audio']
        if len(vs) != 1 or len(aus) != 1:
            raise ValueError('Cần đúng một luồng hình và một luồng âm thanh')
        v, a = vs[0], aus[0]
        want = c['portrait'] if scenes.get('format') == '9:16' else c['landscape']
        checks = {
            'độ phân giải': ([v['width'], v['height']], want),
            'mã hóa hình': (v.get('codec_name'), c['codec']),
            'profile hình': (v.get('profile', '').lower(), c['profile']),
            'định dạng điểm ảnh': (v.get('pix_fmt'), c['pixelFormat']),
            'quét liên tục': (v.get('field_order'), 'progressive'),
            'tỷ lệ điểm ảnh': (v.get('sample_aspect_ratio'), '1:1'),
            'dải màu': (v.get('color_range'), 'tv'),
            'ma trận màu': (v.get('color_space'), c['colorSpace']),
            'màu cơ sở': (v.get('color_primaries'), c['colorSpace']),
            'hàm truyền màu': (v.get('color_transfer'), c['colorSpace']),
            'mã hóa âm thanh': (a.get('codec_name'), c['audioCodec']),
            'profile âm thanh': (a.get('profile'), 'LC'),
            'tần số âm thanh': (int(a.get('sample_rate', 0)), c['sampleRate']),
            'số kênh âm thanh': (a.get('channels'), c['channels']),
        }
        for label, (actual, expected) in checks.items():
            if actual != expected:
                problems.append(f'Sai {label}: {actual}, cần {expected}')
        for key in ('r_frame_rate', 'avg_frame_rate'):
            if Fraction(v.get(key, '0/1')) != c['fps']:
                problems.append(f'Sai fps ({key})')
        duration = float(info['format']['duration'])
        result['duration'] = duration
        if not math.isfinite(duration) or duration <= 0:
            raise ValueError('Thời lượng không hợp lệ')
        if scenes.get('format') == '9:16' and duration > 180.1:
            problems.append('Video dọc vượt 3 phút của chuẩn Shorts')
        # AAC không dùng edit list có độ trễ encoder nhỏ; cho phép tối đa 100 ms.
        for s in (v, a):
            if abs(float(s.get('start_time', 0))) > .1:
                problems.append('Luồng hình/tiếng không bắt đầu gần mốc 0')
        if abs(float(v['duration']) - float(a['duration'])) > .1:
            problems.append('Độ dài luồng hình và tiếng lệch quá 100 ms')
        expected = sum(float(s['duration_s']) for s in scenes['scenes'])
        if abs(duration - expected) > .15:
            problems.append('Thời lượng tệp lệch tổng thời lượng cảnh')
        if abs(duration - float(timeline['audio_end'])) > 1.5:
            problems.append('Thời lượng tệp lệch timeline audio quá 1,5 giây')
        if not (ep / 'audio/subs.clean.srt').is_file():
            problems.append('Thiếu phụ đề SRT bàn giao')
        for s in timeline.get('subs', []):
            if not 0 <= s['start'] < s['end'] <= duration + .1:
                problems.append('Mốc phụ đề vượt thời lượng hoặc sai thứ tự')
                break
        fast, edits = mp4_structure(video)
        if not fast:
            problems.append('MP4 thiếu Fast Start hoặc sai cấu trúc')
        if edits:
            problems.append('MP4 còn edit list')
        frames = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0',
                                 '-show_frames', '-show_entries', 'frame=best_effort_timestamp_time,key_frame,pict_type',
                                 '-of', 'json', str(video)], capture_output=True, text=True, check=True)
        if frames.stderr.strip():
            problems.append('Có lỗi giải mã khi đọc khung hình')
        fs = json.loads(frames.stdout)['frames']
        if not fs:
            raise ValueError('Không đọc được khung hình')
        keys, b_run, max_b = [], 0, 0
        prev = None
        for i, frame in enumerate(fs):
            t = float(frame['best_effort_timestamp_time'])
            if prev is not None and abs(t - prev - 1 / c['fps']) > .0001:
                problems.append('Nhịp khung hình không cố định 30 fps')
                break
            prev = t
            if frame['key_frame']:
                keys.append(i)
            b_run = b_run + 1 if frame['pict_type'] == 'B' else 0
            max_b = max(max_b, b_run)
        if not keys or keys[0] != 0 or any(b - a > c['gop'] for a, b in zip(keys, keys[1:])) or len(fs) - keys[-1] > c['gop']:
            problems.append('Khoảng cách khung khóa vượt 15 khung')
        if max_b > c['bframes']:
            problems.append('Có quá hai khung B liên tiếp')
        # Kiểm tra bitstream thật: CABAC và khung khóa IDR của GOP đóng.
        cabac, idrs = [], 0
        headers = subprocess.Popen(['ffmpeg', '-hide_banner', '-i', str(video),
            '-map', '0:v:0', '-c:v', 'copy', '-bsf:v', 'trace_headers', '-an', '-f', 'null', '-'],
            stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
        with headers.stderr:
            for line in headers.stderr:
                if 'entropy_coding_mode_flag' in line:
                    cabac.append(line.rstrip().endswith('= 1'))
                if re.search(r'nal_unit_type\s+\S+\s+= 5\s*$', line):
                    idrs += 1
        if headers.wait() or not cabac or not all(cabac):
            problems.append('Không xác minh được H.264 dùng CABAC')
        if idrs != len(keys):
            problems.append('Khung khóa không hoàn toàn là IDR của GOP đóng')
        result['h264'] = {'cabac': bool(cabac) and all(cabac), 'idr_count': idrs,
                          'keyframe_count': len(keys), 'max_consecutive_b': max_b}
        result['frame_count'] = len(fs)
        decode = subprocess.run(['ffmpeg', '-v', 'error', '-xerror', '-err_detect', 'explode',
                                 '-i', str(video), '-map', '0:v:0', '-map', '0:a:0', '-f', 'null', '-'],
                                capture_output=True, text=True)
        if decode.returncode or decode.stderr.strip():
            problems.append('Giải mã đầy đủ hình/tiếng thất bại')
    except (OSError, ValueError, KeyError, TypeError, ZeroDivisionError, subprocess.CalledProcessError) as e:
        problems.append(f'Không xác minh đủ kỹ thuật: {str(e)[:250]}')
    # Phát hiện tệp hoặc đầu vào đổi trong lúc kiểm tra.
    if result['video_sha'] != sha(video) or result['inputs'] != input_hashes(ep) or result['config_sha'] != sha(CONFIG):
        problems.append('Video/cấu hình/đầu vào đổi trong lúc kiểm tra')
    result['passed'] = not problems
    return result

def report_problems(ep, report):
    """Cổng duyệt không tin mtime và không chấp nhận báo cáo kiểu cũ."""
    ep = Path(ep)
    if not isinstance(report, dict):
        return ['báo cáo kiểm tra máy không hợp lệ']
    tech = report.get('technical')
    if not isinstance(tech, dict) or tech.get('passed') is not True:
        return ['chưa có kiểm tra kỹ thuật đạt chuẩn']
    out = []
    if tech.get('problems') != []:
        out.append('kiểm tra kỹ thuật còn lỗi')
    if tech.get('video_sha') != sha(ep / 'render/final.mp4'):
        out.append('kiểm tra máy không khớp SHA-256 video hiện tại')
    if tech.get('config_sha') != sha(CONFIG):
        out.append('kiểm tra máy dùng cấu hình xuất cũ')
    if tech.get('inputs') != input_hashes(ep):
        out.append('đầu vào đã đổi sau lần kiểm tra máy')
    return out
