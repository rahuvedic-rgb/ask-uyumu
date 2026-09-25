buildozer_spec_content = """[app]

# (str) Title of your application
title = Ask Uyumu

# (str) Package name
package.name = askuyumu

# (str) Package domain (needed for android/ios packaging)
package.domain = org.rahuvedic

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (include python, image, json files)
source.include_exts = py,png,jpg,jpeg,json,kv

# (list) Application requirements
# SADECE python3 ve kivy! (urllib3/openssl kaldırıldı)
requirements = python3,kivy

# (str) Custom source folders for requirements
# Warning: feature is still experimental
#requirements.source.kivy = ../kivy

# (str) Application versioning (method 1)
version = 1.0

# (list) Permissions
android.permissions = INTERNET

# (str) Supported orientation (one of landscape, sensorLandscape, portrait or all)
orientation = portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (string) Preserved icon filename
icon.filename = %(source.dir)s/icon.png

#
# Android specific
#

# (bool) Indicate whether the screen should be kept on when the app is open
android.keep_screen_on = 1

# (int) Target Android API, should be as high as possible.
android.api = 33

# (int) Minimum API your APK will support.
android.minapi = 21

# (str) Android NDK version to use
android.ndk = 25b

# (bool) Automatically accept SDK license agreements
android.accept_sdk_license = True

# (str) The Android arch to build for, choices: armeabi-v7a, arm64-v8a, x86, x86_64
android.archs = arm64-v8a, armeabi-v7a

# (bool) Enable Android logcat
android.logcat_filters = *:S python:D

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = disable, 1 = enable)
warn_on_root = 1
"""

with open("buildozer.spec", "w", encoding="utf-8") as f:
    f.write(buildozer_spec_content)

print("Tam buildozer.spec dosyası başarıyla oluşturuldu!")
