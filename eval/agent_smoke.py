"""Chạy thử tác tử trên khoảng 10 câu thật (Sprint 3): in bảng tóm tắt, lưu đầu ra thô để đọc lỗi prompt.

python -m eval.agent_smoke [--config full]  -> eval/results/agent_smoke.jsonl, agent_smoke.md
"""
import argparse
import json
from pathlib import Path

from src.ingestion.legal_chunker import article_key, write_jsonl

CASES_PATH = Path("eval/test_cases.json")
OUT_DIR = Path("eval/results")
PICK = {"zalo": 3, "synthetic": 3, "manual": 4}
# dùng khi chưa có đủ câu manual của Hùng: phủ đủ nhánh direct, temporal, out_of_scope
EXTRA = [
    {"id": "X_direct", "source": "manual", "type": "direct", "question": "Điều 357 Bộ luật Dân sự 2015 quy định gì?",
     "gold_citations": ["BLDS2015_Dieu357"]},
    {"id": "X_temporal", "source": "manual", "type": "temporal",
     "question": "Năm 2022 tôi làm việc theo hợp đồng lao động xác định thời hạn 24 tháng, muốn nghỉ việc thì phải "
                 "báo trước bao nhiêu ngày?", "gold_citations": ["BLLD2019_Dieu35"]},
    {"id": "X_oos", "source": "manual", "type": "out_of_scope",
     "question": "Vượt đèn đỏ bằng xe máy bị phạt bao nhiêu tiền?", "gold_citations": []},
    {"id": "X_oos2", "source": "manual", "type": "out_of_scope",
     "question": "Hôm nay thời tiết ở Thành phố Hồ Chí Minh thế nào?", "gold_citations": []},
]


def pick_cases(cases):
    """Chọn câu chạy thử: 3 zalo + 3 synthetic + tối đa 4 manual (ưu tiên câu không phải situational).

    Thiếu câu manual thì bù bằng EXTRA. Trả danh sách case.
    """
    chosen = []
    for source, n in PICK.items():
        pool = [c for c in cases if c["source"] == source]
        if source == "manual":
            pool = sorted(pool, key=lambda c: c["type"] == "situational")
        chosen = chosen + pool[:n]
    n_manual = sum(c["source"] == "manual" for c in chosen)
    return chosen + EXTRA[:PICK["manual"] - n_manual]


def summarize(case, out):
    """Một dòng tóm tắt cho một câu: nhánh route, trích dẫn và căn cứ chuẩn ở cấp Điều, hit, số lượt LLM, tổng ms.

    `hit` là True khi trích dẫn trùng căn cứ chuẩn; với câu không có căn cứ (out_of_scope) thì là True khi tác tử từ chối.
    """
    cited = sorted({article_key(c["chunk_id"]) for c in out["citations"]})
    gold = sorted({article_key(g) for g in case["gold_citations"]})
    route = next((s["output"].get("route_type") for s in out["trace"] if s["node"] == "route"), "-")
    hit = bool(set(cited) & set(gold)) if gold else out["refused"]
    return {"id": case["id"], "type": case["type"], "route": route, "refused": out["refused"], "cited": cited,
            "gold": gold, "hit": hit, "llm_calls": sum(s["llm_calls"] for s in out["trace"]),
            "ms": sum(s["ms"] for s in out["trace"])}


def to_markdown(rows):
    """Bảng Markdown từ các dòng summarize, kèm tổng số đúng và mục trống 'Ghi chú lỗi prompt' để điền tay."""
    lines = ["| id | type | route | refused | cited | gold | hit | LLM | ms |", "|" + "---|" * 9]
    lines += [f"| {r['id']} | {r['type']} | {r['route']} | {r['refused']} | {', '.join(r['cited'])} | "
              f"{', '.join(r['gold'])} | {r['hit']} | {r['llm_calls']} | {r['ms']} |" for r in rows]
    hits = sum(r["hit"] for r in rows)
    return "\n".join(lines + ["", f"Đúng ở cấp Điều (hoặc từ chối đúng): {hits}/{len(rows)}", "", "## Ghi chú lỗi prompt", ""])


def main(argv=None):
    """Điểm vào CLI: chạy tác tử thật trên các câu được chọn, ghi .jsonl và .md vào eval/results."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="full")
    args = parser.parse_args(argv)
    from src.agent.run import load_agent  # nạp mô hình chậm: chỉ khi chạy thật
    agent = load_agent()
    results = []
    for case in pick_cases(json.loads(CASES_PATH.read_text(encoding="utf-8"))):
        out = agent.run(case["question"], args.config)
        row = summarize(case, out)
        print(row, flush=True)
        results = results + [{"case": case, "response": out, "row": row}]
    write_jsonl(OUT_DIR / "agent_smoke.jsonl", results)
    (OUT_DIR / "agent_smoke.md").write_text(to_markdown([r["row"] for r in results]), encoding="utf-8")


if __name__ == "__main__":
    main()
