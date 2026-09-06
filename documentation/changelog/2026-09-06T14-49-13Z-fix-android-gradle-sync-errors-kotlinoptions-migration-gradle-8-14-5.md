# Fix Android Gradle sync errors: kotlinOptions migration, Gradle 8.14.5

Joakim hit two Gradle sync errors opening `android/` in Android Studio, before ever running a
build. `android { kotlinOptions { jvmTarget = "17" } }` is a hard error under Kotlin 2.4.0's Gradle
plugin — migrated to `kotlin { compilerOptions { jvmTarget.set(JvmTarget.JVM_17) } }` in
`android/app/build.gradle.kts`. Separately, Gradle 8.13 warned it'll stop being supported by a
future Kotlin Gradle Plugin release — bumped the wrapper to 8.14.5 (latest patch, includes two
security fixes over 8.14.3).

- **Doc size**: `GLOSSARY.md` +433; `mobile/README.md` +424. Net +857 chars.
