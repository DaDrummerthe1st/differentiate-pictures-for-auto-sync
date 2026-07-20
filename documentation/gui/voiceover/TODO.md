# TODO — documentation/gui/voiceover/

## Durability/export

Current voiceover recordings (audio + pointer-timeline JSON) only work via this app's own server staying runnable - the referenced photo paths and the live playback re-composition break if the app changes significantly or the photo library gets reorganized. Joakim wants recordings to remain listenable/watchable for years, independent of this app's future, and shareable (e.g. shown to his kids later).

Decided direction (2026-07-16): **bake each voiceover into an actual MP4 video** - photos shown full-frame with a moving pointer-dot overlay, synced to the recorded audio, encoded via ffmpeg. This is the most durable option (any device/player can open an MP4 forever, fully independent of this app) versus a self-contained HTML+audio+photos folder (also considered, more fragile long-term - needs a browser and working JS forever) or just fixing path-fragility without exporting (smallest change, doesn't solve the actual "shareable for years" ask).

Not started - needs:

- ffmpeg added to the Docker image (`apt-get install ffmpeg`).
- A frame-plan function: given the recorded events + a target fps + the audio's total duration → which photo and pointer position for each frame. Pure logic, no ffmpeg dependency - unit-testable in the existing pytest suite same as everything else in `app/main.py`.
- A Pillow-based frame renderer: photo letterboxed to a fixed video resolution (e.g. 1280x720) with the dot overlay drawn on top, reusing the same fit/letterbox logic the lightbox already does visually in CSS, just baked into a raster frame instead.
- The ffmpeg invocation itself: mux the rendered frame sequence with the original audio into a single MP4 (`-c:v libx264 -c:a aac`), matching total video length to the audio's duration.
- A UI entry point (e.g. an "Exportera som video" button next to each saved voiceover in the "Berättelser" list) and a way to download the resulting MP4 once rendered - rendering will take real wall-clock time (not instant like the JSON+audio save is today), so this needs its own progress/status UI, not just an instant button click.
