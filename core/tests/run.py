"""Kiểm tra hệ thống, không cần API key. Dùng: python core/tests/run.py [--smoke] [--keep]
vi: khớp srt cho kết quả giống hệt mốc so sánh. ja: chữ hiển thị và chữ đọc tách đúng, badge theo nhãn kênh, thẻ dài bị loại.
en: tạo kênh mới từ mẫu, không sửa core, dựng 15 giây đầu đến cuối. --smoke chỉ chạy phần dựng, dùng cho doctor.py."""
import json, os, re, shutil, subprocess, sys, tempfile, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "core" / "scripts"
FIX = Path(__file__).resolve().parent / "fixtures"
sys.path.insert(0, str(SCRIPTS))
import channel as chan  # noqa: E402
import review  # noqa: E402
import status  # noqa: E402
import make_shared_assets  # noqa: E402
import video_output  # noqa: E402

PY = sys.executable
CHANNELS = ROOT / "channels"
fails = []


def run(*args, ok=(0,)):
    r = subprocess.run([str(a) for a in args], capture_output=True, text=True, cwd=ROOT)
    if r.returncode not in ok:
        raise RuntimeError(f"{' '.join(map(str, args))}\n{r.stdout[-1500:]}\n{r.stderr[-1500:]}")
    return r.stdout


def check(name, cond, detail=""):
    print(("  ✓ " if cond else "  ✗ ") + name + (f": {detail}" if detail and not cond else ""))
    if not cond:
        fails.append(name)


def temp_channel(slug, src=None, lang=None):
    d = CHANNELS / slug
    shutil.rmtree(d, ignore_errors=True)
    args = [PY, SCRIPTS / "new_channel.py", slug]
    if src:
        args += ["--from", src]
    if lang:
        args += ["--lang", lang]
    run(*args)
    ep = d / "episodes" / "t"
    (ep / "audio").mkdir(parents=True)
    return d, ep


def srt_time(t):
    ms = int(round(t * 1000))
    return f"{ms // 3600000:02}:{ms // 60000 % 60:02}:{ms // 1000 % 60:02},{ms % 1000:03}"


def fake_srt(sentences, per_sentence=2.2):
    """Tạo srt theo chữ đọc: giả lập file Sếp gửi."""
    out, t = [], 0.3
    for n, s in enumerate(sentences, 1):
        out.append(f"{n}\n{srt_time(t)} --> {srt_time(t + per_sentence)}\n{s}\n")
        t += per_sentence + 0.2
    return "\n".join(out)


def approve(ep):
    status.write(ep, {**status.read(ep), "approved": {"brief": "sep", "final": None}})


