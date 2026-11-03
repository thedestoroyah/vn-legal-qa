"""Vẽ 4 biểu đồ cho báo cáo từ kết quả đã lưu trong eval/results (không gọi LLM).

  python -m eval.plots [--out-dir docs/report/figures]   # -> rq1.png, rq2.png, rq3_diff.png, rq4.png
"""
import argparse
import csv
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # chạy không cần màn hình
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.ticker import FuncFormatter  # noqa: E402

from eval.agent_eval import (CASES_PATH, RESULTS_DIR, load_judged, load_results, paired_diff, paths,  # noqa: E402
                             report_rows, select_cases)

OUT_DIR = Path("docs/report/figures")
# bảng màu phân loại đã kiểm bằng validator của skill dataviz (CVD, độ sáng); aqua < 3:1 nên mọi cột đều ghi số
SERIES = ("#2a78d6", "#eb6834", "#1baf7a")
INK, MUTED, GRID = "#0b0b0b", "#52514e", "#e4e3df"
RQ1_LABELS = {"clause_header/bm25": "BM25", "clause_header/dense": "Dense", "clause_header/hybrid": "Hybrid (RRF)",
              "clause_header/hybrid_rerank": "Hybrid + rerank"}
RQ2_LABELS = {"fixed/hybrid_rerank": "Cố định 200 từ", "article/hybrid_rerank": "Điều",
              "clause_plain/hybrid_rerank": "Khoản", "clause_header/hybrid_rerank": "Khoản + tiêu đề"}
RQ3_METRICS = {"precision": "Citation P", "recall": "Citation R", "version_ok": "Đúng phiên bản",
               "correctness": "Correctness"}
RQ4_METRICS = {"recall": "Citation R", "version_ok": "Đúng phiên bản", "correctness": "Correctness"}
RQ4_LABELS = {"full@event": "event", "full@current": "current", "full@any": "any"}


