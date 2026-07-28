# TODO — security

Open items needing real resolution — captured so absence is a decision, not an
oversight, per this project's documentation-layout rule.

- **Facial-recognition/detection data security under a future DFS/multi-location
  world** (THREATS.md #6) — raised 2026-07-27, **researched 2026-07-29** against
  authoritative sources only (all lookups logged per `~/.claude/CLAUDE.md`'s
  research-log rule). Findings:
  - **The EDPB (EU's top data-protection body), Opinion 11/2024 on airport facial
    recognition, already ruled on almost exactly this scenario**: of four
    biometric-template storage architectures assessed, only two are
    GDPR-compatible — template on the subject's own device, or centralized
    storage encrypted with the **decryption key held solely by the subject**.
    Storage where the operator (or, by direct analogy, another user's NAS) holds
    the key was explicitly rejected, "regardless of the technical and
    organisational measures accompanying it." **This directly validates this
    project's existing owner-keyed "leased" ownership tier
    ([distributed-sync/OWNERSHIP.md](../distributed-sync/OWNERSHIP.md)) as the
    correct baseline** — not a compromise, the actual EU-regulator-approved
    answer. NIST SP 800-63B independently converges on the same
    local/subject-controlled preference.
  - **This is directly relevant, not a hypothetical "some EU relative" case**:
    Joakim and this project are Sweden-based, squarely inside GDPR's scope —
    there is no "is this even relevant for a non-EU project" question to ask.
  - **Encryption-at-rest is necessary but not sufficient once an embedding is
    ever decrypted.** Peer-reviewed literature (Mai et al., IEEE TPAMI 2018,
    through 2023-2025 follow-ups) shows face embeddings can be reconstructed
    into recognizable images with high fidelity — up to ~98% accuracy even
    against embeddings with privacy-enhancement applied. ISO/IEC 24745
    (irreversibility/unlinkability/renewability) is the field's answer to that
    residual risk, but the same research found published "irreversible" schemes
    were in fact reversible — don't trust a scheme's own claim without
    independent adversarial testing.
  - **GDPR's household/personal-activity exemption (Article 2(2)(c)) very
    plausibly ends the moment this project publishes a network-wide face-embedding
    index** — CJEU case law (Lindqvist, Rynes) ties the exemption to data staying
    within a private/family setting, not "accessible to an indefinite number of
    people." The private cross-network face-matching idea
    ([distributed-sync/METADATA.md](../distributed-sync/METADATA.md)) is the one
    feature most likely to trigger full GDPR Article 9 exposure.
  - **Privacy-preserving matching (homomorphic encryption / secure multiparty
    computation) is real, active, peer-reviewed research with genuine
    server-class efficiency** — but no source found tests it on Pi-class
    (~1GB RAM) hardware; treat as promising but not deployable on this project's
    actual target device today.
  - **Practical recommendation the research supports**: for the private
    cross-network face-matching idea specifically, never let a decrypted/usable
    embedding leave its subject's own device or get published to a shared index
    at all — do the matching such that only the searching user's own device ever
    sees a result, mirroring the EDPB's accepted subject-side/subject-keyed
    pattern, rather than relying on an unverified "irreversible" published
    embedding as the safety mechanism. Full sources and citation-quality labels:
    see the research session's findings, folded into
    [distributed-sync/METADATA.md](../distributed-sync/METADATA.md).
- **Third-party tagging consent** (THREATS.md #4) — no design yet for a tagged
  person (linked-account or local-only) to see, object to, remove, or block a tag
  that names/links her. Needs a real design pass, likely alongside
  [tags/UX_FLOWS.md](../tags/UX_FLOWS.md)'s existing invite-CTA flow rather than
  as a separate mechanism.
- **Server-side bounding-box validation** (THREATS.md #2) and **stored-XSS
  discipline for tag text** (THREATS.md #3) — both straightforward once real
  endpoints/GUI exist; capture as explicit TDD test cases at that point rather
  than trusting mockup-era discipline to carry over.
- **Should labeled face-detection data (bounding box + person tag) get a
  stricter access bar than ordinary photo data**, not just the same
  closed-by-default rule everything else gets (THREATS.md #1)? Undecided.
- **Auth hardening** (THREATS.md #10) — a compromised account inherits every
  privilege this design assumes only its legitimate owner has (leased-tier
  decrypt keys, private tags, item 6's face-matching reference embeddings if
  built). Needs a real design pass (password hashing, rate limiting/lockout,
  session/token management, MFA) before any sharing/DFS feature ships for
  real. Raised 2026-07-28/29 during tag/sharing design; not resolved here.

## Status

Opened 2026-07-27, alongside [README.md](README.md) and [THREATS.md](THREATS.md).
