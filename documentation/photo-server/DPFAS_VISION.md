# DPFAS vision — metadata generation

No code, this is direction only. The standing goal across the whole
project: get users to generate metadata around each photo's vectorized
representation, through three UX paths. This is Pillar 2 of the larger
system direction — see [../VISION.md](../VISION.md) for how it relates
to distributed storage, presentation/sharing, and event reconstruction.

| Path | Status | Notes |
| --- | --- | --- |
| Search / filter | Built in [TODO.md](TODO.md) Phase 4 | Postgres tsvector now; becomes more useful once location/manual tags exist |
| Manual tagging | Schema now, endpoints fast-follow | `tags.kind = 'content'`, see [DATA_DICTIONARY.md](DATA_DICTIONARY.md); album tags (`kind = 'album'`) are a separate, already-built path — see [MOCKUP.md](MOCKUP.md) |
| Automated analysis (face/object recognition) | DPFAS phase, not started | See below |

Inference runs on the phone, on-device — only derived tags and, later,
embeddings sync back to the server via pgvector. Raw photos never need to
leave the server for this to work; the phone reads a full-resolution
photo to run inference locally and discards it afterward.

This is the reason Postgres was chosen as the sole database engine (see
[README.md](README.md)): pgvector runs inside the same instance, so no
second database is needed when this phase starts.
