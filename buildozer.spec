[app]

# (str) Title of your application
title = AskUyumu

# (str) Package name
package.name = askuyumu

# (str) Package domain (needed for android/ios packaging)
package.domain = com.rahuvedic.askuyumu

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas,json,bsp

# (str) Application versioning
version = 1.0.0

# (list) Application requirements
# Skyfield, pytz, timezonefinder ve gerekli C bağımlılıkları eklenmiştir
requirements = python3,kivy==2.2.1,skyfield,pytz,timezonefinder,sgp4,jplephem,certifi,urllib3,requests,numpy,h3,cffi

# (str) Supported orientation (landscape, sensorLandscape, portrait or all)
orientation = portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (str) Icon of the application
icon.filename = %(source.dir)s/1uyum (1).jpg

# (list) Permissions
internet = INTERNET, ACCESS_NETWORK_STATE, ACCESS_FINE_LOCATION, ACCESS_COARSE_LOCATION

# (int) Minimum API required (Android 7.0 / Nougat)
android.minapi = 24

# (int) Target Android API (Android 13 / 14 standartı)
android.api = 33

# (str) Android NDK version
android.ndk = 25.2.9519653

# (bool) Accept SDK license automatically
android.accept_sdk_license = True

# (list) List of Android architectures to build for
android.archs = arm64-v8a, armeabi-v7a

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = disable, 1 = enable)
warn_on_root = 1
