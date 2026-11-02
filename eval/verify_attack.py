"""Phép thử tiêm trích dẫn sai cho verify(b): đo verify bắt được bao nhiêu mã không hỗ trợ câu.

Lấy câu trả lời của cấu hình full (agent_rq3.jsonl), thay một mã trong một câu bằng một đoạn "mồi" không hỗ trợ
câu đó rồi đưa đoạn mồi vào ngữ cảnh (nên regex verify(a) không bắt được), gọi 1 lượt verify(b) và ghi lại:
mồi có bị gỡ không (phát hiện) và bao nhiêu mã khác bị gỡ theo (báo động nhầm). Hai loại mồi:
  same_context: đoạn đã truy xuất nhưng không được trích, khác Điều với mọi mã đã trích, không thuộc căn cứ chuẩn;
  other_law:    một Khoản bất kỳ của văn bản khác hẳn (khác cả họ luật, vd BLLĐ 2012 và 2019 coi là một họ).
Tập kiểm thử tự nhiên hiếm khi có trích dẫn sai nên không đo được giá trị của verify; phép thử này đo trực tiếp.

  python -m eval.verify_attack run [--n 50]
  python -m eval.verify_attack report
"""
import argparse
import json
import random
import re
import sys
from types import SimpleNamespace

import openai

from eval.agent_eval import CASES_PATH, RESULTS_DIR, SEED, append_jsonl, load_results
from eval.judge import load_contexts, used_contexts
from src.agent.nodes import _unsupported_pairs
from src.generation.citations import cited_ids, cited_sentences, sentences
from src.ingestion.legal_chunker import article_key, read_jsonl

OUT_PATH = RESULTS_DIR / "verify_attack.jsonl"
REPORT_PATH = RESULTS_DIR / "verify_attack.md"
KINDS = ("same_context", "other_law")


def inject(answer, index, old_id, new_id):
    """Thay `old_id` bằng `new_id` chỉ trong câu thứ `index` của sentences(answer); ValueError nếu câu không có mã đó."""
    parts = sentences(answer)
    # mã có thể đứng chung ngoặc "[A, B]"; chặn hai đầu để "..._Khoan1" không khớp vào "..._Khoan10"
    new, count = re.subn(rf"(?<![\w]){re.escape(old_id)}(?![\w])", new_id, parts[index])
    if not count:
        raise ValueError(f"không thấy {old_id} trong câu {index}")
    parts[index] = new
    return "".join(parts)


def same_context_distractor(answer, replaced, used, gold_articles, rng):
    """Đoạn mồi trong ngữ cảnh: chưa được trích, khác Điều với mọi mã đã trích, không thuộc Điều chuẩn; None nếu không có."""
    cited_articles = {article_key(c) for c in cited_ids(answer)} | {article_key(replaced)}
    pool = [c for c in used
            if article_key(c["chunk_id"]) not in cited_articles and article_key(c["chunk_id"]) not in gold_articles]
    return rng.choice(pool) if pool else None


def _family(law_id):
    return re.sub(r"\d+", "", law_id)


def other_law_distractor(answer, pool, rng):
    """Đoạn mồi từ văn bản khác họ với mọi văn bản đã trích; None nếu không có."""
    cited = {_family(c.split("_", 1)[0]) for c in cited_ids(answer)}
    candidates = [c for c in pool if _family(c["law_id"]) not in cited]
    return rng.choice(candidates) if candidates else None


def attack(llm, answer, used, index, replaced, distractor):
    """Tiêm `distractor` thay `replaced` ở câu `index`, chạy 1 lượt verify(b).

    Returns:
        {"detected": mồi bị gỡ, "false_alarms": số mã khác bị gỡ, "other_pairs": số cặp (câu, mã) khác}.
    """
    attacked = inject(answer, index, replaced, distractor["chunk_id"])
    by_id = {c["chunk_id"]: c for c in used} | {distractor["chunk_id"]: distractor}
    pairs = cited_sentences(attacked)
    verdicts = _unsupported_pairs(pairs, by_id, SimpleNamespace(llm=llm))
    detected = distractor["chunk_id"] in verdicts.get(index, set())
    flagged = sum(len(ids) for ids in verdicts.values())
    return {"detected": detected, "false_alarms": flagged - detected,
            "other_pairs": sum(len(ids) for _, _, ids in pairs) - 1}