def test_gates(d):
    print("Cổng: brief, fact, nhân vật, ngày đăng, QC chạy tiếp")
    a, b = d / "episodes" / "a", d / "episodes" / "b"
    for ep in (a, b):
        (ep / "qa").mkdir(parents=True)
        (ep / "storyboard.md").write_text("# T\n\n## C\nCâu.\n", encoding="utf-8")
    brief = "# Brief\n\n## Fact và nguồn\n| Mệnh đề | Nguồn |\n|---|---|\n| X | Y |\n"
    (a / "brief.md").write_text(brief, encoding="utf-8")
    run(PY, SCRIPTS / "status.py", a, "brief=ok", ok=(1,))
    check("chưa kiểm tra fact thì không duyệt được brief", status.read(a)["approved"]["brief"] is None)
    run(PY, SCRIPTS / "export_narration.py", a, ok=(1,))
    check("chưa duyệt brief thì không xuất được script.md", not (a / "script.md").exists())
    (a / "qa" / "facts_v1.json").write_text(json.dumps({"n": 1, "sha": status.facts_sha(a), "sai": 1, "chua_xac_minh": 0}), encoding="utf-8")
    check("brief đã kiểm tra thì chờ Claude duyệt", status.waiting(a, status.read(a)) == "Claude duyệt brief")
    run(PY, SCRIPTS / "status.py", a, "brief=ok", ok=(1,))
    check("còn fact sai thì AI không duyệt được", status.read(a)["approved"]["brief"] is None)
    run(PY, SCRIPTS / "status.py", a, "brief=sep")
    check("Sếp vẫn duyệt thẳng được", status.read(a)["approved"]["brief"] == "sep")
    status.write(a, {**status.read(a), "approved": {"brief": None, "final": None}})
    (a / "qa" / "facts_v2.json").write_text(json.dumps({"n": 2, "sha": status.facts_sha(a), "sai": 0, "chua_xac_minh": 0}), encoding="utf-8")
    run(PY, SCRIPTS / "status.py", a, "brief=ok")
    run(PY, SCRIPTS / "export_narration.py", a)
    check("duyệt brief xong thì xuất được script.md", (a / "script.md").exists())
    late = a / "qa" / "facts_v3.json"
    late.write_text(json.dumps({"n": 3, "sha": status.facts_sha(a), "sai": 1, "chua_xac_minh": 0}), encoding="utf-8")
    run(PY, SCRIPTS / "export_narration.py", a, ok=(1,))
    check("lần kiểm tra fact mới báo sai thì các bước sau dừng", True)
    late.unlink()
    (a / "brief.md").write_text(brief + "| Z | W |\n", encoding="utf-8")
    run(PY, SCRIPTS / "status.py", a, "brief=ok", ok=(1,))
    check("sửa bảng fact thì phải kiểm tra lại", status.facts_checked(a) is None)
    (a / "script.md").unlink()
    run(PY, SCRIPTS / "export_narration.py", a, ok=(1,))
    check("sửa brief sau khi duyệt thì các bước sau dừng", not (a / "script.md").exists())
    run(PY, SCRIPTS / "status.py", b, "brief=ok", ok=(1,))
    check("thiếu brief.md thì không duyệt được", status.read(b)["approved"]["brief"] is None)
    run(PY, SCRIPTS / "status.py", a, "species=Megalodon")
    run(PY, SCRIPTS / "status.py", b, "species=megalodon", ok=(1,))
    check("không cho lặp nhân vật gần đây", status.read(b)["species"] == [])
    run(PY, SCRIPTS / "status.py", a, "species=Megalodon")
    check("tập được giữ nhân vật của chính nó", status.read(a)["species"] == ["Megalodon"])
    run(PY, SCRIPTS / "status.py", b, "stage=package", "publish_date=2026-11-05")
    run(PY, SCRIPTS / "status.py", b, "publish_date=mai", ok=(1,))
    check("có bước package và ngày đăng", status.read(b)["stage"] == "package" and status.read(b)["publish_date"] == "2026-11-05")
    run(PY, SCRIPTS / "status.py", b, "stage=audio")
    check("bảng tiến độ báo chờ audio", status.waiting(b, status.read(b)) == "Chạy gen_voice.py")
    (b / "audio").mkdir()
    (b / "audio" / "voice.srt").write_text("1", encoding="utf-8")
    check("chỉ có srt thì vẫn chờ audio", status.waiting(b, status.read(b)) == "Chạy gen_voice.py")
    (b / "audio" / "voice.mp3").write_bytes(b"x")
    check("đủ audio và srt thì hết chờ", status.waiting(b, status.read(b)) == "")
    approve(b)
    run(PY, SCRIPTS / "status.py", b, "final=ok", ok=(1,))
    check("chưa có video thì không chốt được", status.read(b)["approved"]["final"] is None)
    for sub in ("render", "thumb"):
        (b / sub).mkdir()
    (b / "render" / "final.mp4").write_bytes(b"x")
    (b / "thumb" / "thumbnail.jpg").write_bytes(b"x")
    (b / "qa" / "render_check.json").write_text(json.dumps({"problems": []}), encoding="utf-8")
    run(PY, SCRIPTS / "status.py", b, "final=ok", ok=(1,))
    check("chưa QC thì không chốt được", any("QC" in x for x in status.final_problems(b)))
    sha = status.file_sha(b / "render" / "final.mp4")
    # Cổng duyệt kiểm hiệu lực báo cáo; dữ liệu giả chỉ dùng cho kiểm thử cổng.
    (b / 'qa/render_check.json').write_text(json.dumps({'problems': [], 'technical': {
        'passed': True, 'problems': [], 'video_sha': sha,
        'config_sha': video_output.sha(video_output.CONFIG),
        'inputs': video_output.input_hashes(b)}}), encoding='utf-8')
    (b / "qa" / "qc_v1.md").write_text(f"- Video: {sha}\n- Điểm: 7/10. Lỗi nặng: 2. Tổng lỗi: 2.\n", encoding="utf-8")
    run(PY, SCRIPTS / "status.py", b, "final=ok", ok=(1,))
    check("còn lỗi nặng thì không chốt được", any("lỗi nặng" in x for x in status.final_problems(b)))
    (b / "qa" / "qc_v9.md").write_text(f"- Video: {sha}\n- Điểm khung hình trung bình: 8.6/10. Lỗi nặng: 0. Tổng lỗi: 1.\n", encoding="utf-8")
    run(PY, SCRIPTS / "status.py", b, "final=ok", ok=(1,))
    check("QC dưới 9/10 thì chưa đủ điều kiện gửi Sếp", any("9.0/10" in x for x in status.final_problems(b)))
    (b / "qa" / "qc_v10.md").write_text(f"- Video: {sha}\n- Điểm khung hình trung bình: 9.2/10. Lỗi nặng: 0. Tổng lỗi: 1.\n", encoding="utf-8")
    run(PY, SCRIPTS / "status.py", b, "final=ok")
    check("QC mới nhất sạch thì chốt được", status.read(b)["approved"]["final"] == "ok" and not status.final_stale(b))
    (b / "render" / "final.mp4").write_bytes(b"xy")
    check("render lại sau khi chốt thì mất hiệu lực", status.final_stale(b))
    check("QC của bản cũ không dùng được", any("QC" in x for x in status.final_problems(b)))
    status.write(a, {**status.read(a), "approved": {"brief": None, "final": None}})
    run(PY, SCRIPTS / "status.py", a, "final=ok", ok=(1,))
    check("brief chưa duyệt thì không chốt được bản cuối", status.read(a)["approved"]["final"] is None)
    cal = d / "_lich" / "episodes"
    for i, sp in enumerate(["X", "A", "B"], 1):
        (cal / f"e{i}").mkdir(parents=True)
        status.write(cal / f"e{i}", {**status.read(cal / f"e{i}"), "species": [sp], "publish_date": f"2030-01-0{i}"})
    (cal / "moi").mkdir()
    check("xét cả tập liền trước và liền sau theo lịch đăng", set(status.nearby_species(cal / "moi", 1, "2030-01-01")) == {"X", "A"} and status.nearby_species(cal / "moi", 1, "2030-01-09") == ["B"])
    ok_facts = {"facts": [{"id": "F1", "ket_qua": "dung"}, {"id": "F2", "ket_qua": "sai"}]}
    bad_facts = [{"facts": [{"id": "F1", "ket_qua": "dung"}, {"id": "F1", "ket_qua": "dung"}]}, {"facts": [{"id": "F1", "ket_qua": "dung"}, {"id": "F2", "ket_qua": "unknown"}]}, {}]

    def rejected(fn, value):
        try:
            fn(value)
        except ValueError:
            return True
        return False
    check("kết quả fact trùng, thiếu hoặc lạ bị từ chối", review.check_facts(ok_facts, ["F1", "F2"]) and all(rejected(lambda x: review.check_facts(x, ["F1", "F2"]), x) for x in bad_facts))
    calls, old = [], review.ask_images
    answers = ["không phải json", "{}", '{"score": 7, "issues": []}']
    review.ask_images = lambda *x, **k: (calls.append(1), answers[len(calls) - 1])[1]
    try:
        cache = a / "qa" / "c.json"
        r1 = review.ask_json_cached(cache, "k", "p", [])
        r2 = review.ask_json_cached(cache, "k", "p", [])
    finally:
        review.ask_images = old
    img_calls, old_post = [], review.router._post

    def down(*x, **k):
        img_calls.append("9router")
        raise RuntimeError("9router không sẵn sàng")
    review.router._post = down
    errors = []
    try:
        for _ in range(2):
            try:
                review.router.image("p")
            except RuntimeError as error:
                errors.append(str(error))
    finally:
        review.router._post = old_post
    check("ảnh lỗi trả nguyên tuyến, không tự đổi model/provider", len(errors) == 2 and img_calls == ["9router", "9router"], str(img_calls))
    old_ask, old_codex = review.router.ask, review._via_codex

    def no_key(*x, **k):
        raise SystemExit("Không tìm thấy key 9router đang bật")
    review.router.ask, review._via_codex = no_key, lambda *x, **k: "codex"
    try:
        check("không tìm được 9router thì chuyển Codex CLI", review.ask_text("p", provider="9router") == "codex" and review.ask_web("p", provider="9router") == "codex")
    finally:
        review.router.ask, review._via_codex = old_ask, old_codex
    check("QC hỏi lại khi JSON hỏng hoặc rỗng, chạy lại không tốn lượt", r1 == r2 == {"score": 7, "issues": []} and len(calls) == 3, str(calls))


