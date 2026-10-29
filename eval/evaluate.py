"""Thực nghiệm truy xuất: RQ1 (phương pháp) và RQ2 (phân đoạn) trên các câu situational, tách theo nguồn."""
import argparse
import csv
import functools
import json
import sys
import time
from pathlib import Path

from eval.metrics import article_ranking, drm_at, hit_at, mean, mrr_at, recall_at
from src.ingestion.index import make_embedder
from src.ingestion.legal_chunker import article_key
from src.retrieval.retriever import MODES, load_retriever, make_reranker

CASES_PATH = Path("eval/test_cases.json")
RESULTS_DIR = Path("eval/results")
DEPTH = 30  # số chunk lấy về để dựng xếp hạng cấp Điều (một Điều có thể chiếm nhiều chunk)
CONFIGS = {
    "rq1": [("clause_header", mode) for mode in MODES],
    "rq2": [(variant, "hybrid_rerank") for variant in ("fixed", "article", "clause_plain", "clause_header")],
}
CLAUSE_METRICS = ("hit5_clause", "recall10_clause", "mrr10_clause")
METRICS = ("hit5", "recall10", "mrr10", "drm5", *CLAUSE_METRICS, "ms")


def eval_case(retriever, case, mode, clause_level):
    """Chạy truy xuất cho một câu và tính các chỉ số.

    Args:
        retriever: đối tượng có search(query, k, date, mode).
        case: câu hỏi trong eval/test_cases.json.
        mode: chế độ truy xuất.
        clause_level: True nếu biến thể có đơn vị Khoản; chỉ số Khoản chỉ tính khi mọi gold của câu ở cấp Khoản.

    Returns:
        dict gồm id, source, domain và các chỉ số hit5, recall10, mrr10, drm5, ms (+ chỉ số Khoản hoặc None).
    """
    start = time.perf_counter()
    chunks = retriever.search(case["question"], k=DEPTH, date=case["event_date"], mode=mode)
    ms = round((time.perf_counter() - start) * 1000)
    gold = case["gold_citations"]
    gold_articles = sorted({article_key(g) for g in gold})
    ranked = article_ranking(chunks)
    row = {"id": case["id"], "source": case["source"], "domain": case["domain"],
           "hit5": hit_at(ranked, gold_articles, 5), "recall10": recall_at(ranked, gold_articles, 10),
           "mrr10": mrr_at(ranked, gold_articles, 10), "drm5": drm_at(chunks, gold_articles, 5), "ms": ms}
    if not (clause_level and all("_Khoan" in g for g in gold)):
        return {**row, **dict.fromkeys(CLAUSE_METRICS)}
    ids = [c["chunk_id"] for c in chunks]
    return {**row, "hit5_clause": hit_at(ids, gold, 5), "recall10_clause": recall_at(ids, gold, 10),
            "mrr10_clause": mrr_at(ids, gold, 10)}


def run(rq, cases, get_retriever):
    """Chạy mọi (biến thể, chế độ) của `rq` trên danh sách câu; `get_retriever(variant)` trả Retriever. Trả list dòng kết quả, mỗi dòng có `config`."""
    return [{"config": f"{variant}/{mode}", **eval_case(get_retriever(variant), c, mode, variant.startswith("clause"))}
            for variant, mode in CONFIGS[rq] for c in cases]


def summarize(rows, metrics=METRICS):
    """Một dòng cho mỗi (config, source) và (config, 'all'); trung bình các cột `metrics`, bỏ qua giá trị None."""
    groups = {}
    for r in rows:
        for source in (r["source"], "all"):
            groups.setdefault((r["config"], source), []).append(r)
    return [{"config": cfg, "source": src, "n": len(rs), **{m: mean(r[m] for r in rs) for m in metrics}}
            for (cfg, src), rs in groups.items()]


def _fmt(value):
    return "–" if value is None else f"{value:.3f}"


def to_markdown(summary):
    """Bảng Markdown từ kết quả của summarize, một dòng cho mỗi (config, source)."""
    head = ["| config | source | n | Hit@5 | Recall@10 | MRR@10 | DRM@5 | Hit@5 (Khoản) | ms |",
            "|---|---|---|---|---|---|---|---|---|"]
    lines = [f"| {s['config']} | {s['source']} | {s['n']} | {_fmt(s['hit5'])} | {_fmt(s['recall10'])} | "
             f"{_fmt(s['mrr10'])} | {_fmt(s['drm5'])} | {_fmt(s['hit5_clause'])} | {s['ms']:.0f} |" for s in summary]
    return "\n".join(head + lines) + "\n"


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--rq", choices=sorted(CONFIGS), required=True)
    ap.add_argument("--limit", type=int, help="chỉ chạy N câu đầu để thử")
    args = ap.parse_args()
    cases = [c for c in json.loads(CASES_PATH.read_text(encoding="utf-8")) if c["type"] == "situational"]
    cases = cases[: args.limit]
    if not cases:
        sys.exit(f"không có câu situational trong {CASES_PATH}: chạy python -m eval.import_cases trước")
    embed, rerank = make_embedder(), make_reranker()
    get_retriever = functools.cache(lambda variant: load_retriever(variant, embed, rerank))
    rows = run(args.rq, cases, get_retriever)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    with (RESULTS_DIR / f"retrieval_{args.rq}.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    md = to_markdown(summarize(rows))
    (RESULTS_DIR / f"retrieval_{args.rq}.md").write_text(md, encoding="utf-8")
    print(md)


if __name__ == "__main__":
    main()
