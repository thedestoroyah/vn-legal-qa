"""Phân tích lỗi RQ3: chọn câu trả lời chưa tốt của một cấu hình, tạo phiếu gán nhãn, rồi đếm theo loại lỗi.

  python -m eval.error_analysis sheet [--run full] [--n 20] [--force]   # -> eval/results/errors_rq3.csv
  python -m eval.error_analysis report [--sheet eval/results/errors_rq3.csv]   # -> eval/results/errors_rq3.md

Nhãn (cột category, nhiều nhãn cách nhau bằng ";"):
  truy_xuat_sai_dieu      không lấy được Điều đúng, dù đúng văn bản
  sai_van_ban             lấy nhầm sang văn bản khác
  sai_phien_ban           đúng nội dung nhưng sai phiên bản theo thời gian (BLLĐ 2012 / 2019)
  trich_dan_khong_ho_tro  mã trích dẫn không chứa nội dung của câu gắn nó
  dinh_tuyen_sai          router xếp nhầm loại câu hoặc trích sai ngày sự việc
  tu_choi_nham            câu trong phạm vi nhưng bị từ chối
  dap_an_mau_tranh_cai    hệ thống trả lời hợp lý; đáp án mẫu hoặc căn cứ chuẩn mới có vấn đề
  tra_loi_thieu_y         trích đúng nhưng câu trả lời bỏ điều kiện, con số mà câu hỏi cần
  trich_them_lien_quan    trích thêm Điều có liên quan ngoài căn cứ chuẩn (chỉ số trừ điểm, không phải lỗi thật)
  bo_cham_qua_chat        bộ chấm trừ điểm vì thiếu chi tiết mà câu hỏi không hỏi tới (rubric R5)
  khong_phai_loi          chỉ số báo lỗi nhưng xem kỹ thì câu trả lời / từ chối là hợp lý
  khac                    loại khác, ghi rõ ở cột note
"""
import argparse
import csv
import json
import random
import sys
from collections import Counter
from pathlib import Path

from eval.agent_eval import CASES_PATH, RESULTS_DIR, SEED, load_judged, load_results, paths, report_rows

SHEET_PATH = RESULTS_DIR / "errors_rq3.csv"
REPORT_PATH = RESULTS_DIR / "errors_rq3.md"
CATEGORIES = ("truy_xuat_sai_dieu", "sai_van_ban", "sai_phien_ban", "trich_dan_khong_ho_tro", "dinh_tuyen_sai",
              "tu_choi_nham", "dap_an_mau_tranh_cai", "tra_loi_thieu_y", "trich_them_lien_quan", "bo_cham_qua_chat",
              "khong_phai_loi", "khac")
FIELDS = ("id", "source", "type", "question", "reference_answer", "gold", "cited", "route", "answer", "hints",
          "category", "note")


def _below(row, key, value):
    return row.get(key) is not None and row[key] < value


def hints(row):
    """Gợi ý loại lỗi từ chỉ số của một dòng report_rows (giá trị None bỏ qua); danh sách rỗng = không phải lỗi."""
    out = []
    if row.get("answered") == 0 and row.get("refusal_ok") == 0:
        out.append("tu_choi_nham")
    if row.get("answered") == 1 and row.get("refusal_ok") == 0:
        out.append("tra_loi_ngoai_pham_vi")
    if row.get("version_ok") == 0:
        out.append("sai_phien_ban")
    if _below(row, "recall", 1):
        out.append("thieu_can_cu")
    if _below(row, "precision", 1):
        out.append("trich_thua")
    if _below(row, "correctness", 1):
        out.append("sai_dap_an")
    return out


def pick(rows, n, seed=SEED):
    """Chọn n dòng lỗi: nhóm theo gợi ý đầu tiên, xáo từng nhóm theo seed, lấy xoay vòng để mọi nhóm đều có mặt."""
    groups = {}
    for r in rows:
        h = hints(r)
        if h:
            groups.setdefault(h[0], []).append(r)
    rng = random.Random(seed)
    queues = []
    for name in sorted(groups):
        members = list(groups[name])
        rng.shuffle(members)
        queues.append(members)
    out = []
    while len(out) < n and any(queues):
        for q in queues:
            if q and len(out) < n:
                out.append(q.pop(0))
    return out


