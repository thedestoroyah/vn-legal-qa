"""Thực nghiệm sinh câu trả lời: RQ3 (5 cấu hình tác tử) và RQ4 (3 chính sách lọc hiệu lực).

Chạy dần qua nhiều ngày theo quota free tier: kết quả thô ghi nối vào JSONL, chạy lại thì bỏ qua câu đã xong.
  python -m eval.agent_eval run --rq rq3 --configs full baseline
  python -m eval.agent_eval run --rq rq3 --configs no_router no_grading no_verify --subset 60
  python -m eval.agent_eval run --rq rq4
  python -m eval.agent_eval report --rq rq3 [--subset 60]
  python -m eval.agent_eval report --rq rq3 --configs full baseline --common --ci --out eval/results/agent_rq3_full179.md
  python -m eval.agent_eval judge --rq rq3
  python -m eval.agent_eval sheet --rq rq3 --n 20
  python -m eval.agent_eval agree --rq rq3 --filled eval/results/grading_rq3_hung.csv
"""
import argparse
import csv
import json
import random
import sys
from pathlib import Path

import openai

from eval.evaluate import _fmt, summarize
from eval.judge import used_contexts
from eval.metrics import citation_pr, refusal_correct, version_correct
from src.ingestion.legal_chunker import article_key, read_jsonl

CASES_PATH = Path("eval/test_cases.json")
RESULTS_DIR = Path("eval/results")
SEED = 2026
RUNS = {
    # full trước: hết quota trong ngày thì vẫn đã có cấu hình chính
    "rq3": ["full", "baseline", "no_router", "no_grading", "no_verify"],
    "rq4": ["full@event", "full@current", "full@any"],
}
CASE_TYPES = {"rq3": None, "rq4": {"temporal"}}
METRICS = ("answered", "precision", "recall", "refusal_ok", "version_ok", "faithfulness", "correctness", "llm_calls", "ms")
CI_METRICS = ("answered", "precision", "recall", "refusal_ok", "version_ok", "correctness")


def paths(rq):
    """Đường dẫn các file kết quả của một rq."""
    return {"results": RESULTS_DIR / f"agent_{rq}.jsonl", "judge": RESULTS_DIR / f"agent_{rq}_judge.jsonl",
            "report": RESULTS_DIR / f"agent_{rq}.md", "sheet": RESULTS_DIR / f"grading_{rq}.csv"}


def parse_run(run):
    """Tên run '<config>[@<chính sách>]' -> (config, chính sách); không có '@' thì chính sách 'event'."""
    config, _, policy = run.partition("@")
    return config, policy or "event"


def stratified(cases, n, seed=SEED):
    """Mẫu khoảng n câu giữ tỷ lệ theo `source`, giữ thứ tự gốc; cùng seed thì cùng mẫu."""
    rng = random.Random(seed)
    groups = {}
    for c in cases:
        groups.setdefault(c["source"], []).append(c)
    picked = set()
    for _, group in sorted(groups.items()):
        k = min(len(group), round(n * len(group) / len(cases)))
        picked |= {c["id"] for c in rng.sample(group, k)}
    return [c for c in cases if c["id"] in picked]


