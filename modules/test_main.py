"""Manual, local-only dev tool - NOT a pytest test despite the filename (no
test_* functions live here, so pytest collection is a harmless no-op).

Pick a folder, run every modules/ detector (quality.check_all, objects.detect_objects)
on each image file directly inside it, and show every photo - bounding boxes drawn
on it - scrollable in a second window.

Usage: python3 -m modules.test_main
"""
import os
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageDraw, ImageTk

from modules.objects import DetectionResult, detect_objects
from modules.quality import QualityResult, check_all

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
MAX_DISPLAY_WIDTH = 900
BOX_COLOR = "red"


def _image_files(folder: str) -> list[str]:
    return sorted(
        os.path.join(folder, name)
        for name in os.listdir(folder)
        if os.path.splitext(name)[1].lower() in IMAGE_EXTENSIONS
    )


def _annotate(image_path: str, result: DetectionResult) -> Image.Image:
    """The photo, resized to fit the results window, with every detection's
    bounding box and label drawn on top."""
    image = Image.open(image_path).convert("RGB")
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


def _caption(image_path: str, quality: QualityResult, result: DetectionResult) -> str:
    lines = [
        f"{os.path.basename(image_path)}  ({result.image_width}x{result.image_height})",
        f"blur {quality.blur:.0f}%  exposure {quality.exposure:+.0f}%  saturation {quality.saturation:.0f}%",
    ]
    if result.detections:
        lines.append(", ".join(f"{d.class_name} ({d.confidence:.0%})" for d in result.detections))
    else:
        lines.append("no objects detected")
    return "\n".join(lines)


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

    results = tk.Toplevel()
    results.title(f"Findings - {folder}")
    results.geometry("960x800")

    canvas, inner = _make_scrollable(results)
    photo_refs: list[ImageTk.PhotoImage] = []  # keep every PhotoImage alive
    results.photo_refs = photo_refs

    for path in paths:
        frame = tk.Frame(inner, pady=10)
        frame.pack(fill=tk.X)
        try:
            quality = check_all(path)
            result = detect_objects(path)
            photo = ImageTk.PhotoImage(_annotate(path, result))
            photo_refs.append(photo)

            tk.Label(frame, text=_caption(path, quality, result), justify=tk.LEFT, anchor="w").pack(fill=tk.X)
            tk.Label(frame, image=photo).pack()
        except Exception as exc:  # surfaced per-image, not a crash
            tk.Label(frame, text=f"{os.path.basename(path)}\nERROR: {exc}", fg="red", justify=tk.LEFT, anchor="w").pack(fill=tk.X)

        results.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox("all"))


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
