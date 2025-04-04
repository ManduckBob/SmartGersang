buildscript {
    dependencies {
        classpath("com.google.gms:google-services:4.4.2")
    }
}

plugins {
    id("com.android.application")
    id("kotlin-android")
    id("dev.flutter.flutter-gradle-plugin")
    id("com.google.gms.google-services")
    // ✅ 버전 없는 기본 선언
}

android {
    namespace = "com.example.smartgersang"
    compileSdk = flutter.compileSdkVersion
    ndkVersion = "27.0.12077973"

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_11
        targetCompatibility = JavaVersion.VERSION_11
        isCoreLibraryDesugaringEnabled = true  // ✅ 이 줄 추가!
    }

    kotlinOptions {
        jvmTarget = JavaVersion.VERSION_11.toString()
    }

    defaultConfig {
        applicationId = "com.example.smartgersang"
        minSdk = flutter.minSdkVersion
        targetSdk = flutter.targetSdkVersion
        versionCode = flutter.versionCode
        versionName = flutter.versionName
    }

    buildTypes {
        release {
            signingConfig = signingConfigs.getByName("debug")
        }
    }
}

flutter {
    source = "../.."
}

dependencies {
    // 🔥 이 줄 꼭 추가!
    coreLibraryDesugaring("com.android.tools:desugar_jdk_libs:2.0.4")

    // ✅ Firebase BoM (모든 Firebase 의존성을 이 버전에 맞춰줌)
    implementation(platform("com.google.firebase:firebase-bom:33.12.0"))

    // ✅ 사용하고자 하는 Firebase 제품들
    implementation("com.google.firebase:firebase-analytics")
    implementation("com.google.firebase:firebase-messaging")  // 🔔 FCM 알림
}
