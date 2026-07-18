[app]
title = Metal marking
package.name = metalmarking
package.domain = org.marking
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1
android.ndk = 25b
android.ndk_version = 25b
requirements = python3, kivy, numpy, matplotlib, kivy_garden.matplotlib
android.sdk_path = /home/runner/.buildozer/android/platform/android-sdk
android.ndk_path = /home/runner/.buildozer/android/platform/android-ndk-r25b
orientation = portrait
fullscreen = 0
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = True
android.api = 33
android.minapi = 21
android.ndk_api = 21
android.private_storage = True
android.sdk_build_tools_version = 34.0.0

[buildozer]
log_level = 2
warn_on_root = 1
