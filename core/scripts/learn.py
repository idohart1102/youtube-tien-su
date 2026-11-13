"""Bộ nhớ học hỏi của hệ thống: knowledge/lessons.jsonl lưu trong git, AI nào, máy nào cũng đọc được. Cơ chế ở knowledge/README.md.
  learn.py add --scope global|<slug> --area asset|motion|script|video|thumbnail|map|ops|stats --rule "..." --evidence "..."
  learn.py brief --area asset [--channel slug] [--max 12]   in bài học liên quan cho AI đọc trước khi làm
  learn.py mark <id> da-chung-minh|bi-bac --evidence "..."  cập nhật trạng thái khi có bằng chứng
  learn.py review                                          liệt kê bài học đủ điều kiện đề xuất Sếp đưa vào tiêu chuẩn"""
import argparse, fcntl, json, os, re
from contextlib import contextmanager
from datetime import date
from pathlib import Path
from paths import ROOT

FILE = Path(os.environ.get("LESSONS_FILE") or ROOT / "knowledge" / "lessons.jsonl")  # biến môi trường chỉ dùng khi test
PROMOTE_HITS = 3  # gặp từ 3 lần hoặc đã chứng minh thì đề xuất đưa vào tiêu chuẩn, Sếp duyệt mới sửa
RANK = {"da-chung-minh": 0, "gia-thuyet": 1, "bi-bac": 2}


def read():
    if not FILE.exists():
        return []
    return [json.loads(l) for l in FILE.read_text(encoding="utf-8").splitlines() if l.strip()]


@contextmanager
def locked():
    """Khóa đọc-sửa-ghi: nhiều thread/tiến trình cùng thêm bài học thì xếp hàng, không bài nào bị ghi đè mất."""
    FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(FILE.with_name("." + FILE.name + ".lock"), "w") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(f, fcntl.LOCK_UN)


def write(rows):
    """Ghi ra file tạm rồi thay, người đang đọc không bao giờ thấy file ghi dở."""
    FILE.parent.mkdir(parents=True, exist_ok=True)
    tmp = FILE.with_name(f".{FILE.name}.{os.getpid()}.tmp")
    tmp.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
    os.replace(tmp, FILE)


def norm(s):
    return re.sub(r"\W+", " ", s.lower()).strip()


def add(scope, area, rule, evidence="", status="gia-thuyet"):
    """Trùng nội dung thì tăng số lần gặp và thêm bằng chứng, không tạo dòng mới."""
    with locked():
        return _add(scope, area, rule, evidence, status)


def _add(scope, area, rule, evidence, status):
    rows = read()
    for r in rows:
        if r["scope"] == scope and r["area"] == area and norm(r["rule"]) == norm(rule):
            r["hits"] += 1
            if evidence and evidence not in r["evidence"]:
                r["evidence"].append(evidence)
            r["updated"] = date.today().isoformat()
            write(rows)
            return r["id"]
    nid = 1 + max([r["id"] for r in rows], default=0)
    rows.append({"id": nid, "scope": scope, "area": area, "rule": rule, "status": status, "hits": 1, "evidence": [evidence] if evidence else [],
                 "created": date.today().isoformat(), "updated": date.today().isoformat()})
    write(rows)
    return nid


# Loại lỗi video: QC gắn mỗi lỗi nặng vào 1 loại, bài học lưu theo loại (không theo mô tả riêng của tập) để đếm được số lần lặp.
VIDEO_DEFECTS = {
    "hinh-loi-lech": "Hình phải đổi theo đối tượng lời đọc đang nói; lời chuyển sang di cốt, địa điểm, nhân vật khác thì tách cảnh, không để ảnh cũ ở lại",
    "nhan-sai": "Nhãn, vòng khoanh, mũi tên đặt đúng vật và đúng vị trí lời đọc nói tới; xác minh ảnh là gì trước khi gắn nhãn",
    "lo-dap-an": "Hình không lộ đáp án trước câu trả lời; câu hỏi có đáp án về sau phải có [HỎI]/[ĐÁP] và hình đáp án ẩn",
    "chu-nho": "Sơ đồ và chữ trên hình phải đọc được trên điện thoại; sơ đồ khoa học thì phóng vào đúng vùng đang nói và đánh dấu",
    "chu-cat-mep": "Chữ, nhãn và sơ đồ nằm trọn trong vùng an toàn, không bị cắt mép",
    "chu-chong": "Nhãn không đè nhau; mỗi lúc chỉ một khối chữ, không trùng lúc với phụ đề",
    "chinh-ta": "Chữ trên màn hình đúng chính tả và đủ dấu theo ngôn ngữ kênh",
    "cutout-loi": "Cutout đủ thân, viền màu giấy theo nền (không trắng tinh), không bị cắt ngang, chân chạm đất, ánh sáng khớp nền",
    "anh-loi": "Ảnh không có chữ rác, sai giải phẫu, sai thời kỳ hoặc vật thể lạ",
    "ban-do": "Bản đồ đúng địa lý, có Hoàng Sa, Trường Sa khi có Việt Nam, không có đường yêu sách biển",
    "lap-nhip": "Không giữ một bố cục quá lâu hoặc lặp cùng ý máy nhiều cảnh liền",
    "mau": "Không phủ màu vàng, cam, sepia cả cảnh khi chủ đề không cần",
    "nguon-anh": "Ảnh thật có dòng nguồn và đúng nội dung đang nói",
}


def record_defects(cfg, episode, area, rules):
    """QC gọi hàm này với bài học đã khái quát (nội dung cổng hoặc luật của loại lỗi), không phải mã cổng hay mô tả riêng của tập.
    Trùng nội dung thì tăng số lần gặp; lặp nhiều thì được đề xuất lên tiêu chuẩn."""
    slug = Path(cfg["_dir"]).name
    for r in dict.fromkeys(filter(None, rules)):
        add(slug, area, r, f"{episode} QC")


def brief(area, channel=None, limit=12):
    rows = [r for r in read() if r["status"] != "bi-bac" and r["area"] == area and r["scope"] in ("global", channel)]
    rows.sort(key=lambda r: (RANK[r["status"]], -r["hits"]))
    return rows[:limit]


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("add")
    p.add_argument("--scope", required=True); p.add_argument("--area", required=True); p.add_argument("--rule", required=True); p.add_argument("--evidence", default="")
    p = sub.add_parser("brief")
    p.add_argument("--area", required=True); p.add_argument("--channel"); p.add_argument("--max", type=int, default=12)
    p = sub.add_parser("mark")
    p.add_argument("id", type=int); p.add_argument("status", choices=list(RANK)); p.add_argument("--evidence", default="")
    sub.add_parser("review")
    a = ap.parse_args()
    if a.cmd == "add":
        print("Bài học", add(a.scope, a.area, a.rule, a.evidence))
    elif a.cmd == "brief":
        for r in brief(a.area, a.channel, a.max):
            print(f"- [{r['status']}, gặp {r['hits']} lần] {r['rule']}")
    elif a.cmd == "mark":
        with locked():
            rows = read()
            for r in rows:
                if r["id"] == a.id:
                    r["status"] = a.status
                    r["updated"] = date.today().isoformat()
                    if a.evidence:
                        r["evidence"].append(a.evidence)
            write(rows)
    else:
        for r in read():
            if r["status"] == "da-chung-minh" or (r["status"] == "gia-thuyet" and r["hits"] >= PROMOTE_HITS):
                print(f"#{r['id']} [{r['scope']}/{r['area']}] {r['rule']} | bằng chứng: {'; '.join(r['evidence'][:3])}")
