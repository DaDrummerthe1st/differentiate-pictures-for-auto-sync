"""Manual, local-only dev tool - NOT a pytest test despite the filename (no
test_* functions live here, so pytest collection is a harmless no-op).

Pick a folder, run every modules/ detector (quality.check_all, objects.detect_objects)
on each image file directly inside it, and show every photo - bounding boxes drawn
on it, plus its EXIF/quality/objects findings - scrollable in a second window,
paginated (IMAGES_PER_PAGE at a time) so a large folder doesn't exhaust the X
server rendering every photo simultaneously.

Usage: python3 -m modules.test_main
"""
import os
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import ExifTags, Image, ImageDraw, ImageOps, ImageTk

from modules.objects import DetectionResult, detect_objects
from modules.quality import QualityResult, check_all

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
MAX_DISPLAY_WIDTH = 900
BOX_COLOR = "red"
IMAGES_PER_PAGE = 20  # rendering every photo in a large folder at once exhausts
# the X server's pixmap allocation (hit 2026-09-04: BadAlloc on a 100-photo
# folder) - a page's worth is torn down before the next is built, so memory
# stays bounded regardless of folder size.


def _image_files(folder: str) -> list[str]:
    return sorted(
        os.path.join(folder, name)
        for name in os.listdir(folder)
        if os.path.splitext(name)[1].lower() in IMAGE_EXTENSIONS
    )


def _format_exposure_time(seconds: float) -> str:
    return f"{seconds:.1f}s" if seconds >= 1 else f"1/{round(1 / seconds)}s"


def _gps_to_decimal(dms: tuple, ref: str) -> float | None:
    if not dms or not ref:
        return None
    degrees, minutes, seconds = dms
    decimal = float(degrees) + float(minutes) / 60 + float(seconds) / 3600
    return -decimal if ref in ("S", "W") else decimal


def _exif_lines(image_path: str) -> list[str]:
    """Every commonly-useful EXIF field this photo actually has - camera,
    capture settings, capture date, GPS - as plain-language lines."""
    exif = Image.open(image_path).getexif()
    if not exif:
        return ["(none)"]

    base = {ExifTags.TAGS.get(tag_id, tag_id): value for tag_id, value in exif.items()}
    try:
        sub = {ExifTags.TAGS.get(tag_id, tag_id): value for tag_id, value in exif.get_ifd(ExifTags.IFD.Exif).items()}
    except Exception:
        sub = {}

    lines = []
    if "Make" in base or "Model" in base:
        lines.append(f"Camera: {base.get('Make', '')} {base.get('Model', '')}".strip())
    if "DateTimeOriginal" in sub:
        lines.append(f"Captured: {sub['DateTimeOriginal']}")
    settings = []
    if "ExposureTime" in sub:
        settings.append(_format_exposure_time(sub["ExposureTime"]))
    if "FNumber" in sub:
        settings.append(f"f/{sub['FNumber']}")
    if "ISOSpeedRatings" in sub:
        settings.append(f"ISO {sub['ISOSpeedRatings']}")
    if "FocalLength" in sub:
        settings.append(f"{sub['FocalLength']}mm")
    if settings:
        lines.append("Settings: " + "  ".join(settings))

    try:
        gps = exif.get_ifd(ExifTags.IFD.GPSInfo)
        lat = _gps_to_decimal(gps.get(2), gps.get(1))
        lon = _gps_to_decimal(gps.get(4), gps.get(3))
        if lat is not None and lon is not None:
            lines.append(f"GPS: {lat:.6f}, {lon:.6f}")
    except Exception:
        pass

    return lines or ["(none)"]


def _annotate(image_path: str, result: DetectionResult) -> Image.Image:
    """The photo, resized to fit the results window, with every detection's
    bounding box and label drawn on top."""
    # cv2.imread (modules/objects.py's detector) auto-rotates a JPEG per its
    # EXIF orientation tag, so detect_objects()'s bboxes are in that rotated,
    # upright coordinate space - PIL.Image.open does *not* auto-rotate, so
    # this must match that rotation explicitly or boxes land on the wrong
    # content entirely (found 2026-09-04: correct predictions, wrong places).
    image = ImageOps.exif_transpose(Image.open(image_path)).convert("RGB")
    assert (image.width, image.height) == (result.image_width, result.image_height), (
        f"annotated image size {image.size} doesn't match detection's "
        f"({result.image_width}, {result.image_height}) - EXIF rotation mismatch"
    )
    scale = min(1.0, MAX_DISPLAY_WIDTH / image.width)
    if scale < 1.0:
        image = image.resize((round(image.width * scale), round(image.height * scale)))

    draw = ImageDraw.Draw(image)
    for det in result.detections:
        x1, y1, x2, y2 = (round(v * scale) for v in det.bbox)
        draw.rectangle((x1, y1, x2, y2), outline=BOX_COLOR, width=2)
        label = f"{det.class_name} {det.confidence:.0%}"
        label_y = max(0, y1 - 14)
        draw.rectangle((x1, label_y, x1 + 7 * len(label), label_y + 14), fill=BOX_COLOR)
        draw.text((x1 + 2, label_y + 1), label, fill="white")
    return image


def _section(parent: tk.Widget, heading: str, lines: list[str]) -> None:
    tk.Label(parent, text=heading, font=("TkDefaultFont", 9, "bold"), anchor="w").pack(fill=tk.X)
    tk.Label(parent, text="\n".join(lines), justify=tk.LEFT, anchor="w").pack(fill=tk.X, padx=(10, 0))


