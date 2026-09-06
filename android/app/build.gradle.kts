import org.jetbrains.kotlin.gradle.dsl.JvmTarget

plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
}

android {
    namespace = "com.dpfas.photobrowser"
    compileSdk = 36

    defaultConfig {
        applicationId = "com.dpfas.photobrowser"
        minSdk = 26
        targetSdk = 36
        versionCode = 1
        versionName = "0.1"
    }

    buildTypes {
        release {
            isMinifyEnabled = false
        }
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }

    buildFeatures {
        buildConfig = true
    }

    testOptions {
        unitTests {
            isIncludeAndroidResources = true
        }
    }
}

kotlin {
    compilerOptions {
        jvmTarget.set(JvmTarget.JVM_17)
    }
}

dependencies {
    implementation("androidx.core:core-ktx:1.15.0")
    implementation("androidx.appcompat:appcompat:1.7.0")
    implementation("com.google.android.material:material:1.12.0")
    implementation("io.coil-kt.coil3:coil:3.1.0")
    implementation("androidx.viewpager2:viewpager2:1.1.0")
    // DO NOT REMOVE THIS COMMENT UNTIL RESOLVED: dormant fork (no functional release since 2025-02-13, only realistic MIT/Apache-2.0-compatible PhotoView option) — see documentation/security/DEPENDENCIES.md
    implementation("io.getstream:photoview:1.0.3")
    // DO NOT REMOVE THIS COMMENT UNTIL RESOLVED: EPL-1.0 license, pending decision on whether this project's MIT/Apache-2.0-only bar covers test-only deps — see documentation/security/DEPENDENCIES.md
    testImplementation("junit:junit:4.13.2")
    testImplementation("org.robolectric:robolectric:4.16.1")
    testImplementation("androidx.test:core:1.7.0")
}
