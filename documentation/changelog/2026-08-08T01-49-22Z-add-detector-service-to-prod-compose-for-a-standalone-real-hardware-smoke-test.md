# Add detector service to prod compose for a standalone real-hardware smoke test

Joakim wants to test-run the built-so-far detector work (quality trio + face detection) on the real
home server hardware before next session's fuller admin-source-setting + benchmarking build. Since
`detector`'s `POST /detect` takes image bytes directly and reads no mounted directory itself, it can
be added to `docker-compose.prod.yml` standalone - purely additive, doesn't touch `photo-viewer`'s
existing live `PHOTOS_HOST_PATH`/`momfiles` mount, no host port published. `documentation/photo-
server/DEPLOYMENT.md` gained a copy-paste section: pull latest, `up -d --build detector`, copy one
real photo from `/tank` into the container, POST it to `/detect`, and read real `docker stats` output
- gives Joakim actual hardware numbers for the currently-built detectors without needing any of the
still-unbuilt `documentation/plans/tingly-humming-pudding.md` work first.

- **Doc size**: `documentation/photo-server/DEPLOYMENT.md` +2256 chars.