def retrieval_means(csv_path, source="zalo"):
    """Trung bình (Hit@5, Recall@10) theo cấu hình trên các câu thuộc `source`, giữ thứ tự xuất hiện trong CSV."""
    sums = {}
    with open(csv_path, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["source"] == source:
                acc = sums.setdefault(row["config"], [0.0, 0.0, 0])
                acc[0] += float(row["hit5"])
                acc[1] += float(row["recall10"])
                acc[2] += 1
    return {cfg: (h / n, r / n) for cfg, (h, r, n) in sums.items()}


def _style(ax, value_axis):
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(MUTED)
    ax.tick_params(colors=MUTED, labelcolor=INK)
    # báo cáo tiếng Việt dùng dấu phẩy thập phân, giống nhãn số trên cột
    comma = FuncFormatter(lambda v, _: f"{v:g}".replace(".", ",").replace("-", "−"))
    getattr(ax, f"{value_axis}axis").set_major_formatter(comma)
    ax.set_axisbelow(True)


def _grouped_bars(groups, series, title, ylabel, out):
    """Cột ghép: groups = nhãn nhóm; series = {tên chuỗi: [giá trị theo nhóm]}; mỗi cột ghi giá trị."""
    fig, ax = plt.subplots(figsize=(7.5, 4))
    width = 0.8 / len(series)
    for i, (name, values) in enumerate(series.items()):
        xs = [g + (i - (len(series) - 1) / 2) * width for g in range(len(groups))]
        bars = ax.bar(xs, values, width * 0.92, label=name, color=SERIES[i])
        ax.bar_label(bars, labels=[f"{v:.3f}".replace(".", ",") for v in values], padding=2, fontsize=8, color=INK)
    ax.set_xticks(range(len(groups)), groups)
    ax.set_ylim(0, 1.08)
    ax.set_ylabel(ylabel, color=INK)
    ax.set_title(title, color=INK, loc="left")
    ax.yaxis.grid(True, color=GRID, linewidth=0.8)
    ax.legend(frameon=False, loc="upper left", ncols=len(series))
    _style(ax, "y")
    fig.tight_layout()
    fig.savefig(out, dpi=200)
    plt.close(fig)


def plot_retrieval(csv_path, labels, title, out):
    """Biểu đồ Hit@5 / Recall@10 theo cấu hình (chỉ câu Zalo), thứ tự theo `labels`."""
    means = retrieval_means(csv_path)
    keys = [k for k in labels if k in means]
    _grouped_bars([labels[k] for k in keys], {"Hit@5": [means[k][0] for k in keys],
                                              "Recall@10": [means[k][1] for k in keys]}, title, "Tỷ lệ", out)


def plot_diffs(rows, ref, out):
    """Biểu đồ khoảng: chênh lệch so với `ref` và khoảng bootstrap 95%, mỗi chỉ số một ô, mỗi cấu hình một hàng."""
    metrics = list(RQ3_METRICS)
    diffs = {m: paired_diff(rows, ref, m) for m in metrics}
    runs = list(diffs[metrics[0]])
    fig, axes = plt.subplots(1, len(metrics), figsize=(10, 3.2), sharey=True)
    for ax, m in zip(axes, metrics):
        for y, run in enumerate(runs):
            n, d, lo, hi = diffs[m][run]
            significant = lo > 0 or hi < 0
            ax.plot([lo, hi], [y, y], color=SERIES[0], linewidth=2, solid_capstyle="round")
            ax.plot(d, y, "o", markersize=7, color=SERIES[0] if significant else "white",
                    markeredgecolor=SERIES[0], markeredgewidth=2)
        ax.axvline(0, color=MUTED, linewidth=1)
        ax.set_title(RQ3_METRICS[m], color=INK, fontsize=10)
        ax.xaxis.grid(True, color=GRID, linewidth=0.8)
        _style(ax, "x")
    axes[0].set_yticks(range(len(runs)), runs)
    axes[0].invert_yaxis()
    n = len({r["id"] for r in rows})
    fig.suptitle(f"RQ3: chênh lệch so với {ref} trên {n} câu "
                 "(ghép cặp theo câu, bootstrap 95%; chấm đặc = khoảng không chứa 0)",
                 color=INK, fontsize=10, x=0.01, ha="left")
    fig.tight_layout()
    fig.savefig(out, dpi=200)
    plt.close(fig)


def _mean(values):
    values = [v for v in values if v is not None]
    return sum(values) / len(values) if values else 0.0


def plot_rq4(rows, out):
    """Cột ghép recall / đúng phiên bản / correctness theo 3 chính sách lọc hiệu lực."""
    policies = [p for p in RQ4_LABELS if any(r["config"] == p for r in rows)]
    n = len({r["id"] for r in rows})
    series = {label: [_mean(r[m] for r in rows if r["config"] == p) for p in policies]
              for m, label in RQ4_METRICS.items()}
    _grouped_bars([RQ4_LABELS[p] for p in policies], series,
                  f"RQ4: chính sách lọc hiệu lực trên {n} câu có mốc thời gian", "Tỷ lệ", out)


def _rows(rq, common):
    cases = select_cases(json.loads(CASES_PATH.read_text(encoding="utf-8")), rq)
    p = paths(rq)
    results = load_results(p["results"])
    return report_rows(cases, results, load_judged(p["judge"], results), common)


def main(argv=None):
    """Sinh rq1.png, rq2.png, rq3_diff.png, rq4.png vào --out-dir."""
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--out-dir", default=str(OUT_DIR))
    out = Path(parser.parse_args(argv).out_dir)
    out.mkdir(parents=True, exist_ok=True)
    plot_retrieval(RESULTS_DIR / "retrieval_rq1.csv", RQ1_LABELS, "RQ1: phương pháp truy xuất (77 câu Zalo)",
                   out / "rq1.png")
    plot_retrieval(RESULTS_DIR / "retrieval_rq2.csv", RQ2_LABELS, "RQ2: cách phân đoạn (77 câu Zalo, hybrid + rerank)",
                   out / "rq2.png")
    plot_diffs(_rows("rq3", common=True), "full", out / "rq3_diff.png")
    plot_rq4(_rows("rq4", common=False), out / "rq4.png")
    print(f"ghi 4 hình vào {out}")


if __name__ == "__main__":
    main()