def _add_entry(parent: tk.Widget, path: str, photo_refs: list) -> None:
    """One photo's full findings - EXIF, quality, objects, annotated image -
    inside its own bordered box, clearly separated from the next entry."""
    entry = tk.Frame(parent, relief=tk.GROOVE, borderwidth=2, padx=10, pady=8)
    entry.pack(fill=tk.X, pady=(0, 14))

    tk.Label(entry, text=os.path.basename(path), font=("TkDefaultFont", 11, "bold"), anchor="w").pack(fill=tk.X)

    try:
        quality = check_all(path)
        result = detect_objects(path)

        _section(entry, "EXIF", _exif_lines(path))
        _section(
            entry,
            "Quality",
            [f"blur {quality.blur:.1f}%   exposure {quality.exposure:+.1f}%   saturation {quality.saturation:.1f}%"],
        )
        if result.detections:
            object_lines = [f"{d.class_name}  {d.confidence:.0%}  bbox={d.bbox}" for d in result.detections]
        else:
            object_lines = ["(none detected)"]
        _section(entry, f"Objects ({result.image_width}x{result.image_height})", object_lines)

        photo = ImageTk.PhotoImage(_annotate(path, result))
        photo_refs.append(photo)
        tk.Label(entry, image=photo).pack(pady=(8, 0))
    except Exception as exc:  # surfaced per-image, not a crash
        tk.Label(entry, text=f"ERROR: {exc}", fg="red", justify=tk.LEFT, anchor="w").pack(fill=tk.X)


def _make_scrollable(parent: tk.Widget) -> tuple[tk.Canvas, tk.Frame]:
    """A vertically-scrollable area: mouse wheel works while hovering it, a
    scrollbar works always. Returns (canvas, inner_frame) - pack widgets into
    inner_frame."""
    outer = tk.Frame(parent)
    outer.pack(fill=tk.BOTH, expand=True)

    canvas = tk.Canvas(outer, highlightthickness=0)
    scrollbar = tk.Scrollbar(outer, orient=tk.VERTICAL, command=canvas.yview)
    canvas.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    inner = tk.Frame(canvas)
    canvas.create_window((0, 0), window=inner, anchor="nw")
    inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    def _scroll(delta: int) -> None:
        canvas.yview_scroll(delta, "units")

    def _bind_wheel(_event) -> None:
        canvas.bind_all("<MouseWheel>", lambda e: _scroll(int(-1 * (e.delta / 120))))
        canvas.bind_all("<Button-4>", lambda e: _scroll(-1))
        canvas.bind_all("<Button-5>", lambda e: _scroll(1))

    def _unbind_wheel(_event) -> None:
        canvas.unbind_all("<MouseWheel>")
        canvas.unbind_all("<Button-4>")
        canvas.unbind_all("<Button-5>")

    canvas.bind("<Enter>", _bind_wheel)
    canvas.bind("<Leave>", _unbind_wheel)

    return canvas, inner


def _show_results(folder: str) -> None:
    paths = _image_files(folder)
    if not paths:
        messagebox.showinfo("No images", f"No image files found directly in {folder}")
        return

    page_count = -(-len(paths) // IMAGES_PER_PAGE)  # ceil division
    state = {"page": 0}

    results = tk.Toplevel()
    results.title(f"Findings - {folder}")
    results.geometry("960x800")

    nav = tk.Frame(results, pady=6)
    nav.pack(fill=tk.X)
    prev_button = tk.Button(nav, text="< Prev")
    prev_button.pack(side=tk.LEFT, padx=10)
    page_label = tk.Label(nav, text="")
    page_label.pack(side=tk.LEFT, expand=True)
    next_button = tk.Button(nav, text="Next >")
    next_button.pack(side=tk.RIGHT, padx=10)

    canvas, inner = _make_scrollable(results)

    def _render_page() -> None:
        for widget in inner.winfo_children():
            widget.destroy()
        results.photo_refs = []  # drops every PhotoImage from the previous page

        page = state["page"]
        start = page * IMAGES_PER_PAGE
        for path in paths[start : start + IMAGES_PER_PAGE]:
            _add_entry(inner, path, results.photo_refs)
            results.update_idletasks()
            canvas.configure(scrollregion=canvas.bbox("all"))

        canvas.yview_moveto(0)
        page_label.config(text=f"{start + 1}-{min(start + IMAGES_PER_PAGE, len(paths))} of {len(paths)}   (page {page + 1}/{page_count})")
        prev_button.config(state=tk.NORMAL if page > 0 else tk.DISABLED)
        next_button.config(state=tk.NORMAL if page < page_count - 1 else tk.DISABLED)

    def _go(delta: int) -> None:
        state["page"] += delta
        _render_page()

    prev_button.config(command=lambda: _go(-1))
    next_button.config(command=lambda: _go(1))

    _render_page()


def _choose_folder(root: tk.Tk) -> None:
    folder = filedialog.askdirectory(title="Choose a folder of pictures")
    if folder:
        _show_results(folder)


def main() -> None:
    root = tk.Tk()
    root.title("modules/ detector dev tool")
    root.geometry("320x120")

    label = tk.Label(root, text="Run every modules/ detector on a folder of pictures.")
    label.pack(pady=10)

    button = tk.Button(root, text="Choose folder...", command=lambda: _choose_folder(root))
    button.pack(pady=10)

    root.mainloop()


if __name__ == "__main__":
    main()
