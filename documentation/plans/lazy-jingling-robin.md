# Automatic tagging: containerized detector service (quality + face + object/animal)

## Context

The tags GUI (built 2026-08-05, see `documentation/gui/TODO.md`) has a `source` column
(`manual`|`auto`) and already renders `auto`-sourced tags distinctly (dashed border/chip,
`.tag-box-auto`/`.tag-chip-auto` in `app/static/style.css`, driven purely by
`tag.source === "auto"` in `app/static/app.js:872,888`) — confirmed by reading the code, not
assumed. Nothing produces `source='auto'` rows yet. `documentation/curation/DETECTORS.md` has
researched, license-cleared model picks for several detection areas, but curation/ has no
numbered, TDD-able build plan yet — only a catalog. This plan is that first build plan, scoped to
one session.

Two decisions from this conversation shape the design:
- **Containerized, not in-process**: detector models (OpenCV/ONNX Runtime, several hundred MB of
  library + model weight footprint) run in their own container, called by the main `photo-viewer`
  app rather than imported into it — keeps the app container light, and is a natural first step
  toward Joakim's longer-term interest in swappable/user-supplied detection models (flagged, not
  built, in `documentation/curation/RESEARCH_QUEUE.md`'s "Bring-your-own identity model" item and
  `documentation/security/THREATS.md` #12 — model files are a code-execution surface, ONNX only,
  never pickle/`.pt`).
- **Roles, not hardcoded accounts**: "build user groups. elisabeth = user with her own space to
  save in. joakim = admin = access everywhere." Today's JWT only carries `sub` (user id) — no role
  claim reaches `app/auth.py` at all, even though `server/`'s `users` table already has a `role`
  column. This plan adds `role` to the JWT and uses it for tag visibility, rather than writing
  code that has to change again once the account model changes.