def parse_categories(text):
    """Tách ô category ("a; B ") thành nhãn chuẩn hóa; ValueError nếu rỗng hoặc có nhãn ngoài CATEGORIES."""
    labels = [part.strip().lower() for part in (text or "").split(";") if part.strip()]
    if not labels:
        raise ValueError("chưa gán nhãn")
    unknown = [x for x in labels if x not in CATEGORIES]
    if unknown:
        raise ValueError(f"nhãn lạ {unknown}; nhãn hợp lệ: {', '.join(CATEGORIES)}")
    return labels


def count_categories(sheet_rows):
    """Đếm số câu theo nhãn trên phiếu đã điền; ValueError nêu id của dòng chưa gán hoặc gán sai nhãn."""
    counts = Counter()
    for row in sheet_rows:
        try:
            counts.update(parse_categories(row.get("category")))
        except ValueError as e:
            raise ValueError(f"{row.get('id')}: {e}") from None
    return counts


def _route(response):
    step = next((s for s in response["trace"] if s["node"] == "route"), None)
    return (step or {}).get("output", {}).get("route_type") or ""


def cmd_sheet(args):
    """Tạo phiếu gán nhãn; không ghi đè phiếu đã có (mất công gán nhãn) trừ khi có --force."""
    if SHEET_PATH.exists() and not args.force:
        sys.exit(f"{SHEET_PATH} đã có (có thể đã gán nhãn); thêm --force nếu muốn tạo lại")
    cases = json.loads(CASES_PATH.read_text(encoding="utf-8"))
    p = paths("rq3")
    results = {k: v for k, v in load_results(p["results"]).items() if k[1] == args.run}
    rows = report_rows(cases, results, load_judged(p["judge"], results))
    by_id = {c["id"]: c for c in cases}
    with SHEET_PATH.open("w", encoding="utf-8-sig", newline="") as f:  # BOM để Excel đọc đúng tiếng Việt
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        for row in pick(rows, args.n):
            case, resp = by_id[row["id"]], results[(row["id"], args.run)]
            writer.writerow({"id": row["id"], "source": case["source"], "type": case["type"],
                             "question": case["question"], "reference_answer": case.get("reference_answer") or "",
                             "gold": "; ".join(case["gold_citations"]),
                             "cited": "; ".join(c["chunk_id"] for c in resp["citations"]), "route": _route(resp),
                             "answer": resp["answer"], "hints": "; ".join(hints(row)), "category": "", "note": ""})
    print(f"ghi {SHEET_PATH}; điền cột category (xem docstring python -m eval.error_analysis -h) và note")


def cmd_report(args):
    """Đếm nhãn trên phiếu đã điền, ghi bảng errors_rq3.md (loại lỗi, số câu, tối đa 3 id ví dụ)."""
    with open(args.sheet, encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    counts = count_categories(rows)
    examples = {}
    for row in rows:
        for label in parse_categories(row["category"]):
            examples.setdefault(label, []).append(row["id"])
    lines = [f"Phân tích lỗi trên {len(rows)} câu. Một câu có thể thuộc nhiều loại.", "",
             "| Loại lỗi | Số câu | Ví dụ |", "|---|---|---|"]
    lines += [f"| {label} | {n} | {', '.join(examples[label][:3])} |" for label, n in counts.most_common()]
    md = "\n".join(lines) + "\n"
    REPORT_PATH.write_text(md, encoding="utf-8")
    print(md)


def main(argv=None):
    """Điểm vào CLI."""
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    sheet = sub.add_parser("sheet")
    sheet.add_argument("--run", default="full", help="cấu hình cần phân tích lỗi")
    sheet.add_argument("--n", type=int, default=20)
    sheet.add_argument("--force", action="store_true", help="ghi đè phiếu đã có")
    sheet.set_defaults(fn=cmd_sheet)
    report = sub.add_parser("report")
    report.add_argument("--sheet", default=str(SHEET_PATH))
    report.set_defaults(fn=cmd_report)
    args = parser.parse_args(argv)
    args.fn(args)


if __name__ == "__main__":
    main()
