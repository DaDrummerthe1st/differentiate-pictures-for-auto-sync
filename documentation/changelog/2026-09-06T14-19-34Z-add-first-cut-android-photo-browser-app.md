# Add first-cut Android photo-browser app

The smallest possible sideloaded Android app — a single Activity that requests photo permission
and shows a `MediaStore` grid, nothing else — to prove the Kotlin/Gradle/Android toolchain works on
this machine at all, per Joakim's explicit request to skip the fuller Slice 1 plan scrapped earlier
this session. No tests written for this pass, a deliberate one-time exception to this repo's TDD
rule — see `documentation/mobile/README.md`. Not yet build-verified: written before Android Studio
finished installing here.

- **Doc size**: `README.md` +234; `documentation/README.md` +117; `documentation/tooling/README.md`
  +101; new `documentation/mobile/README.md` +2498; new `documentation/mobile/TODO.md` +1127; new
  `android/README.md` (code-dir stub) +143. Net +4220 chars.
