"""Gộp tập kiểm thử từ Zalo, câu tổng hợp và câu tự soạn; kiểm tra hợp lệ rồi mới ghi eval/test_cases.json."""
import argparse
import collections
import json
import sys
from pathlib import Path

from eval.cases import validate_cases
from src.ingestion.legal_chunker import article_key, read_jsonl

LAWS_PATH = Path("data/raw/laws.json")
CHUNKS_PATH = Path("data/processed/chunks.jsonl")
ZALO_DIR = Path("data/external/zalo")
SYNTHETIC_PATH = Path("data/test_cases.json")
MANUAL_PATH = Path("eval/manual_cases.json")
EXCLUDE_PATH = Path("eval/zalo_exclude.txt")
OUT_PATH = Path("eval/test_cases.json")


def _law_ids(laws):
    return {info["number"].upper(): law_id for law_id, info in laws.items()}


def _case(case_id, question, law_id, gold, laws, source, reference_answer=""):
    return {"id": case_id, "question": question.strip(), "type": "situational", "domain": laws[law_id]["domain"],
            "event_date": None, "gold_citations": gold, "reference_answer": reference_answer, "source": source,
            "checked_by": None}


def zalo_cases(queries, qrels, laws, exclude=frozenset()):
    """Câu Zalo có mọi căn cứ thuộc kho, căn cứ ở cấp Điều. qrels: [(query_id, '91/2015/qh13+321')]."""
    ids = _law_ids(laws)
    refs = collections.defaultdict(list)
    for qid, corpus_id in qrels:
        number, article = corpus_id.rsplit("+", 1)
        refs[qid].append((ids.get(number.upper()), article))
    out = []
    for qid in sorted(refs):
        case_id = f"Z_{qid[:8]}"
        if qid not in queries or case_id in exclude or any(law_id is None for law_id, _ in refs[qid]):
            continue
        gold = sorted({f"{law_id}_Dieu{article}" for law_id, article in refs[qid]})
        out.append(_case(case_id, queries[qid], refs[qid][0][0], gold, laws, "zalo"))
    return out


def _synthetic_gold(law_id, ground_truth):
    clause_gold = [f"{law_id}_Dieu{a}_Khoan{k}" for a, _, k in (c.partition(".") for c in ground_truth["clauses"]) if k]
    covered = {article_key(g) for g in clause_gold}
    return clause_gold + [f"{law_id}_Dieu{a}" for a in ground_truth["articles"] if f"{law_id}_Dieu{a}" not in covered]


def synthetic_cases(raw_cases, laws):
    """Câu tổng hợp trong data/test_cases.json: ground_truth {articles: ["3"], clauses: ["3.1"]} → chunk_id."""
    ids = _law_ids(laws)
    out = []
    for t in raw_cases:
        law_id = ids.get(t["law_number"].upper())
        if law_id is None:
            raise ValueError(f"{t['id']}: số hiệu {t['law_number']} chưa có trong laws.json")
        out.append(_case(t["id"], t["question"], law_id, _synthetic_gold(law_id, t["ground_truth"]), laws,
                         "synthetic", t.get("expected_answer", "")))
    return out


def read_exclude(path):
    """Mã câu Zalo bị loại khi duyệt; mỗi dòng '<id>  # lý do'."""
    path = Path(path)
    if not path.exists():
        return frozenset()
    lines = (line.split("#", 1)[0].strip() for line in path.read_text(encoding="utf-8").splitlines())
    return frozenset(line for line in lines if line)


def load_manual(path):
    path = Path(path)
    if not path.exists():
        return []
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        sys.exit(f"{path} không phải JSON hợp lệ: {e}")


def load_zalo(zalo_dir):
    zalo_dir = Path(zalo_dir)
    queries = {r["_id"]: r["text"] for r in read_jsonl(zalo_dir / "queries.jsonl")}
    qrels = [(r["query-id"], r["corpus-id"]) for split in ("train", "test")
             for r in read_jsonl(zalo_dir / "qrels" / f"{split}.jsonl")]
    return queries, qrels


def main():
    argparse.ArgumentParser(description=__doc__).parse_args()
    laws = json.loads(LAWS_PATH.read_text(encoding="utf-8"))
    synthetic_raw = json.loads(SYNTHETIC_PATH.read_text(encoding="utf-8"))["test_cases"]
    cases = (zalo_cases(*load_zalo(ZALO_DIR), laws, read_exclude(EXCLUDE_PATH))
             + synthetic_cases(synthetic_raw, laws) + load_manual(MANUAL_PATH))
    errors = validate_cases(cases, [c["chunk_id"] for c in read_jsonl(CHUNKS_PATH)])
    if errors:
        print("\n".join(errors), file=sys.stderr)
        sys.exit(f"{len(errors)} lỗi, chưa ghi {OUT_PATH}")
    OUT_PATH.write_text(json.dumps(cases, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"đã ghi {len(cases)} câu vào {OUT_PATH}")
    for field in ("source", "type", "domain"):
        print(f"  {field}: {dict(collections.Counter(c[field] for c in cases))}")


if __name__ == "__main__":
    main()