def summary(rows):
    """{kind: (n, tỷ lệ phát hiện, tỷ lệ báo động nhầm hoặc None nếu không có cặp khác)}."""
    out = {}
    for kind in dict.fromkeys(r["kind"] for r in rows):
        rs = [r for r in rows if r["kind"] == kind]
        others = sum(r["other_pairs"] for r in rs)
        out[kind] = (len(rs), sum(r["detected"] for r in rs) / len(rs),
                     sum(r["false_alarms"] for r in rs) / others if others else None)
    return out


def _targets(n):
    """Mẫu cố định n câu trả lời của full còn ít nhất một câu có trích dẫn (theo SEED)."""
    cases = {c["id"]: c for c in json.loads(CASES_PATH.read_text(encoding="utf-8"))}
    results = load_results(RESULTS_DIR / "agent_rq3.jsonl")
    ids = sorted(cid for (cid, run), resp in results.items()
                 if run == "full" and not resp["refused"] and cited_sentences(resp["answer"]))
    return [(cases[cid], results[(cid, "full")]) for cid in sorted(random.Random(SEED).sample(ids, min(n, len(ids))))]


def cmd_run(args):
    """Chạy phép thử cho các câu chưa xong, ghi nối verify_attack.jsonl; hết quota thì dừng, chạy lại để tiếp."""
    from src.generation.llm import from_env
    llm = from_env("LLM")
    contexts = load_contexts()
    pool = list(contexts["clause"].values())
    done = {(r["id"], r["kind"]) for r in read_jsonl(OUT_PATH)} if OUT_PATH.exists() else set()
    for case, resp in _targets(args.n):
        used = used_contexts(resp, contexts)
        used_ids = {c["chunk_id"] for c in used}
        # chỉ chọn câu có mọi mã nằm trong ngữ cảnh dựng lại được
        pairs = [p for p in cited_sentences(resp["answer"]) if set(p[2]) <= used_ids]
        if not pairs:
            continue
        rng = random.Random(f"{SEED}-{case['id']}")
        index, _, ids = rng.choice(pairs)
        replaced = rng.choice(sorted(ids))
        gold = {article_key(g) for g in case["gold_citations"]}
        for kind in KINDS:
            if (case["id"], kind) in done:
                continue
            kind_rng = random.Random(f"{SEED}-{case['id']}-{kind}")
            distractor = (same_context_distractor(resp["answer"], replaced, used, gold, kind_rng) if kind == "same_context"
                          else other_law_distractor(resp["answer"], pool, kind_rng))
            if distractor is None:
                continue
            try:
                row = attack(llm, resp["answer"], used, index, replaced, distractor)
            except openai.RateLimitError:
                print(f"hết quota ở {case['id']}/{kind}: dừng; chạy lại cùng lệnh khi quota hồi", file=sys.stderr)
                return
            except openai.APIError as e:
                print(f"bỏ qua {case['id']}/{kind}: {e!r}"[:300], file=sys.stderr)
                continue
            append_jsonl(OUT_PATH, {"id": case["id"], "kind": kind, "sentence": index, "replaced": replaced,
                                    "distractor": distractor["chunk_id"], **row})
    print(f"{llm.calls} lượt gọi API thật")


def cmd_report(args):
    """In và ghi bảng tỷ lệ phát hiện / báo động nhầm theo loại mồi."""
    rows = read_jsonl(OUT_PATH)
    lines = ["| Loại mồi | n | Phát hiện (mồi bị gỡ) | Báo động nhầm (mã khác bị gỡ) |", "|---|---|---|---|"]
    for kind, (n, hit, fa) in summary(rows).items():
        lines.append(f"| {kind} | {n} | {hit:.3f} | {'–' if fa is None else f'{fa:.3f}'} |")
    lines += ["", "verify(a) (regex) không bắt được mồi nào vì mồi nằm trong ngữ cảnh: cấu hình no_verify và "
              "baseline có tỷ lệ phát hiện 0 theo cách dựng."]
    md = "\n".join(lines) + "\n"
    REPORT_PATH.write_text(md, encoding="utf-8")
    print(md)


def main(argv=None):
    """Điểm vào CLI."""
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    run = sub.add_parser("run")
    run.add_argument("--n", type=int, default=50, help="số câu trả lời của full đem tiêm mồi")
    run.set_defaults(fn=cmd_run)
    sub.add_parser("report").set_defaults(fn=cmd_report)
    args = parser.parse_args(argv)
    args.fn(args)


if __name__ == "__main__":
    main()
