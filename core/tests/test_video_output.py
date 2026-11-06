"""Hồi quy chuẩn xuất: báo cáo cũ/thiếu không được vượt cổng duyệt."""
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / 'scripts'
sys.path.insert(0, str(SCRIPTS))
import status

class ReportGateTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.ep = Path(self.tmp.name)
        for name in ('render', 'qa', 'thumb'):
            (self.ep / name).mkdir()
        self.video = self.ep / 'render/final.mp4'
        self.video.write_bytes(b'video-current')
        (self.ep / 'thumb/thumbnail.jpg').write_bytes(b'image')
        sha = status.file_sha(self.video)
        (self.ep / 'qa/qc_v1.md').write_text(f'- Video: {sha}\n- Điểm khung hình trung bình: 9.5/10. Lỗi nặng: 0.\n')

    def test_legacy_report_cannot_approve_video(self):
        (self.ep / 'qa/render_check.json').write_text(json.dumps({'problems': []}))
        self.assertTrue(status.final_problems(self.ep), 'Báo cáo thiếu xác nhận kỹ thuật phải chặn duyệt')

    def test_report_with_wrong_sha_cannot_approve_video(self):
        (self.ep / 'qa/render_check.json').write_text(json.dumps({'problems': [], 'video_sha': 'old', 'technical': {'passed': True}}))
        self.assertTrue(status.final_problems(self.ep), 'Đổi mtime báo cáo không được vượt kiểm tra SHA')

    def test_invalid_report_fails_closed(self):
        (self.ep / 'qa/render_check.json').write_text('{broken')
        self.assertTrue(status.final_problems(self.ep))

class MediaInspectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import subprocess
        cls.tmp = tempfile.TemporaryDirectory()
        cls.base = Path(cls.tmp.name)
        cls.good = cls.base / 'good.mp4'
        cls.encode_command = ['ffmpeg', '-v', 'error', '-y', '-f', 'lavfi', '-i',
            'testsrc2=size=1920x1080:rate=30', '-f', 'lavfi', '-i',
            'sine=frequency=440:sample_rate=48000', '-t', '1',
            '-c:v', 'libx264', '-crf', '18', '-preset', 'medium', '-profile:v', 'high',
            '-g', '15', '-keyint_min', '15', '-sc_threshold', '0', '-bf', '2',
            '-x264-params', 'open-gop=0:b-adapt=0:cabac=1', '-flags', '+cgop',
            '-pix_fmt', 'yuv420p', '-color_range', 'tv', '-colorspace', 'bt709',
            '-vf', 'setparams=range=limited:color_primaries=bt709:color_trc=bt709:colorspace=bt709',
            '-color_primaries', 'bt709', '-color_trc', 'bt709', '-c:a', 'aac',
            '-ar', '48000', '-ac', '2', '-b:a', '384k', '-movflags', '+faststart',
            '-use_editlist', '0', str(cls.good)]
        subprocess.run(cls.encode_command, check=True)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def setUp(self):
        import shutil
        import video_output as vo
        self.vo = vo
        self.tmp_ep = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp_ep.cleanup)
        self.ep = Path(self.tmp_ep.name)
        for d in ('render', 'qa', 'audio'):
            (self.ep / d).mkdir()
        shutil.copyfile(self.good, self.ep / 'render/final.mp4')
        (self.ep / 'scenes.json').write_text(json.dumps({'fps': 30, 'scenes': [{'duration_s': 1}]}))
        (self.ep / 'timeline.json').write_text(json.dumps({'audio_end': 1, 'subs': []}))
        (self.ep / 'audio/subs.clean.srt').write_text('1\n00:00:00,000 --> 00:00:00,900\nTest\n')
        self.receipt()

    def receipt(self):
        (self.ep / 'qa/encoding.json').write_text(json.dumps({
            'video_sha': self.vo.sha(self.ep / 'render/final.mp4'),
            'config_sha': self.vo.sha(self.vo.CONFIG), 'inputs': self.vo.input_hashes(self.ep),
            'settings': json.loads(self.vo.CONFIG.read_text()),
            'commands': [{'type': 'stitcher', 'args': self.encode_command[1:]}]}))

    def test_real_mp4_passes(self):
        result = self.vo.inspect(self.ep)
        self.assertTrue(result['passed'], result['problems'])
        self.assertEqual([], self.vo.report_problems(self.ep, {'technical': result}))

    def test_changed_timeline_invalidates_receipt(self):
        (self.ep / 'timeline.json').write_text(json.dumps({'audio_end': 10, 'subs': []}))
        result = self.vo.inspect(self.ep)
        self.assertFalse(result['passed'])
        self.assertTrue(any('Đầu vào' in p for p in result['problems']))

    def test_landscape_file_cannot_pass_as_portrait(self):
        (self.ep / 'scenes.json').write_text(json.dumps({'fps': 30, 'format': '9:16', 'scenes': [{'duration_s': 1}]}))
        self.receipt()
        result = self.vo.inspect(self.ep)
        self.assertFalse(result['passed'])
        self.assertTrue(any('độ phân giải' in p for p in result['problems']))

    def test_corrupt_file_cannot_pass_even_with_new_receipt(self):
        (self.ep / 'render/final.mp4').write_bytes(b'broken mp4')
        self.receipt()
        self.assertFalse(self.vo.inspect(self.ep)['passed'])

    def test_wrong_fps_is_rejected(self):
        (self.ep / 'scenes.json').write_text(json.dumps({'fps': 24, 'scenes': [{'duration_s': 1}]}))
        self.receipt()
        result = self.vo.inspect(self.ep)
        self.assertFalse(result['passed'])
        self.assertTrue(any('30 fps' in p for p in result['problems']))

    def test_missing_timeline_is_rejected(self):
        (self.ep / 'timeline.json').unlink()
        self.receipt()
        self.assertFalse(self.vo.inspect(self.ep)['passed'])

    def test_missing_audio_is_rejected(self):
        import subprocess
        p = self.ep / 'render/no-audio.mp4'
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(self.good),
                        '-map', '0:v', '-c', 'copy', str(p)], check=True)
        p.replace(self.ep / 'render/final.mp4')
        self.receipt()
        self.assertFalse(self.vo.inspect(self.ep)['passed'])

    def test_passed_report_becomes_stale_on_source_change(self):
        result = self.vo.inspect(self.ep)
        self.assertTrue(result['passed'], result['problems'])
        (self.ep / 'timeline.json').write_text('{}')
        self.assertTrue(self.vo.report_problems(self.ep, {'technical': result}))

    def test_changed_voice_invalidates_report(self):
        result = self.vo.inspect(self.ep)
        self.assertTrue(result['passed'], result['problems'])
        (self.ep / 'audio/voice.mp3').write_bytes(b'new voice')
        self.assertTrue(self.vo.report_problems(self.ep, {'technical': result}))

    def test_wrong_audio_target_in_actual_command_is_rejected(self):
        p = self.ep / 'qa/encoding.json'
        receipt = json.loads(p.read_text())
        args = receipt['commands'][0]['args']
        args[args.index('-b:a') + 1] = '128k'
        p.write_text(json.dumps(receipt))
        result = self.vo.inspect(self.ep)
        self.assertFalse(result['passed'])
        self.assertTrue(any('bitrate' in s for s in result['problems']))


if __name__ == '__main__':
    unittest.main()
