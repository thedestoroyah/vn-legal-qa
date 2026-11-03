from eval import plots


def test_retrieval_means_filters_source(tmp_path):
    csv = tmp_path / "r.csv"
    csv.write_text("config,id,source,hit5,recall10\n"
                   "a,1,zalo,1.0,1.0\na,2,zalo,0.0,0.5\na,3,synthetic,0.0,0.0\nb,1,zalo,1.0,0.0\n", encoding="utf-8")
    assert plots.retrieval_means(csv) == {"a": (0.5, 0.75), "b": (1.0, 0.0)}


def test_main_writes_four_figures(tmp_path):
    plots.main(["--out-dir", str(tmp_path)])
    for name in ("rq1", "rq2", "rq3_diff", "rq4"):
        assert (tmp_path / f"{name}.png").stat().st_size > 10_000
