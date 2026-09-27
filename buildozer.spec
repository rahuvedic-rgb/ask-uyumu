[app]

# (str) Application title
title = Ask Uyumu Analizi

# (str) Package name
package.name = askuyumu

# (str) Package domain
package.domain = com.rahuvedic

# (str) Source code where the main.py lives
source.dir = .

# (list) Source files to include
source.include_exts = py,png,jpg,kv,atlas,json

# (str) Application versioning
version = 1.0.0

# (list) Application requirements
requirements = python3==3.11.0,kivy==2.2.1,pytz,certifi,urllib3,requests,chardet,idna

# (str) Supported orientations
orientation = portrait

# (bool) Fullscreen
fullscreen = 0

# (list) Permissions
android.permissions = INTERNET, ACCESS_NETWORK_STATE

# (int) Target Android API
android.api = 33

# (int) Minimum API required
android.minapi = 21

# (str) Android NDK version
android.ndk = 25b

# (bool) Skip updating Android SDK
android.skip_update = False

# (bool) Automatically accept SDK licenses
android.accept_sdk_licenses = True

# (list) Modern 64-bit mimari
android.archs = arm64-v8a

[buildozer]

# (int) Log level
log_level = 2

# (int) Display warning if run as root
warn_on_root = 1