def test_vi():
    print("Tiếng Việt: giống hệt mốc so sánh")
    d, ep = temp_channel("_t-vi", "tiensu-vn")
    shutil.copy(FIX / "vi" / "storyboard.md", ep)
    shutil.copy(FIX / "vi" / "voice.srt", ep / "audio")
    run(PY, SCRIPTS / "align_srt.py", ep)
    check("timeline.json không đổi", (ep / "timeline.json").read_bytes() == (FIX / "vi" / "timeline.expected.json").read_bytes())
    check("phụ đề không đổi", (ep / "audio" / "subs.clean.srt").read_bytes() == (FIX / "vi" / "subs.expected.srt").read_bytes())
    approve(ep)
    run(PY, SCRIPTS / "export_narration.py", ep)
    txt = (ep / "script.md").read_text(encoding="utf-8")
    check("script.md sạch ghi chú", "[" not in txt and "#" not in txt)
    check("script.md không còn chữ số", not re.search(r"\d", txt) and "sáu mươi sáu triệu" in txt, txt[:80])
    sp = chan.speech(chan.load(d))
    cases = {"105 loài": "một trăm lẻ năm loài", "21 con": "hai mươi mốt con", "1.005": "một nghìn không trăm lẻ năm", "2,5 lần": "hai phẩy năm lần", "3/4 số loài": "ba phần tư số loài", "12%": "mười hai phần trăm", "18-22 phút": "mười tám đến hai mươi hai phút"}
    check("đọc số tiếng Việt đúng", all(sp.speak(k) == v for k, v in cases.items()), str({k: sp.speak(k) for k in cases}))
    check("phụ đề vẫn hiện số", sp.display("66 triệu năm") == "66 triệu năm")
    rows = [{"round": 1, "gates_failed": 0, "fact_errors": 0, "pct": 90, "unnatural": 2}, {"round": 2, "gates_failed": 1, "fact_errors": 0, "pct": 99, "unnatural": 0}, {"round": 3, "gates_failed": 0, "fact_errors": 0, "pct": 85, "unnatural": 0}]
    check("QC chọn đúng vòng tốt nhất", review.best_round(rows)["round"] == 1)
    cap = d / "_qc_cap"
    (cap / "qa").mkdir(parents=True)
    (cap / "storyboard.md").write_text("đang sửa", encoding="utf-8")
    for r in rows + [{"round": 4, "gates_failed": 1, "fact_errors": 2, "pct": 70, "unnatural": 3}, {"round": 5, "gates_failed": 2, "fact_errors": 0, "pct": 60, "unnatural": 1}]:
        n = r["round"]
        (cap / "qa" / f"script_v{n}.json").write_text(json.dumps({**r, "n": n, "file": "storyboard.md"}), encoding="utf-8")
        (cap / "qa" / f"snapshot_v{n}.md").write_text(f"bản vòng {n}", encoding="utf-8")
    check("QC dừng sau 5 vòng", "Bản tốt nhất: vòng 1" in run(PY, SCRIPTS / "qc_script.py", cap, ok=(1,)))
    run(PY, SCRIPTS / "qc_script.py", cap, "--use-best")
    check("QC lấy lại bản tốt nhất", (cap / "storyboard.md").read_text(encoding="utf-8") == "bản vòng 1")
    test_gates(d)
    return d