def subset_cases(cases, n, path):
    """Mẫu phân tầng n câu, chốt danh sách id vào `path` ở lần dùng đầu tiên.

    Lần sau đọc lại file nên mẫu không đổi khi tập kiểm thử thêm/sửa câu: các cấu hình chạy ở những ngày khác
    nhau vẫn so trên cùng một tập câu. Xóa file để lấy mẫu lại.
    """
    path = Path(path)
    if path.exists():
        ids = set(json.loads(path.read_text(encoding="utf-8")))
        return [c for c in cases if c["id"] in ids]
    picked = stratified(cases, n)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps([c["id"] for c in picked], ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return picked


def select_cases(cases, rq, subset=None, limit=None, subset_path=None):
    """Các câu dùng cho `rq`: rq4 chỉ câu temporal; `subset` = mẫu phân tầng (chốt vào `subset_path` nếu có);
    `limit` = N câu đầu (chạy thử)."""
    types = CASE_TYPES[rq]
    pool = [c for c in cases if types is None or c["type"] in types]
    if subset:
        pool = subset_cases(pool, subset, subset_path) if subset_path else stratified(pool, subset)
    return pool[:limit] if limit else pool


def append_jsonl(path, row):
    """Ghi nối một dòng JSON (tạo thư mục cha nếu cần); ghi từng dòng để dừng giữa chừng không mất kết quả."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def load_results(path):
    """{(id, run): response} của các dòng chạy thành công; dòng lỗi bị bỏ qua, trùng thì lấy dòng sau."""
    path = Path(path)
    rows = read_jsonl(path) if path.exists() else []
    return {(r["id"], r["run"]): r["response"] for r in rows if "error" not in r}


def run_agent(agent, cases, runs, out_path):
    """Chạy tác tử cho mọi (run, câu) chưa xong, ghi nối từng dòng vào `out_path`.

    Args:
        agent: có run(question, config, date_policy).
        cases: các câu cần chạy.
        runs: tên run, xem parse_run.
        out_path: file JSONL kết quả thô.

    Returns:
        Số dòng mới ghi. Hết quota (openai.RateLimitError sau khi SDK đã thử lại) thì dừng sớm, không ném lỗi;
        lỗi API khác ghi thành dòng {"error"} để lần chạy sau thử lại.
    """
    done = set(load_results(out_path))
    written = 0
    for run in runs:
        config, policy = parse_run(run)
        for case in cases:
            if (case["id"], run) in done:
                continue
            try:
                row = {"id": case["id"], "run": run, "response": agent.run(case["question"], config, policy)}
            except openai.RateLimitError:
                print(f"hết quota ở {run}/{case['id']}: dừng; chạy lại cùng lệnh khi quota hồi", file=sys.stderr)
                return written
            except openai.APIError as e:
                row = {"id": case["id"], "run": run, "error": repr(e)[:300]}
            append_jsonl(out_path, row)
            written += 1
    return written


def score(case, run, response):
    """Chỉ số của một câu trả lời ở cấp Điều; None = không áp dụng (vd recall của câu out_of_scope)."""
    cited = sorted({article_key(c["chunk_id"]) for c in response["citations"]})
    gold = sorted({article_key(g) for g in case["gold_citations"]})
    precision, recall = citation_pr(cited, gold)
    version = version_correct(case, [c.split("_", 1)[0] for c in cited])
    return {"id": case["id"], "config": run, "source": case["source"], "type": case["type"],
            "answered": float(not response["refused"]), "precision": precision, "recall": recall, "refusal_ok": float(refusal_correct(case, response)),
            "version_ok": None if version is None else float(version),
            "llm_calls": sum(s["llm_calls"] for s in response["trace"]), "ms": sum(s["ms"] for s in response["trace"])}


def report_rows(cases, results, judged, common=False):
    """Dòng chỉ số cho mọi kết quả thuộc `cases`, gộp điểm bộ chấm (`judged`: {(id, run): {...}}) nếu có.

    common=True: chỉ giữ câu đã có kết quả ở mọi run, để so các cấu hình trên cùng một tập câu.
    """
    by_id = {c["id"]: c for c in cases}
    keys = [(cid, run) for cid, run in results if cid in by_id]  # bỏ câu ngoài tập đang báo cáo (vd ngoài subset)
    if common:
        runs = {run for _, run in keys}
        shared = {cid for cid, _ in keys if all((cid, r) in results for r in runs)}
        keys = [(cid, run) for cid, run in keys if cid in shared]
    rows = []
    for cid, run in keys:
        resp = results[(cid, run)]
        verdict = judged.get((cid, run), {})
        rows.append({**score(by_id[cid], run, resp), "faithfulness": verdict.get("faithfulness"),
                     "correctness": verdict.get("correctness")})
    return rows


def to_markdown(summary):
    """Bảng Markdown: một dòng cho mỗi (run, source), kèm cảnh báo khi các run phủ số câu khác nhau và cách đọc."""
    head = ["| run | source | n | Trả lời | Citation P | Citation R | Từ chối đúng | Đúng phiên bản | Faithfulness | "
            "Correctness | LLM/câu | ms/câu |", "|" + "---|" * 12]
    summary = sorted(summary, key=lambda s: (s["config"], s["source"] != "all", s["source"]))
    lines = [f"| {s['config']} | {s['source']} | {s['n']} | " + " | ".join(_fmt(s[m]) for m in METRICS[:7])
             + f" | {_fmt(s['llm_calls'])} | {_fmt(s['ms'])} |" for s in summary]
    sizes = {s["config"]: s["n"] for s in summary if s["source"] == "all"}
    notes = ["", "Cách đọc: mỗi chỉ số là trung bình trên các câu áp dụng được (bỏ giá trị trống): Citation P chỉ tính "
             "câu có trích dẫn; Faithfulness chỉ tính câu được trả lời; Correctness chỉ tính câu có đáp án mẫu (không "
             "có câu Zalo). Đọc kèm cột \"Trả lời\". Cột ms có cache LLM, không dùng để so latency (đo riêng bằng "
             "`run --cache-dir <thư mục mới>`)."]
    if len(set(sizes.values())) > 1:
        notes.append(f"Cảnh báo: các run phủ số câu khác nhau {sizes}; chạy `report --common` để so trên cùng tập câu.")
    return "\n".join(head + lines + notes) + "\n"

def paired_diff(rows, ref, metric, n_boot=2000, seed=SEED):
    """Chênh lệch trung bình (run − ref) của `metric`, ghép cặp theo câu, kèm khoảng tin cậy bootstrap 95%.

    Ghép cặp vì các run chạy trên cùng câu: so trực tiếp từng câu loại được độ khó khác nhau giữa các câu, hẹp
    hơn nhiều so với so hai trung bình độc lập.

    Args:
        rows: dòng của report_rows ({"id", "config", <metric>}).
        ref: run làm mốc (vd "full").
        metric: tên cột; câu có giá trị None ở một trong hai run bị bỏ.

    Returns:
        {run: (n cặp, chênh lệch, cận dưới, cận trên)} cho mọi run khác ref có ít nhất một cặp.
    """
    values = {(r["id"], r["config"]): r[metric] for r in rows}
    base = {cid: v for (cid, run), v in values.items() if run == ref and v is not None}
    rng = random.Random(seed)
    out = {}
    for run in sorted({run for _, run in values} - {ref}):
        diffs = [values[(cid, run)] - v for cid, v in base.items() if values.get((cid, run)) is not None]
        if not diffs:
            continue
        boots = sorted(sum(rng.choices(diffs, k=len(diffs))) / len(diffs) for _ in range(n_boot))
        out[run] = (len(diffs), sum(diffs) / len(diffs), boots[int(0.025 * n_boot)], boots[int(0.975 * n_boot) - 1])
    return out


def diff_markdown(rows, ref):
    """Bảng Markdown chênh lệch so với `ref` (xem paired_diff) cho CI_METRICS; '*' = khoảng tin cậy không chứa 0."""
    diffs = {m: paired_diff(rows, ref, m) for m in CI_METRICS}
    runs = sorted({run for d in diffs.values() for run in d})
    head = [f"Chênh lệch so với `{ref}` (ghép cặp theo câu, bootstrap 95%; * = khoảng không chứa 0; n = số câu "
            "của cột Recall):", "", "| run | n | " + " | ".join(CI_METRICS) + " |", "|" + "---|" * (len(CI_METRICS) + 2)]
    lines = []
    for run in runs:
        n = diffs["recall"].get(run, (0,))[0]
        cells = []
        for m in CI_METRICS:
            if run not in diffs[m]:
                cells.append("–")
                continue
            k, d, lo, hi = diffs[m][run]
            # cột ít câu hơn hẳn (vd version_ok chỉ có câu temporal) phải ghi n để khỏi đọc nhầm dấu *
            cells.append(f"{d:.3f}{'*' if lo > 0 or hi < 0 else ''} [{lo:.3f}; {hi:.3f}]" + (f" (n={k})" if k != n else ""))
        lines.append(f"| {run} | {n} | " + " | ".join(cells) + " |")
    return "\n".join(head + lines) + "\n"


def judge_results(llm, cases, results, out_path, contexts):
    """Chấm mọi kết quả thuộc `cases` chưa có trong `out_path`, ghi nối từng dòng; hết quota thì dừng sớm.

    Returns:
        Số dòng mới ghi.
    """
    from eval.judge import judge
    out_path = Path(out_path)
    done = {(r["id"], r["run"]) for r in read_jsonl(out_path)} if out_path.exists() else set()
    by_id = {c["id"]: c for c in cases}
    written = 0
    for (cid, run), resp in results.items():
        if (cid, run) in done or cid not in by_id:
            continue
        try:
            verdict = judge(llm, by_id[cid], resp, contexts)
        except openai.RateLimitError:
            print(f"bộ chấm hết quota ở {run}/{cid}: dừng; chạy lại khi quota hồi", file=sys.stderr)
            return written
        except openai.APIError as e:
            print(f"bỏ qua {run}/{cid}: {e!r}"[:300], file=sys.stderr)
            continue
        append_jsonl(out_path, {"id": cid, "run": run, **verdict})
        written += 1
    return written


SHEET_FIELDS = ("id", "question", "answer", "contexts", "reference_answer", "faithfulness", "correctness", "note")


def write_sheet(cases, results, run, n, path, contexts):
    """Phiếu chấm tay CSV (UTF-8 BOM để Excel đọc đúng tiếng Việt): mẫu cố định n câu đã được trả lời của `run`.

    Không kèm điểm của bộ chấm LLM, để người chấm không bị ảnh hưởng. Trả số câu đã ghi.
    """
    from src.generation.prompts import format_context
    answered = [c for c in cases if (c["id"], run) in results and not results[(c["id"], run)]["refused"]]
    rows = []
    for c in stratified(answered, n) if len(answered) > n else answered:
        resp = results[(c["id"], run)]
        used = used_contexts(resp, contexts)
        rows.append({"id": c["id"], "question": c["question"], "answer": resp["answer"],
                     "contexts": format_context(used), "reference_answer": c.get("reference_answer", ""),
                     "faithfulness": "", "correctness": "", "note": ""})
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=SHEET_FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    return len(rows)


def _human_score(text):
    text = (text or "").strip().replace(",", ".")  # người chấm có thể gõ 0,5
    return float(text) if text else None


def agreement(sheet_rows, judged, run):
    """Tỷ lệ khớp điểm giữa người chấm (phiếu đã điền) và bộ chấm LLM, theo từng tiêu chí.

    Returns:
        {tiêu chí: (tỷ lệ khớp hoặc None, số cặp được so)}; ô trống hoặc điểm LLM None thì không tính.
    """
    out = {}
    for metric in ("faithfulness", "correctness"):
        pairs = [(_human_score(r[metric]), judged[(r["id"], run)][metric]) for r in sheet_rows
                 if _human_score(r[metric]) is not None and judged.get((r["id"], run), {}).get(metric) is not None]
        out[metric] = (sum(a == b for a, b in pairs) / len(pairs) if pairs else None, len(pairs))
    return out


def _cases(args):
    subset_path = RESULTS_DIR / f"subset_{args.rq}_{args.subset}.json" if args.subset else None
    return select_cases(json.loads(CASES_PATH.read_text(encoding="utf-8")), args.rq, args.subset, args.limit,
                        subset_path)


def cmd_run(args):
    """Lệnh `run`: chạy tác tử thật cho các run của rq, ghi nối vào agent_<rq>.jsonl."""
    from src.agent.run import load_agent  # nạp mô hình chậm: chỉ khi chạy thật
    agent = load_agent(cache_dir=args.cache_dir)
    runs = args.configs or RUNS[args.rq]
    written = run_agent(agent, _cases(args), runs, paths(args.rq)["results"])
    print(f"ghi {written} dòng; {agent.deps.llm.calls} lượt gọi API thật ({agent.deps.llm.requests} lượt logic)")


def cmd_report(args):
    """Lệnh `report`: tính chỉ số (gộp điểm bộ chấm nếu có), in và ghi bảng (mặc định agent_<rq>.md, hoặc --out).

    --configs chỉ giữ các run đã nêu; --ci thêm bảng chênh lệch so với run đầu tiên của rq có mặt (vd full).
    """
    p = paths(args.rq)
    judged = {(r["id"], r["run"]): r for r in read_jsonl(p["judge"])} if p["judge"].exists() else {}
    results = {k: v for k, v in load_results(p["results"]).items() if not args.configs or k[1] in args.configs}
    rows = report_rows(_cases(args), results, judged, args.common)
    md = to_markdown(summarize(rows, METRICS))
    if args.ci:
        present = {r["config"] for r in rows}
        ref = next((run for run in RUNS[args.rq] if run in present), None)
        md += "\n" + diff_markdown(rows, ref) if ref else ""
    Path(args.out or p["report"]).write_text(md, encoding="utf-8")
    print(md)


def cmd_judge(args):
    """Lệnh `judge`: chấm bằng LLM bộ chấm (JUDGE_*) các kết quả chưa chấm, ghi nối vào agent_<rq>_judge.jsonl."""
    from eval.judge import load_contexts
    from src.generation.llm import from_env
    llm = from_env("JUDGE")
    p = paths(args.rq)
    written = judge_results(llm, _cases(args), load_results(p["results"]), p["judge"], load_contexts())
    print(f"chấm {written} câu; {llm.calls} lượt gọi API thật")


def cmd_sheet(args):
    """Lệnh `sheet`: tạo phiếu chấm tay CSV grading_<rq>.csv cho một run."""
    from eval.judge import load_contexts
    p = paths(args.rq)
    n = write_sheet(_cases(args), load_results(p["results"]), args.run, args.n, p["sheet"], load_contexts())
    print(f"ghi {n} câu vào {p['sheet']}; mỗi người chép một bản rồi điền cột faithfulness, correctness (0 / 0,5 / 1)")


def cmd_agree(args):
    """Lệnh `agree`: in tỷ lệ khớp giữa phiếu chấm tay đã điền (--filled) và bộ chấm LLM."""
    p = paths(args.rq)
    judged = {(r["id"], r["run"]): r for r in read_jsonl(p["judge"])}
    with open(args.filled, encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    for metric, (rate, n) in agreement(rows, judged, args.run).items():
        print(f"{metric}: khớp {_fmt(rate)} trên {n} câu")


def build_parser():
    """Parser CLI với các lệnh con run, report, judge, sheet, agree (chung --rq, --subset, --limit)."""
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    for name, fn in (("run", cmd_run), ("report", cmd_report), ("judge", cmd_judge), ("sheet", cmd_sheet),
                     ("agree", cmd_agree)):
        p = sub.add_parser(name)
        p.add_argument("--rq", choices=sorted(RUNS), required=True)
        p.add_argument("--subset", type=int, help="mẫu phân tầng khoảng N câu (cố định theo SEED)")
        p.add_argument("--limit", type=int, help="chỉ N câu đầu (chạy thử)")
        p.set_defaults(fn=fn)
        if name == "run":
            p.add_argument("--configs", nargs="+", help="tên run, vd full baseline full@any (mặc định: mọi run của rq)")
            p.add_argument("--cache-dir", help="thư mục cache LLM; đặt thư mục mới để đo latency không dùng cache")
        if name == "report":
            p.add_argument("--common", action="store_true", help="chỉ tính câu đã có kết quả ở mọi run")
            p.add_argument("--configs", nargs="+", help="chỉ báo cáo các run này")
            p.add_argument("--ci", action="store_true", help="thêm bảng chênh lệch so với full, bootstrap 95%%")
            p.add_argument("--out", help="file bảng Markdown (mặc định agent_<rq>.md)")
        if name in ("sheet", "agree"):
            p.add_argument("--run", default="full", help="run cần chấm tay")
        if name == "sheet":
            p.add_argument("--n", type=int, default=20)
        if name == "agree":
            p.add_argument("--filled", required=True, help="phiếu CSV đã điền điểm")
    return parser


def main(argv=None):
    """Điểm vào CLI."""
    args = build_parser().parse_args(argv)
    args.fn(args)


if __name__ == "__main__":
    main()
