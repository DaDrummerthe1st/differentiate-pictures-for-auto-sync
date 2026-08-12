"""Real per-detector CPU-time benchmarking against actual home-server
hardware - see documentation/plans/tingly-humming-pudding.md Part B for
the full design/reasoning. Not run in CI, not run by any AI session:

    docker compose exec photo-viewer python -m app.benchmark_detector [--batch-size 100]

Walks every account's dpfas_media image files, POSTs each to the detector
service's /detect?include_timing=true, and appends one JSON-line batch
summary to BENCHMARK_LOG_PATH. Doesn't write to the tags table - pure
measurement, no side effects beyond that log file.
"""

import argparse
import json
import mimetypes
import os
import time
import urllib.request
import uuid
from datetime import datetime, timezone
from pathlib import Path

from app.main import MEDIA_ROOT_NAME, PHOTOS_LIBRARY_ROOT, PICTURE_EXTS

DETECTOR_URL = os.environ.get("DETECTOR_URL", "http://detector:8500/detect")
# Same analytics_data volume the SQLite DB lives on - survives container
# restarts, unlike a path inside the image itself.
BENCHMARK_LOG_PATH = Path(os.environ.get("BENCHMARK_LOG_PATH", "/data/benchmark.log"))

DETECTOR_KEYS = ("blur", "exposure", "monochrome", "face")


def summarize_batch(timings: list[dict]) -> dict:
    """Pure aggregation: a list of per-photo `timings` dicts (the exact
    shape /detect?include_timing=true returns under the "timings" key) ->
    one batch summary. peak_rss_kb is the max seen in the batch, not a
    sum - ru_maxrss is a cumulative peak since detector process start
    (mostly one-time model-load cost), so summing it across photos would
    double-count the same fixed cost repeatedly."""
    totals = {key: 0.0 for key in DETECTOR_KEYS}
    peak_rss_kb = 0
    for entry in timings:
        cpu_time_ms = entry["cpu_time_ms"]
        for key in DETECTOR_KEYS:
            totals[key] += cpu_time_ms.get(key, 0.0)
        peak_rss_kb = max(peak_rss_kb, entry.get("peak_rss_kb", 0))
    return {
        "photo_count": len(timings),
        "cpu_time_ms_total": totals,
        "peak_rss_kb": peak_rss_kb,
    }


def _iter_image_files(root: Path):
    for path in sorted(root.rglob("*")):
        if path.is_file() and path.suffix.lower() in PICTURE_EXTS:
            yield path


def _post_detect(path: Path) -> dict:
    boundary = uuid.uuid4().hex
    mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="file"; filename="{path.name}"\r\n'
        f"Content-Type: {mime}\r\n\r\n"
    ).encode() + path.read_bytes() + f"\r\n--{boundary}--\r\n".encode()
    req = urllib.request.Request(
        f"{DETECTOR_URL}?include_timing=true",
        data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        method="POST",
    )
    with urllib.request.urlopen(req) as res:
        return json.loads(res.read())


def _log_batch(summary: dict) -> None:
    line = json.dumps(summary)
    print(line)
    BENCHMARK_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with BENCHMARK_LOG_PATH.open("a") as f:
        f.write(line + "\n")


def run_benchmark(batch_size: int = 100) -> None:
    # A direct-filesystem CLI tool run by Joakim via docker exec, not an
    # HTTP endpoint - walks every account's photos together, since
    # per-user privacy scoping is an app/ (HTTP-layer) concern, not one
    # that applies to an admin running commands inside the container.
    root = PHOTOS_LIBRARY_ROOT / MEDIA_ROOT_NAME
    batch: list[dict] = []
    batch_start = time.monotonic()

    for path in _iter_image_files(root):
        result = _post_detect(path)
        batch.append(result["timings"])
        if len(batch) >= batch_size:
            summary = summarize_batch(batch)
            summary["wall_clock_ms"] = (time.monotonic() - batch_start) * 1000
            summary["ts"] = datetime.now(timezone.utc).isoformat()
            _log_batch(summary)
            batch = []
            batch_start = time.monotonic()

    if batch:
        summary = summarize_batch(batch)
        summary["wall_clock_ms"] = (time.monotonic() - batch_start) * 1000
        summary["ts"] = datetime.now(timezone.utc).isoformat()
        _log_batch(summary)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Real per-detector CPU-time benchmark - must be run against real hardware, "
        "no local stand-in produces meaningful numbers."
    )
    parser.add_argument("--batch-size", type=int, default=100)
    args = parser.parse_args()
    run_benchmark(batch_size=args.batch_size)


if __name__ == "__main__":
    main()