- **Test on this workstation first, deploy later**: Joakim wants to see real results here before
  anything touches the server's `/tank` library. Deploy commands are written for Joakim to
  copy/paste (per `POLICY.md`'s "Deployment... always performed by Joakim, never automated by the
  AI session") — not run by this session.

**Explicitly out of scope for this session** (per the original request's own priority order):
global tag search/browse, the ES-module split, OCR/burned-in-timestamp (a materially different
mechanism — feeds a date field via a confirm-flow, not a plain auto-tag), and any "app store"/
bring-your-own-model UI (captured as a forward-looking doc note only, tied to the two references
above).

**Session scope, confirmed with Joakim**: this session builds only Phase 0 and Phase 1 below
(role-aware sessions + the empty `detector` service skeleton), then stops and leaves a short
handoff note for the next session to pick up at Phase 2. Phases 2-7 are recorded below as the
already-designed roadmap (so the next session doesn't have to re-derive category mappings, model
picks, or the vendoring/testing approach) but are **not implemented this session**. Everything
within Phase 0-1's own scope proceeds autonomously, without further check-ins.

## Detector roster this session

- **Quality trio** (no model — classic CV, DETECTORS.md area A pick): blur (variance of
  Laplacian), exposure (luminance histogram), monochrome (saturation-channel mean).
- **Face detection**: YuNet (OpenCV Zoo, Apache-2.0, sub-1MB ONNX, via `cv2.FaceDetectorYN`).
- **Object/animal detection**: NanoDet-Plus (Apache-2.0), COCO 80 classes — 10 of them are animals
  (bird/cat/dog/horse/sheep/cow/elephant/bear/zebra/giraffe), the rest map to `objects`.

Category/value mapping onto `app/main.py`'s existing `TAG_CATEGORIES`
(`people/places/objects/animals/occasion/generic`) — no new categories:

| Detector | category | value | bbox |
| --- | --- | --- | --- |
| Blur | `generic` | `"blurry"` | none (whole-photo) |
| Over/under exposure | `generic` | `"overexposed"` / `"underexposed"` | none |
| Monochrome | `generic` | `"black_and_white"` | none |
| Face | `people` | `"Person"` (placeholder — Joakim/Elisabeth relabel with a real name by editing the auto chip, same edit flow manual tags already use) | yes |
| Object (non-animal COCO class) | `objects` | COCO class name | yes |
| Object (animal COCO class) | `animals` | COCO class name | yes |

Each detector gates on a confidence threshold (named constant, overridable via env var — nothing
hardcoded/magic) and simply doesn't emit a tag below it; no confidence column added to `tags`
(not asked for, keeps the schema change minimal).

## Phase 0 — Role-aware sessions (prerequisite for shared auto-tag visibility)

0.1 `server/app/tokens.py`'s `create_access_token` takes a `role` param, embeds `"role": role` in
the JWT payload alongside `sub`. `server/app/auth_routes.py`'s login handler passes the role
already loaded from `users.role`. Test: a minted token decodes with the expected role claim.
**Security**: role comes only from the DB row just authenticated against, never from client input.

0.2 `app/auth.py` (photo-viewer): `require_session` returns `(user_id, role)` instead of bare
`user_id` (update the one caller in `app/main.py` accordingly — currently `Depends(require_session)`
sites just unpack the tuple). Test: a token with no `role` claim (old-style, for
backward-compatibility during rollout) defaults to `"member"`, never `"admin"` — fail closed, not
open. **Security**: this is the one place a forged/old token could try to claim elevated access;
explicit test that a tampered `role` claim without a valid signature is still rejected by the
existing `jwt.decode` verification (already true, but worth a named regression test given the new
field is now security-relevant).

0.3 `GET /api/tags` and `GET /api/tags/values` in `app/main.py`: visibility rule becomes
`user_id = <requester> OR source = 'auto' OR <requester's role> = 'admin'` instead of the current
strict `user_id = ?`. Test matrix: member sees own manual tags + all auto tags, not another
member's manual tags; admin sees everything. **Security**: `POST/PATCH/DELETE /api/tags` stay
scoped to the acting user's own manual tags only (unchanged) — admin's "access everywhere" is
read visibility, not silent edit/delete rights over someone else's manual tag; write that as an
explicit test, not an assumption.

## Phase 1 — `detector` service skeleton

New `detector/` directory: `main.py` (FastAPI, `GET /health`), `Dockerfile` (`python:3.12-slim` +
`libgl1`/`libglib2.0-0` — confirm these are actually the packages `opencv-python-headless` needs
on slim before writing the Dockerfile, don't assume), `requirements.txt` (`fastapi`, `uvicorn`,
`opencv-python-headless`, `onnxruntime`, `numpy`, `python-multipart`) — kept entirely separate from
the root `requirements.txt` so the main app container's footprint doesn't grow.

Wire into `docker-compose.yml` (local dev) only in this phase: new `detector` service, `build:
./detector`, no host port published (internal network only, matches `auth`/`postgres`/`redis`'s
existing pattern), `mem_limit: 768m` (a starting conservative value — flag inline that this needs
real measurement once models are loaded, per the existing unresolved "object-detection timing
benchmark" item in `documentation/curation/TODO.md`, not guessed further).

Test: `docker compose up -d detector && curl` against its health check from another container on
the same network (mirrors 0.2's compose smoke-test pattern in `documentation/photo-server/TODO.md`).

## Phase 2 — Quality trio (no model, TDD against synthetic PIL images)

`detector/quality.py`: `detect_blur`, `detect_exposure`, `detect_monochrome`, each a pure function
(image → bool + nothing else, no bbox). Tests generate the same kind of synthetic fixtures
`app/tests/conftest.py` already does (`Image.new(...)`) — a sharp vs. Gaussian-blurred image, an
all-white/all-black vs. mid-tone image, a grayscale vs. saturated-color image. Wire behind
`POST /detect` on the detector service, gated by confidence thresholds.

## Phase 3 — Face detection (YuNet)

Vendor `face_detection_yunet_*.onnx` under `detector/models/`, downloaded from the OpenCV Zoo
GitHub release, same "fetch once, commit, note the source+license" convention as
`app/static/vendor/`'s jQuery/Bootstrap/Material Symbols. Add a `detector/models/LICENSES.md`
entry (Apache-2.0, source URL).

Test fixtures: `resources/test_pictures/Florida1/` (real, disposable, already gitignored, already
used informally as this project's test photo tree) has real people in some frames — pick 1-2 known
files with a clear face and 1-2 with none as fixed-path fixtures for a positive/negative test.
**Confirm the actual `cv2.FaceDetectorYN` API shape against the real downloaded model file before
writing the wrapper** — don't assume the constructor/inference signature, same "verify against a
real file first" convention this project already follows for EXIF/RAW APIs
(`documentation/photo-server/TODO.md` 3.1/3.2).

## Phase 4 — Object/animal detection (NanoDet-Plus)

Same vendoring pattern as Phase 3 for the NanoDet-Plus ONNX export. **Confirm the actual
pre/postprocessing this specific ONNX export needs (anchor-free decode, NMS) against the real file
before writing code** — NanoDet's output shape isn't a single standard everyone's export agrees
on; check what's actually in the downloaded graph rather than assuming a reference
implementation's shape applies unchanged. Test fixtures: same `resources/test_pictures/Florida1/`
tree, picking files with recognizable COCO-class objects.

## Phase 5 — Orchestration: the auto-tag batch job

`app/auto_tag.py`, run via `docker compose exec photo-viewer python -m app.auto_tag` (same
invocation convention as `scripts/create_account.py` — a CLI, not a new HTTP admin endpoint, since
this is an infrequent batch operation, not something the GUI triggers). Walks `PHOTOS_ROOT`, POSTs
each image's bytes to `http://detector:8500/detect`, inserts qualifying detections into `tags`
with `source='auto'` under a reserved sentinel user id (`AUTO_TAGGER_USER_ID`, a named constant,
never a real account — Phase 0.3's visibility rule makes the stored id moot for `auto` rows anyway
since they're globally visible regardless of who/what wrote them).

Idempotent re-runs: before inserting new auto rows for a given `photo_path`, delete existing
`source='auto'` rows for that path first (re-running after a model change replaces stale
detections rather than accumulating duplicates). Test: running twice against the same fixture
photo produces the same row count, not double.

**Security**: the batch job only ever reads photo bytes from within `PHOTOS_ROOT` (reuses
`resolve_relpath`'s existing traversal guard) and only ever writes to the `tags` table — no other
side effects.

## Phase 6 (human checkpoint) — local smoke-test on this workstation

Run the whole stack locally (`docker compose up -d`), run `app/auto_tag.py` against
`resources/test_pictures/Florida1/` (real photos, already local, already disposable-per-policy —
not `/tank`/`momfiles`), open the gallery, confirm: auto tags render dashed as expected with zero
GUI changes; a face box can be relabeled with a real name via the existing edit flow; Elisabeth's
role (`member`) still can't see another member's *manual* tags but does see all `auto` ones;
admin role sees everything. This is the checkpoint before anything below gets written for the
server.

## Phase 7 — Deploy commands (written for Joakim to run, not run by this session)

Once Phase 6 passes: a new `detector` service block for `docker-compose.prod.yml` (same
internal-only-network shape as Phase 1, real `mem_limit`), plus a copyable command block for
running `app/auto_tag.py` against a broader read-only mount of `/tank`'s parent (not just the
existing `PHOTOS_HOST_PATH`/`momfiles` mount) — per Joakim's ask and the existing "/tank test-data
convention" note in `documentation/curation/TODO.md` (rest of `/tank` outside `momfiles` is
Joakim's own sanctioned test scope). Delivered as a plain copyable command block at the end of this
session, per `POLICY.md`'s deployment rule — this session never SSHes into or runs anything against
192.168.1.10 itself.

## Documentation updated in the same pass

- `documentation/curation/TODO.md` / `RESEARCH_QUEUE.md`: mark the build-plan item as started, link
  to this session's work.
- `documentation/tags/SCHEMA.md`: note the role-based visibility rule in the "Now" section, and
  `AUTO_TAGGER_USER_ID`'s existence.
- `documentation/gui/TODO.md`: new dated session entry (per this repo's own convention).
- `documentation/curation/DETECTORS.md`: flip the three built areas from "researched" to
  "built" with a pointer to `detector/`.
- Any new term (YuNet, NanoDet-Plus, COCO classes, JWT role claim if not already glossed) appended
  to `documentation/GLOSSARY.md` in the same turn each is explained in chat, per CLAUDE.md.
- A short forward-looking note (DETECTORS.md's "Also flagged" section or `curation/ARCHITECTURE.md`)
  recording the "app store"/bring-your-own-detector idea Joakim raised, cross-linked to the
  existing RESEARCH_QUEUE.md item and THREATS.md #12 — not designed further now.

## Verification (this session — Phase 0 and 1 only)

- `.venv-test/bin/python -m pytest app/tests/ -q` and `server/`'s existing suite, both green,
  including new tests for the role claim and the `user_id = ? OR source = 'auto' OR role =
  'admin'` visibility rule.
- Phase 1's compose health-check smoke test (`docker compose up -d detector && curl` its
  `/health` from another container on the same network).

## Handoff note for the next session (write this into `documentation/curation/TODO.md` /
`documentation/gui/TODO.md` at the end of this session, kept short per this repo's own
lean-doc convention)

Phase 0 (role-aware sessions) and Phase 1 (`detector` service skeleton, empty `/health` only) are
done. **Start at Phase 2** in this same plan's roadmap above: the quality trio (blur/exposure/
monochrome — no model, TDD against synthetic PIL images, same pattern as `app/tests/conftest.py`).
Phases 3-7 (face detection/YuNet, object detection/NanoDet-Plus, the `auto_tag.py` orchestration
job, the local smoke-test checkpoint, and the written-not-run server deploy commands) follow in
order after that — model picks, category/value mappings, and vendoring conventions are already
decided above, don't re-research them.
