# Fix EXIF-rotation bbox misplacement, add EXIF section to test_main

Joakim ran test_main.py on real phone photos and found predictions correct but boxes on the
wrong content, image visibly rotated. Root cause: cv2.imread (objects.py's detector)
auto-rotates per EXIF orientation, PIL.Image.open (test_main's display) doesn't - fixed with
ImageOps.exif_transpose plus an assertion so a recurrence fails loudly. Also restructured each
photo's entry into clearly separated, bordered sections (EXIF/Quality/Objects/image), and added
an EXIF section (camera, settings, GPS - read directly via PIL, not a new modules/ detector)
per Joakim's follow-up ask.

- **Doc size**: GLOSSARY.md +837, modules/README.md +318.
