"""Tiến độ từng tập: status.yaml trong thư mục tập cho biết đang ở bước nào, ai giữ, đã duyệt gì. Người hoặc AI nhận việc đọc đây trước.
  python core/scripts/status.py                         bảng mọi kênh
  python core/scripts/status.py <tập> stage=render final=ok   cập nhật (khóa: stage, owner, brief, final, note, species, publish_date)
Bước: brief → script → audio → assets → build → render → qc → package → publish → done.
brief=ok chỉ nhận khi bảng fact đã qua qc_facts.py, không còn sai hoặc chưa xác minh. final=ok chỉ nhận khi QC bản render hiện tại không còn lỗi nặng.
brief=sep, final=sep: Sếp tự duyệt, bỏ qua kiểm tra. AI chỉ dùng khi Sếp nói rõ. species bị từ chối nếu trùng no_repeat_species tập gần nhất. publish_date dạng YYYY-MM-DD.
can_sep: cờ "cần Sếp" do máy ghi khi chạm luật dừng (precheck 4 vòng, render lại 2 lần, kịch bản 5 vòng); Sếp trả lời xong thì xóa: can_sep=
renders: số lần render đầy đủ (produce.py tự tăng). Tối đa 1 lần đầu + 2 lần render lại (MAX_RENDERS)."""
import hashlib, json, re, sys
from pathlib import Path
import yaml
from paths import ROOT

STAGES = ["brief", "script", "audio", "assets", "build", "render", "qc", "package", "publish", "done"]
DEFAULT = {"stage": "brief", "owner": "", "approved": {"brief": None, "final": None}, "species": [], "qc_rounds": 0, "publish": {}, "publish_date": "", "brief_sha": "", "final_sha": "", "note": "", "can_sep": "", "renders": 0}
MAX_RENDERS = 3  # render đầy đủ lần đầu + tối đa 2 lần render lại (core/roles/approver.md)


def read(ep):
    p = Path(ep) / "status.yaml"
    d = yaml.safe_load(p.read_text(encoding="utf-8")) if p.exists() else {}
    return {**DEFAULT, **(d or {})}


def write(ep, d):
    (Path(ep) / "status.yaml").write_text(yaml.safe_dump(d, allow_unicode=True, sort_keys=False), encoding="utf-8")


def facts_section(text):
    m = re.search(r"^## Fact và nguồn.*?(?=^## |\Z)", text, re.M | re.S)
    return m.group(0) if m else ""


def facts_sha(ep):
    return hashlib.sha256(facts_section((Path(ep) / "brief.md").read_text(encoding="utf-8")).encode()).hexdigest()


def facts_checked(ep):
    """Kết quả qc_facts.py mới nhất nếu nó khớp bảng fact hiện tại, ngược lại trả về None."""
    rows = [json.loads(p.read_text(encoding="utf-8")) for p in (Path(ep) / "qa").glob("facts_v*.json")]
    last = max(rows, key=lambda r: r["n"], default=None)
    return last if last and last["sha"] == facts_sha(ep) else None


def file_sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def require_brief(ep):
    """Cổng cho các bước sau brief: chưa duyệt, hoặc brief đã sửa sau khi duyệt, thì dừng."""
    d, brief = read(ep), Path(ep) / "brief.md"
    v = d["approved"]["brief"]
    if v == "sep":
        return
    if v != "ok":
        raise SystemExit(f"Brief của {Path(ep).name} chưa được duyệt. Vai trò approver duyệt: python core/scripts/status.py <tập> brief=ok")
    if not brief.exists() or d.get("brief_sha") != file_sha(brief):
        raise SystemExit(f"Brief của {Path(ep).name} đã đổi sau khi duyệt. Kiểm tra fact và duyệt lại.")
    r = facts_checked(ep)
    if not r or r["sai"] or r["chua_xac_minh"]:
        raise SystemExit(f"Kết quả kiểm tra fact mới nhất của {Path(ep).name} chưa đạt. Sửa brief, kiểm tra và duyệt lại.")


def final_stale(ep):
    """Đã chốt final=ok nhưng video hiện tại không phải bản đã chốt, hoặc đã mất."""
    d, video = read(ep), Path(ep) / "render" / "final.mp4"
    return d["approved"]["final"] == "ok" and (not video.exists() or d.get("final_sha") != file_sha(video))


