from PIL import JpegImagePlugin

from app import main as app_main


def test_thumb_generation_calls_draft_before_resize(client, monkeypatch):
    """Image.draft() lets the JPEG decoder skip decoding at full source
    resolution when only a small thumbnail is needed - real memory/CPU
    savings per thumbnail, same output size/quality. Must be called
    before exif_transpose/thumbnail(), which would otherwise force a
    full decode first.

    draft() is overridden on JpegImageFile (the real, functional
    implementation) rather than defined on the base Image.Image class
    (which just has a no-op) - patch the concrete class actually used
    for real JPEGs, not the base class."""
    relpath = "AlbumA/1/pic1.jpg"
    cache_path = app_main.THUMB_CACHE / (relpath + ".jpg")
    cache_path.unlink(missing_ok=True)  # other tests may have cached this already

    calls = []
    real_draft = JpegImagePlugin.JpegImageFile.draft

    def spy_draft(self, mode, size):
        calls.append((mode, size))
        return real_draft(self, mode, size)

    monkeypatch.setattr(JpegImagePlugin.JpegImageFile, "draft", spy_draft)

    res = client.get("/thumb", params={"p": relpath})

    assert res.status_code == 200
    assert len(calls) == 1
    mode, size = calls[0]
    assert size == app_main.THUMB_SIZE
