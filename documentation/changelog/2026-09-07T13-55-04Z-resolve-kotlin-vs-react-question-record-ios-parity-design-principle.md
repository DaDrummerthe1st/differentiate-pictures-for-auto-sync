# Resolve Kotlin-vs-React question, record iOS-parity design principle

Joakim asked whether Kotlin vs. React was even a meaningful choice given both would eventually
need platform-specific work, especially for iOS. Answer: it depends which "React" — React Native
(a real mobile app, same background-photo-access capability as Kotlin) vs. a React web app/PWA
(which reintroduces the exact structural limitation the native-app pivot escaped). Confirmed:
staying on native Kotlin. Recorded a standing "consider iOS parity at every design decision"
principle in `VISION.md`'s cross-cutting-principle section so future sessions carry it forward
without re-deriving it.

- **Doc size**: `VISION.md` +1148 chars.
