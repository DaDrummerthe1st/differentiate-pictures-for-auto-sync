# Show upload progress and jump to newly uploaded photos

Joakim reported that uploading photos showed no progress and the uploads never appeared as thumbnails (`documentation/bugs/repo/under_process/2026-08-13-photo-upload-has-no-visible-progress-and-uploaded-photos-aren-t-shown.md`). Root cause for both: the existing progress text was written into `uploadBtn`, which its own click handler had already hidden inside `#moreActionsMenu`; and uploads land in a flat, unnamed-headline (`"."`) album that the frontend never auto-switches to. Added a visible top progress banner (`app/static/index.html`/`style.css`, same pattern as `#recordingBanner`) and made a successful upload jump to that album via the existing `setActiveAlbum()`, now displayed as "Uppladdade bilder" instead of a bare `.`.

- **Doc size**: bug file 0 → 4,143 characters (new).
