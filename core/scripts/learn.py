"""Bộ nhớ học hỏi của hệ thống: knowledge/lessons.jsonl lưu trong git, AI nào, máy nào cũng đọc được. Cơ chế ở knowledge/README.md.
  learn.py add --scope global|<slug> --area asset|motion|script|thumbnail|map|ops|stats --rule "..." --evidence "..."
  learn.py brief --area asset [--channel slug] [--max 12]   in bài học liên quan cho AI đọc trước khi làm
  learn.py mark <id> da-chung-minh|bi-bac --evidence "..."  cập nhật trạng thái khi có bằng chứng
  learn.py review                                          liệt kê bài học đủ điều kiện đề xuất Sếp đưa vào tiêu chuẩn"""
import argparse, json, re
from datetime import date
from pathlib import Path
from paths import ROOT

FILE = ROOT / "knowledge" / "lessons.jsonl"
PROMOTE_HITS = 3  # gặp từ 3 lần hoặc đã chứng minh thì đề xuất đưa vào tiêu chuẩn, Sếp duyệt mới sửa
RANK = {"da-chung-minh": 0, "gia-thuyet": 1, "bi-bac": 2}


def read():
    if not FILE.exists():
        return []
    return [json.loads(l) for l in FILE.read_text(encoding="utf-8").splitlines() if l.strip()]


def write(rows):
    FILE.parent.mkdir(exist_ok=True)
    FILE.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")


def norm(s):
    return re.sub(r"\W+", " ", s.lower()).strip()


def add(scope, area, rule, evidence="", status="gia-thuyet"):
    """Trùng nội dung thì tăng số lần gặp và thêm bằng chứng, không tạo dòng mới."""
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


def record_defects(cfg, episode, area, defects):
    """QC gọi hàm này: lỗi nặng thành bài học cấp kênh để lần sau tránh, lặp nhiều thì được đề xuất lên tiêu chuẩn."""
    slug = Path(cfg["_dir"]).name
    for d in defects:
        if d:
            add(slug, area, f"Tránh lỗi: {d}", f"{episode} QC")


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
