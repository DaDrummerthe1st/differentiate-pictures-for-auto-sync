# Decide MNN runtime, scope sync-engine security research, iOS interim answer

Decided MNN (Alibaba, Apache-2.0) over ncnn for on-device inference — matches this project's
existing Apache-2.0 license family and carries an explicit patent grant BSD-3-Clause lacks, not
because either is more "open" than ONNX Runtime. Researched Syncthing's real maintenance status
(core actively maintained by the Syncthing Foundation, distinct from its separately discontinued
Android GUI-wrapper app) and confirmed embedding it (no separate app, via Go/gomobile bindings,
proven by the community SyncUp project) is technically real but non-trivial. Left the embed-vs-
build-custom sync engine choice open pending a dedicated security research pass (MITM, leak
surface) Joakim explicitly wants before deciding — too large for this session. Recorded the
interim iOS answer: the app must stay foregrounded until a sync completes, given iOS suspends
networking once backgrounded regardless of sync-engine choice.

- **Doc size**: `curation/IDENTITY_MATCHING.md` +2386 chars, `mobile/TODO.md` +453 chars.