def test_ja():
    print("Tiếng Nhật: chữ đọc, phụ đề, badge, thẻ")
    d, ep = temp_channel("_t-ja", "kodai-jp")
    approve(ep)
    story = "# テスト\n\n## 第1章\n[THẺ: 8500万年前] 8500万年前、穂別《ほべつ》の海に、地層《ちそう》が生まれました。\n[確定] 体長は7メートルです。\n[THẺ: これはとても長すぎるカードの文章なので表示しません] 証拠は、ここにあります。\n"
    (ep / "storyboard.md").write_text(story, encoding="utf-8")
    cfg = chan.load(d)
    sp = chan.speech(cfg)
    sents = ["8500万年前、穂別《ほべつ》の海に、地層《ちそう》が生まれました。", "体長は7メートルです。", "証拠は、ここにあります。"]
    (ep / "audio" / "voice.srt").write_text(fake_srt([sp.speak(s) for s in sents]), encoding="utf-8")
    run(PY, SCRIPTS / "align_srt.py", ep)
    doc = json.loads((ep / "timeline.json").read_text(encoding="utf-8"))
    check("khớp srt", doc["match"] >= 0.9, str(doc["match"]))
    check("phụ đề hiện kanji, không còn cách đọc", all("《" not in s["text"] for s in doc["subs"]) and "穂別" in "".join(s["text"] for s in doc["subs"]))
    check("phụ đề không quá dài", all(len(s["text"]) <= cfg["lang"]["subtitle"]["max"] + 6 for s in doc["subs"]))
    (ep / "scenes.json").write_text(json.dumps({"fps": 30, "scenes": [{"id": "a", "lines": [0, 2], "component": "KenBurns", "asset": "shared/textures/tang-da.jpg", "props": {}}]}), encoding="utf-8")
    out = run(PY, SCRIPTS / "align_srt.py", ep, "--apply")
    props = json.loads((ep / "scenes.json").read_text(encoding="utf-8"))["scenes"][0]["props"]
    check("badge nhận nhãn tiếng Nhật", any(b["type"] == "xac-nhan" for b in props.get("badges", [])))
    check("thẻ đúng giới hạn ký tự", props.get("cards", [{}])[0].get("text") == "8500万年前")
    run(PY, SCRIPTS / "export_narration.py", ep)
    txt = (ep / "script.md").read_text(encoding="utf-8")
    check("chữ đọc đã đổi sang kana", "ほべつ" in txt and "はっせんごひゃくまんねんまえ" in txt, txt[:80])
    check("bản TTS không còn kanji, số", not sp.leftover(txt), str(sp.leftover(txt)))
    srt = (ep / "script_srt.md").read_text(encoding="utf-8")
    check("2 bản chỉ có lời thuyết minh", all(not re.search(r"[\[\]#《》]|第1章|テスト|THẺ", x) for x in (txt, srt)), srt[:80])
    check("bản SRT là chữ thông thường", "8500万年前" in srt and "穂別" in srt and "《" not in srt and "[" not in srt, srt[:80])
    check("đọc biến âm đúng", sp.speak("4年前に1回") == "よねんまえにいっかい", sp.speak("4年前に1回"))
    check("bắt số thiếu cách đọc", sp.problems("3匹います") == ["3匹"] and not sp.problems("3匹《さんびき》います"))
    check("nhãn bản đồ theo ngôn ngữ kênh", cfg["lang"]["labels"]["biendong"] == "南シナ海")
    return d