QC_PASS = 9.0


def final_problems(ep):
    """Điều kiện máy kiểm được để chốt bản cuối. Trả về danh sách lỗi, rỗng là đủ điều kiện."""
    ep = Path(ep)
    video, rc = ep / "render" / "final.mp4", ep / "qa" / "render_check.json"
    if not video.exists():
        return ["chưa có render/final.mp4"]
    out = []
    if not rc.exists():
        out.append("chưa có qa/render_check.json")
    else:
        if rc.stat().st_mtime < video.stat().st_mtime:
            out.append("kiểm tra máy là của bản render cũ")
        try:
            import video_output
            report = json.loads(rc.read_text(encoding="utf-8"))
            out += video_output.report_problems(ep, report)
            if not isinstance(report, dict) or not isinstance(report.get('problems'), list):
                out.append('báo cáo kiểm tra máy thiếu danh sách lỗi')
            else:
                out += [f"kiểm tra máy: {p}" for p in report['problems']]
        except (OSError, ValueError, TypeError):
            out.append('không đọc được báo cáo kiểm tra máy')
    if not (ep / "thumb" / "thumbnail.jpg").exists():
        out.append("chưa có thumb/thumbnail.jpg")
    qcs = sorted((ep / "qa").glob("qc_v*.md"), key=lambda p: int(re.search(r"(\d+)", p.stem)[1]))
    text = qcs[-1].read_text(encoding="utf-8") if qcs else ""
    if f"- Video: {file_sha(video)}" not in text:
        return out + ["chưa có QC cho bản render hiện tại"]
    m = re.search(r"Lỗi nặng: (\d+)", text)
    if not m:
        out.append(f"không đọc được số lỗi nặng trong {qcs[-1].name}")
    elif int(m[1]):
        out.append(f"{qcs[-1].name} còn {m[1]} lỗi nặng")
    sc = re.search(r"Điểm khung hình trung bình: ([\d.]+)/10", text)
    if not sc or float(sc[1]) < QC_PASS:  # Sếp 2026-11-03: QC từ 9/10 mới đủ điều kiện gửi Sếp duyệt
        out.append(f"{qcs[-1].name} điểm {sc[1] if sc else '?'}/10, cần từ {QC_PASS}/10")
    return out


def set_values(ep, pairs):
    d = read(ep)
    for k, v in pairs:
        if k == "brief" and v == "ok":
            if not (Path(ep) / "brief.md").exists():
                raise SystemExit("Chưa có brief.md, không duyệt được.")
            r = facts_checked(ep)
            if not r:
                raise SystemExit("Bảng fact chưa được kiểm tra, hoặc đã sửa sau lần kiểm tra. Chạy: python core/scripts/qc_facts.py <tập>")
            if r["sai"] or r["chua_xac_minh"]:
                raise SystemExit(f"Còn {r['sai']} fact sai, {r['chua_xac_minh']} fact chưa xác minh, xem qa/facts_v{r['n']}.md. Sửa brief rồi kiểm tra lại, hết 3 lần thì báo Sếp.")
            d["brief_sha"] = file_sha(Path(ep) / "brief.md")
        if k == "final" and v == "ok":
            require_brief(ep)
            bad = final_problems(ep)
            if bad:
                raise SystemExit("Chưa chốt được bản cuối: " + "; ".join(bad))
            d["final_sha"] = file_sha(Path(ep) / "render" / "final.mp4")
        if k in ("brief", "final"):
            d["approved"][k] = v
        elif k == "species":
            d["species"] = [x.strip() for x in v.split(",") if x.strip()]
        elif k == "publish_date" and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", v):
            raise SystemExit(f"Ngày đăng phải có dạng YYYY-MM-DD: {v}")
        elif k == "stage" and v not in STAGES:
            raise SystemExit(f"Bước không hợp lệ: {v}. Dùng: {', '.join(STAGES)}")
        else:
            d[k] = v
    if any(k in ("species", "publish_date") for k, _ in pairs):
        clash = species_clash(ep, d["species"], d["publish_date"])
        if clash:
            raise SystemExit(f"Nhân vật trùng với các tập sát lịch đăng: {', '.join(clash)}. Chọn nhân vật hoặc ngày đăng khác.")
    write(ep, d)


