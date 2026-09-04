"""Manual, local-only dev tool - NOT a pytest test despite the filename (no
test_* functions live here, so pytest collection is a harmless no-op).

Pick a folder, run every modules/ detector (quality.check_all, objects.detect_objects)
on each image file directly inside it, and show the findings in a second window.

Usage: python3 -m modules.test_main
"""
import os
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext

from modules.objects import detect_objects
from modules.quality import check_all

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def _image_files(folder: str) -> list[str]:
    return sorted(
        os.path.join(folder, name)
        for name in os.listdir(folder)
        if os.path.splitext(name)[1].lower() in IMAGE_EXTENSIONS
    )


def _describe(image_path: str) -> str:
    quality = check_all(image_path)
    result = detect_objects(image_path)
    lines = [
        os.path.basename(image_path),
        f"  {result.image_width}x{result.image_height}",
        f"  blur {quality.blur:.1f}%  exposure {quality.exposure:+.1f}%  saturation {quality.saturation:.1f}%",
    ]
    if result.detections:
        for det in result.detections:
            lines.append(f"  {det.class_name} ({det.confidence:.0%}) at {det.bbox}")
    else:
        lines.append("  no objects detected")
    return "\n".join(lines)


def _show_results(folder: str) -> None:
    paths = _image_files(folder)
    if not paths:
        messagebox.showinfo("No images", f"No image files found directly in {folder}")
        return

    results = tk.Toplevel()
    results.title(f"Findings - {folder}")
    results.geometry("700x500")

    text = scrolledtext.ScrolledText(results, wrap=tk.WORD)
    text.pack(fill=tk.BOTH, expand=True)

    text.insert(tk.END, f"{len(paths)} image(s) in {folder}\n\n")
    for path in paths:
        try:
            text.insert(tk.END, _describe(path) + "\n\n")
        except Exception as exc:  # surfaced in the results window, not a crash
            text.insert(tk.END, f"{os.path.basename(path)}\n  ERROR: {exc}\n\n")
        results.update_idletasks()

    text.configure(state=tk.DISABLED)


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
