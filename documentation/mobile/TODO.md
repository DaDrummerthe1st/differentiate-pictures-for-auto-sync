# mobile/ TODO

- **Verify the app actually builds and runs.** Written without a working Android SDK on this
  machine — open `android/` in Android Studio once installed, let it sync (it will need to
  generate `gradlew`/the Gradle wrapper jar, not committed), and confirm it installs on a real
  phone over `adb` before anything else touches this code.
- **Decide whether to keep iterating on this app or rewrite it once the toolchain is proven.**
  This pass was explicitly framed as disposable — don't assume the current `MainActivity`/
  `PhotoAdapter` split is the real foundation without asking Joakim first.
- **Resume the deferred roadmap once the above is settled**: on-device quality scoring (port of
  `previous-work/pictures-pipeline/quality.py`), on-device object detection (port of
  `objects.py`), user-driven sync to a server, automatic background trigger. None of this is
  scoped yet — treat `previous-work/pictures-pipeline/` as reference only, not a plan to resume
  verbatim, per [../../previous-work/README.md](../../previous-work/README.md).
- iOS: still a "consider it, don't build it" note, unchanged.
