# documentation/gui/voiceover/

The "record a story while clicking through pictures" feature — talk while
freely browsing photos, play it back later with the right photo and a
pointer dot re-appearing in sync with the narration.

## How it works today

**Recording**: `MediaRecorder` captures microphone audio (WebM/Opus,
browser default). While recording, a `setInterval` samples every 200ms:
whichever photo the pointer currently rests on (thumbnail grid *or*
fullscreen lightbox), and the pointer's x/y position as a fraction of
that photo's rendered box. Each sample is `{t, path, x, y}` (`t` = seconds
since recording started). No fixed plan or script - it's freeform, timed
purely by when the user happens to be pointing at something.

**Storage**: `POST /api/voiceover` (multipart: the audio blob + the
JSON event array) → `app/main.py`'s `voiceovers` SQLite table
(timestamp, audio filename, the full event list as JSON) + the audio
file itself in the `stories` docker volume.

**Playback**: `GET /api/voiceover/{id}` returns the events and an audio
URL. As the audio's `timeupdate` fires, the player finds the latest
event at or before the current playback time, swaps the displayed photo
if it changed, and repositions a dot overlay at that event's x/y
fraction.

**Discoverability**: a "❓ Hjälp" button keeps the first-use explanation
of how recording works reachable even after it's been dismissed once
(see the dismissable-info-message system in
[../README.md](../README.md#features-current-state)) — nothing read-once
here is ever permanently lost.

## Known limitation

Everything above depends on this app's server staying runnable and the
referenced photo paths staying valid. If the app changes significantly
or the photo library gets reorganized, playback breaks even though the
audio file itself would still be intact. See TODO.md for the planned fix.