def nearby_species(ep, n, date=""):
    """Nhân vật của N tập liền trước và N tập liền sau tập này theo lịch đăng, kể cả tập đang làm."""
    ep = Path(ep).resolve()
    key = str(date or ep.name[:10])  # chưa có ngày đăng thì theo ngày tạo trong tên tập
    rows = []
    for p in (ep.parents[1] / "episodes").glob("*/status.yaml"):
        if p.parent != ep:
            d = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
            rows.append((str(d.get("publish_date") or p.parent.name[:10]), p.parent.name, d.get("species", [])))
    rows.sort()
    out = []
    for row in [r for r in rows if r[0] <= key][-n:] + [r for r in rows if r[0] > key][:n]:
        out += row[2]
    return out


def species_clash(ep, names, date=""):
    ep = Path(ep).resolve()
    y = ep.parents[1] / "channel.yaml"
    n = (yaml.safe_load(y.read_text(encoding="utf-8")) or {}).get("no_repeat_species", 0) if y.exists() else 0
    used = {s.lower() for s in nearby_species(ep, n, date)} if n else set()
    return [s for s in names if s.lower() in used]


def has_voice(ep):
    """Có file giọng đọc thật, không tính voice.srt."""
    return any(p.suffix.lower() in (".mp3", ".wav", ".m4a") for p in (Path(ep) / "audio").glob("voice.*"))


def waiting(ep, d):
    """Việc tập này đang chờ ai duyệt hoặc gửi gì, rỗng nếu không chờ."""
    ep, stage, ok = Path(ep), d["stage"], d["approved"]
    if d.get("can_sep"):
        return "Sếp: " + str(d["can_sep"])
    if stage == "brief" and not ok["brief"] and (ep / "brief.md").exists() and facts_checked(ep):
        return "Claude duyệt brief"
    if stage == "audio" and not (has_voice(ep) and any((ep / "audio").glob("*.srt"))):
        return "Chạy gen_voice.py" if "tts:" in (ep.parent.parent / "channel.yaml").read_text(encoding="utf-8") else "Sếp gửi audio + srt"
    if stage == "qc" and any((ep / "qa").glob("qc_v*.md")):
        return "Claude quyết render lại"
    if stage == "publish" and not ok["final"]:
        return "Claude chốt bản cuối"
    if ok["final"] and stage not in ("publish", "done"):
        return "Đã chốt bản cuối: chuyển stage=publish"
    if stage == "publish" and not d.get("publish", {}).get("drive"):
        return "Chạy publish_clean (lên Drive)"
    if stage == "publish":
        return "Sếp đăng YouTube, xong ghi stage=done"
    if stage == "script":
        return "Viết kịch bản" if not (ep / "storyboard.md").exists() else "Chấm/sửa kịch bản (qc_script)"
    if stage == "assets":
        return "Tạo asset (gen_assets)"
    if stage == "build":
        return "Dựng cảnh (scene_dsl, validate)"
    if stage == "render":
        return "Render (produce)" if not (ep / "render" / "final.mp4").exists() else "QC video (qc_video)"
    if stage == "package":
        return "Meta + thumbnail (package)"
    return ""


if __name__ == "__main__":
    if len(sys.argv) > 2:
        set_values(sys.argv[1], [a.split("=", 1) for a in sys.argv[2:]])
        print(read(sys.argv[1]))
    else:
        print(f"{'KÊNH':<14}{'TẬP':<34}{'BƯỚC':<10}{'GIỮ':<10}{'NGÀY ĐĂNG':<12}{'DUYỆT':<13}ĐANG CHỜ")
        for ep in sorted(ROOT.glob("channels/*/episodes/*")):
            if ep.is_dir() and not ep.parent.parent.name.startswith("_"):
                d = read(ep)
                ok = ",".join(k for k, v in d["approved"].items() if v) or "-"
                print(f"{ep.parent.parent.name:<14}{ep.name[:32]:<34}{d['stage']:<10}{str(d['owner'])[:9]:<10}{str(d['publish_date']):<12}{ok:<13}{waiting(ep, d)}")
