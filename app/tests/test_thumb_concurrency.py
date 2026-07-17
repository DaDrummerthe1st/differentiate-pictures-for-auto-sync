import threading
import time

import pytest
from PIL import Image

from app import main as app_main


@pytest.fixture()
def slow_uncached_images(tmp_path, monkeypatch):
    """Two distinct, never-before-cached picture files, plus a real
    THUMB_CACHE dir so cache_path.parent.mkdir() has somewhere to write."""
    root = app_main.PHOTOS_ROOT / "ConcurrencyTest"
    root.mkdir(parents=True, exist_ok=True)
    paths = []
    for name in ("slow1.jpg", "slow2.jpg"):
        p = root / name
        Image.new("RGB", (40, 30), color="red").save(p, "JPEG")
        paths.append(f"ConcurrencyTest/{name}")
    return paths


def _patch_slow_open(monkeypatch, events, delay=0.15):
    """Make Image.open take `delay` seconds and record (relpath, start,
    end) into `events`, keyed by a per-call marker via closures over the
    real Image.open."""
    real_open = Image.open

    def slow_open(fp, *args, **kwargs):
        start = time.monotonic()
        time.sleep(delay)
        im = real_open(fp, *args, **kwargs)
        events.append((str(fp), start, time.monotonic()))
        return im

    monkeypatch.setattr(app_main.Image, "open", slow_open)


def test_concurrent_thumbnail_generation_is_limited(
    client, slow_uncached_images, monkeypatch
):
    # Force the semaphore down to 1 so overlap is impossible if the gate
    # works, and force Image.open to be slow enough that two threads
    # fired near-simultaneously would visibly overlap without the gate.
    monkeypatch.setattr(app_main, "_thumb_semaphore", threading.Semaphore(1))
    events: list[tuple[str, float, float]] = []
    _patch_slow_open(monkeypatch, events)

    results = {}

    def fetch(relpath):
        res = client.get("/thumb", params={"p": relpath})
        results[relpath] = res.status_code

    threads = [
        threading.Thread(target=fetch, args=(p,)) for p in slow_uncached_images
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert all(status == 200 for status in results.values())
    assert len(events) == 2
    # With the semaphore capped at 1, the second Image.open must not
    # start until the first one has finished - no overlap allowed.
    (_, start_a, end_a), (_, start_b, end_b) = sorted(events, key=lambda e: e[1])
    assert start_b >= end_a