EN = {"xac-nhan": "Confirmed", "co-the": "Likely", "tranh-cai": "Debated", "clock": "EARTH CALENDAR", "hoangsa": "Paracel Islands", "truongsa": "Spratly Islands",
      "biendong": "South China Sea", "ai_notice": "Created with AI assistance", "today": "Today"}


def test_en(seconds=15):
    print(f"Ngôn ngữ mới (tiếng Anh): kênh mới từ mẫu, dựng {seconds} giây, không sửa core")
    d, ep = temp_channel("_t-en", lang="en")
    y = d / "channel.yaml"
    s = y.read_text(encoding="utf-8").replace('locale: ""', "locale: en-US").replace('country: ""', "country: US")
    for k, v in EN.items():
        s = s.replace(f'    {k}: ""', f'    {k}: "{v}"')
    for tpl in ("{n} billion years ago", "{n} million years ago", "{n} years ago"):
        s = s.replace('tpl: ""', f'tpl: "{tpl}"', 1)
    y.write_text(s, encoding="utf-8")
    run(PY, SCRIPTS / "channel.py", d)
    (d / "theme.json").write_text(json.dumps({"palette": {"bg": "#16120e", "fg": "#f1e7d3", "accent": "#c8963e", "danger": "#b8402a"}, "font": "Be Vietnam Pro", "grain": 0.3, "vignette": 0.4, "subtitles": True,
                                              "badges": {"xac-nhan": "#4f7a65", "co-the": "#c8963e", "tranh-cai": "#a5482b"}}), encoding="utf-8")
    sents = ["Sixty six million years ago, nobody heard the blast.", "The ground began to shake within the hour.", "Then the sky started to rain fire.", "Today the rocks still remember it.", "This is how we know."]
    n = max(1, min(len(sents), round(seconds / 3)))
    sents = sents[:n]
    (ep / "storyboard.md").write_text("# Test\n\n## Part one\n[THẺ: 66 million years] " + sents[0] + "\n[Confirmed] " + "\n".join(sents[1:]) + "\n", encoding="utf-8")
    per = seconds / n - 0.2
    (ep / "audio" / "voice.srt").write_text(fake_srt(sents, per), encoding="utf-8")
    run("ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono", "-t", seconds, ep / "audio" / "voice.mp3")
    make_shared_assets.fixtures(ep / "assets")
    run(PY, SCRIPTS / "align_srt.py", ep)
    stage = {"cam": "in", "atmosphere": [{"type": "leaves", "n": 6}], "layers": [{"asset": "cutout.png", "x": 900, "y": 800, "h": 300, "shadow": {"w": 200}, "motion": "breathe"}]}
    scenes = [{"id": "a", "lines": [0, min(1, n - 1)], "component": "Stage", "asset": "bg.jpg", "props": stage}]
    if n > 2:
        scenes.append({"id": "b", "lines": [2, min(3, n - 1)], "component": "GeoMap", "transition": "cut", "props": {"center": [107, 15], "scale": 2300, "strata_in": {"dir": "up", "dur_s": 1.0, "from_asset": "bg.jpg", "counter": {"from_ma": 66}}}})
    if n > 4:
        scenes.append({"id": "c", "lines": [4, n - 1], "component": "Stage", "asset": "bg.jpg", "props": {**stage, "cam": "out"}})
    (ep / "scenes.json").write_text(json.dumps({"fps": 30, "scenes": scenes}), encoding="utf-8")
    run(PY, SCRIPTS / "align_srt.py", ep, "--apply")
    run(PY, SCRIPTS / "validate_scenes.py", ep / "scenes.json")
    lock = ROOT / ".render.lock"
    if not lock.exists():  # đang có render thật thì bỏ qua phần thử khóa
        lock.write_text(json.dumps({"pid": os.getpid(), "ep": "test", "started": "now"}))
        p = subprocess.Popen(["node", str(SCRIPTS / "render.mjs"), str(ep)], cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        time.sleep(4)
        check("render thứ hai tự đợi khóa", p.poll() is None and not (ep / "render").exists())
        lock.unlink()
        out, _ = p.communicate()
        check("hết khóa thì render tiếp", p.returncode == 0 and "Đang chờ" in out, out[-500:])
        check("render xong tự gỡ khóa", not lock.exists())
        lock.write_text(json.dumps({"pid": 999999, "ep": "test", "started": "now"}))  # khóa của tiến trình đã chết
    run("node", SCRIPTS / "render.mjs", ep)
    check("khóa cũ tự gỡ, có video", (ep / "render" / "final.mp4").exists() and not lock.exists())
    out = run(PY, SCRIPTS / "render_check.py", ep, ok=(0, 1))
    probs = json.loads((ep / "qa" / "render_check.json").read_text(encoding="utf-8"))["problems"]
    probs = [p for p in probs if "Đứng hình" not in p]  # ảnh test tĩnh, không tính
    check("kiểm tra máy không có lỗi", not probs, str(probs))
    if seconds >= 15:  # HT-11: render lại theo đoạn, dùng lại đoạn không đổi
        print("Render lại theo đoạn (render/chunks)")
        run("node", SCRIPTS / "render.mjs", ep, "--chunk-frames", "120")
        o2 = run("node", SCRIPTS / "render.mjs", ep, "--chunk-frames", "120")
        m2 = re.search(r"Đoạn: (\d+) render mới, (\d+) dùng lại", o2)
        check("render lần 2 không đổi gì thì dùng lại mọi đoạn", m2 and m2[1] == "0", o2[-300:])
        sp = ep / "scenes.json"
        doc = json.loads(sp.read_text(encoding="utf-8"))
        doc["scenes"][-1].setdefault("props", {})["label"] = "Đổi thử"
        sp.write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
        o3 = run("node", SCRIPTS / "render.mjs", ep, "--chunk-frames", "120")
        m3 = re.search(r"Đoạn: (\d+) render mới, (\d+) dùng lại", o3)
        check("sửa cảnh cuối chỉ render lại đoạn chạm cảnh đó", m3 and 1 <= int(m3[1]) and int(m3[2]) >= 1, o3[-300:])
        run(PY, SCRIPTS / "render_check.py", ep, ok=(0, 1))
        probs = [p for p in json.loads((ep / "qa" / "render_check.json").read_text(encoding="utf-8"))["problems"] if "Đứng hình" not in p]
        check("ghép đoạn dùng lại: kiểm tra máy không lỗi ở mối nối", not probs, str(probs))
    return d


def test_scene_rules():
    """HT-02: bộ mẫu dựng lại từ lỗi thật tập 1 phải bị máy bắt ≥ 90% theo cảnh, và validate dừng produce."""
    print("Luật máy trên bộ mẫu lỗi tập 1 (scenes_loi_tap1.json)")
    from PIL import Image
    exp = json.loads((FIX / "scenes_loi_tap1.expect.json").read_text(encoding="utf-8"))
    with tempfile.TemporaryDirectory() as tmp:
        ep = Path(tmp)
        for rel, (w, h) in exp["images"].items():
            f = ep / "assets" / rel
            f.parent.mkdir(parents=True, exist_ok=True)
            Image.new("RGBA" if rel.endswith(".png") else "RGB", (w, h), (90, 80, 70)).save(f)
        (ep / "qa").mkdir()
        (ep / "qa" / "zones.json").write_text(json.dumps(exp["zones"]), encoding="utf-8")
        (ep / "qa" / "asset_check.json").write_text(json.dumps(exp["asset_check"]), encoding="utf-8")
        shutil.copy(FIX / "scenes_loi_tap1.json", ep / "scenes.json")
        run(PY, SCRIPTS / "validate_scenes.py", ep / "scenes.json", "--report", ep / "rules.json", ok=(1,))
        hits = json.loads((ep / "rules.json").read_text(encoding="utf-8"))
        got = [sid for sid, rule in exp["expect"].items() if sid in hits.get(rule, [])]
        miss = sorted(set(exp["expect"]) - set(got))
        check("bắt ≥ 90% cảnh lỗi tập 1", len(got) >= 0.9 * len(exp["expect"]), f"{len(got)}/{len(exp['expect'])}, sót {miss}")
        sys.path.insert(0, str(SCRIPTS))
        import geo
        check("mẫu bản đồ vn, dna, asia đủ Hoàng Sa và Trường Sa", all(not geo.island_problems({"preset": k}) for k in geo.PRESETS))
        # HT-10: cảnh dựng bằng scene_dsl mặc định không vi phạm luật bản đồ, sương, dải phụ đề
        (ep / "scene_plan.py").write_text('st([0, 0], "bg", "in", ["leaves"], [L("nguoi", 900, 1000, 430)])\n'
                                          'gm([1, 1], "vn", [(103.41, 20.21, "Huà Phăn, Lào", 0.4)], highlight=["418"])\n'
                                          'gm([2, 2], "asia", [(84.68, 51.4, "Siberia", 0.4)])\n', encoding="utf-8")
        run(PY, SCRIPTS / "scene_dsl.py", ep)
        import scene_rules
        dd = json.loads((ep / "scenes.json").read_text(encoding="utf-8"))
        for x in dd["scenes"]:
            x["duration_s"] = 5
        bad = {k: v for k, v in scene_rules.check(dd, ep).items() if v and k in ("ban-do-dao", "ban-do-to-mau", "mist", "phu-de-layer")}
        check("scene_dsl mặc định đạt luật bản đồ, sương, dải phụ đề", not bad, str(bad))


def test_learn_lock(n=20):
    print("learn.py: nhiều tiến trình cùng thêm bài học")
    with tempfile.TemporaryDirectory() as tmp:
        env = {**os.environ, "LESSONS_FILE": str(Path(tmp) / "lessons.jsonl")}
        ps = [subprocess.Popen([PY, SCRIPTS / "learn.py", "add", "--scope", "global", "--area", "ops", "--rule", f"luật {i}"], cwd=ROOT, env=env, stdout=subprocess.DEVNULL)
              for i in range(n)]
        for q in ps:
            q.wait()
        rows = [json.loads(l) for l in (Path(tmp) / "lessons.jsonl").read_text(encoding="utf-8").splitlines()]
        check(f"đủ {n} bài học, id không trùng", len(rows) == n and len({r["id"] for r in rows}) == n, f"{len(rows)} dòng")


if __name__ == "__main__":
    made = []
    make_shared_assets.ensure()
    try:
        run(PY, ROOT / "core/tests/test_router_images.py")
        if "--smoke" in sys.argv:
            made.append(test_en(3))
        else:
            test_learn_lock()
            test_scene_rules()
            made += [test_vi(), test_ja(), test_en(15)]
    except RuntimeError as e:
        fails.append(str(e))
        print(e)
    finally:
        if "--keep" not in sys.argv:
            for s in ("_t-vi", "_t-ja", "_t-en"):
                shutil.rmtree(CHANNELS / s, ignore_errors=True)
    print("ĐẠT" if not fails else f"KHÔNG ĐẠT: {len(fails)} mục")
    sys.exit(1 if fails else 0)
