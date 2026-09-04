from app.benchmark_detector import summarize_batch


def test_summarize_batch_sums_cpu_time_across_photos():
    timings = [
        {"cpu_time_ms": {"blur": 1.0, "exposure": 2.0, "monochrome": 0.5, "face": 10.0}, "peak_rss_kb": 400000},
        {"cpu_time_ms": {"blur": 1.5, "exposure": 2.5, "monochrome": 0.5, "face": 12.0}, "peak_rss_kb": 410000},
    ]

    summary = summarize_batch(timings)

    assert summary["photo_count"] == 2
    assert summary["cpu_time_ms_total"] == {"blur": 2.5, "exposure": 4.5, "monochrome": 1.0, "face": 22.0}


def test_summarize_batch_reports_max_peak_rss_not_sum():
    # ru_maxrss is a cumulative peak since process start (mostly one-time
    # model-load cost) - summing it across photos in a batch would
    # double-count that fixed cost, so the aggregate must be a max.
    timings = [
        {"cpu_time_ms": {"blur": 1.0, "exposure": 1.0, "monochrome": 1.0, "face": 1.0}, "peak_rss_kb": 300000},
        {"cpu_time_ms": {"blur": 1.0, "exposure": 1.0, "monochrome": 1.0, "face": 1.0}, "peak_rss_kb": 410000},
        {"cpu_time_ms": {"blur": 1.0, "exposure": 1.0, "monochrome": 1.0, "face": 1.0}, "peak_rss_kb": 350000},
    ]

    summary = summarize_batch(timings)

    assert summary["peak_rss_kb"] == 410000


def test_summarize_batch_of_empty_list():
    summary = summarize_batch([])

    assert summary["photo_count"] == 0
    assert summary["peak_rss_kb"] == 0
    assert summary["cpu_time_ms_total"] == {"blur": 0.0, "exposure": 0.0, "monochrome": 0.0, "face": 0.0}
