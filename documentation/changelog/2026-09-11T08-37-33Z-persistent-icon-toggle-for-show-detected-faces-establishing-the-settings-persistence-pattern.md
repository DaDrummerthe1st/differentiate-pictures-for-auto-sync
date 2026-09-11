# Persistent icon toggle for show-detected-faces, establishing the settings-persistence pattern

Joakim asked that the fullscreen "show detected faces" `CheckBox` become a filled/outline icon toggle whose state survives swiping between photos and app restarts — and that this persistence pattern apply to every toggleable setting built from now on, not just this one. Replaced the checkbox with an `ImageButton` swapping between two rounded-rectangle `<shape>` drawables (outline/filled), backed by a new `SharedPreferences`-wrapping `AppSettings` class (`android/app/src/main/java/com/dpfas/photobrowser/settings/AppSettings.kt`) that future settings should extend rather than duplicate. TDD throughout: 83/83 unit tests green (5 new).

- **Doc size**: `documentation/mobile/TODO.md` 17,754 → 18,719 (+965); `documentation/mobile/README.md` 6,615 → 7,025 (+410); `documentation/GLOSSARY.md` 72,721 → 73,329 (+608).
