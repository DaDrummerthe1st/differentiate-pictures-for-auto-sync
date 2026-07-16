# mamma-photo-viewer

Single-container, no-login web viewer for browsing `/home/joakim/Pictures/mammas_bilder`
and picking photos to keep. Built for a one-off task: browse everything, mark ~20-30
favorites, save them.

## Run

```
cd /home/joakim/code/project/mamma-photo-viewer
docker compose up -d
```

Open **https://\<this-machine's-LAN-IP\>:8420** (LAN IP right now: `192.168.0.252`, may
differ on reboot — check with `ip -4 addr`). HTTPS is required (self-signed cert) because
the folder-picker feature only works in a secure browser context. First load will show a
"connection is not private" warning — click **Advanced → Proceed** (normal for a
self-signed cert, nothing is actually wrong).

Stop with:

```
docker compose down
```

## How it works for the person using it

1. First screen: click **"Välj mapp för nedladdningar"** and pick a folder on her own
   Windows machine (needs Edge or Chrome — Firefox doesn't support this API). That choice
   is remembered for future visits.
2. Browse mode (default): click a thumbnail to open it full-screen/zoomed, with a
   download button and prev/next.
3. Click **"Markera bilder"** to switch into selection mode: clicking thumbnails marks
   them (checkmark), and a floating **"Ladda ner markerade (N)"** button appears —
   downloads all marked photos straight to the chosen folder, no per-file dialogs.
4. Albums: grouped by top-level folder name as a headline, with sub-galleries labeled by
   their immediate parent folder path underneath (e.g. headline `Florida1`, chunks
   `Florida1/Florida/1`, `Florida1/Florida/2`, ...).

## Known limitations (accepted for speed)

- No auth, no HTTPS cert trust — fine only because this stays on the home LAN.
- Self-signed cert triggers one browser warning on first visit.
- Non-image files in the source tree (there's a lot of old software-install junk under
  `no_label/`) are silently skipped — only actual image extensions are shown.
