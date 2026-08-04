# Discuss tagging legal jurisdiction, OCR-PII-to-privacy-tag, tag provenance disclosure, entity-squatting analysis, BYO-model risk

Joakim asked a cluster of questions about tagging individuals: cross-border legal responsibility, OCR-detected text-as-PII becoming a per-photo privacy tag, being informed exactly how derived data is used, whether tagging himself/his dog lets someone else "tap into" that identity, and bringing his own pretrained identity model for comparison. Resolved/recorded, not all newly designed — several turned out to already be answered by existing design, verified rather than assumed:

- **Jurisdiction (POLICY.md)**: GDPR Article 3(1)'s establishment criterion means responsibility sits with the Sweden-established controller for *any* tagged individual, regardless of her nationality/location — a non-EU friend doesn't create a weaker regime. EDPB Guidelines 3/2018 sourced.
- **Entity/identity squatting (THREATS.md #11)**: analyzed against SCHEMA.md/TAXONOMY.md — owner-scoped entities plus email-bound (not name-matched) invite linking already close this; documented as mitigated-by-design rather than newly designed. Genuinely open risk is mislabeling (already tracked separately).
- **BYO pretrained model risk (THREATS.md #12)**: loading a user-supplied model file (e.g. pickle-based `.pt`) is a code-execution surface, not just a content risk — flagged before any such feature exists. Menu item added (RESEARCH_QUEUE.md).
- **OCR-in-frame (DETECTORS.md area D)**: UX mechanism sketched — detect text, pattern-match for PII, confirm-or-blur prompt, becomes a privacy-category tag feeding the existing blur-preview review. No model pick yet. A speculative reverse-search idea ("feed me text to protect") added under "Also flagged" — corrected Joakim's own assumption that it needs an LLM; it's a plain string match once OCR text is indexed.
- **Tag provenance/usage disclosure (TAXONOMY.md)**: new transparency principle — any tag should show what produced it, its confidence, who can see it, and what it's used for, extending the Curator's existing "explain, never silent" rule to every tag.

GLOSSARY.md gets PII, establishment vs. targeting criterion, unsafe deserialization/pickle RCE, face detection vs. recognition vs. re-identification, and tag provenance/usage disclosure entries.

- **Doc size**: +12,587 chars (net, across POLICY.md, THREATS.md, DETECTORS.md, RESEARCH_QUEUE.md, TAXONOMY.md, GLOSSARY.md; Unicode codepoints, per DOC_METRICS.md methodology).
