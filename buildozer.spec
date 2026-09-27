[app]

# (str) Title of your application
title = AskUyumu

# (str) Package name
package.name = askuyumu

# (str) Package domain (needed for android/ios packaging)
package.domain = com.rahuvedic.askuyumu

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include
source.include_exts = py,png,jpg,kv,atlas,json,bsp

# (str) Application versioning
version = 1.0.0

# (list) Application requirements
# Python 3, Kivy ve Skyfield için gerekli saf Python / p4a paketleri
requirements = python3,kivy==2.2.1,skyfield,pytz,timezonefinder,certifi,urllib3,requests,chardet,idna

# (str) Supported orientation
orientation = portrait

# (bool) Fullscreen
fullscreen = 0

# (str) Icon
icon.filename = %(source.dir)s/1uyum (1).jpg

# (list) Permissions
internet = INTERNET, ACCESS_NETWORK_STATE

# (int) Target & Min API
android.minapi = 21
android.api = 33
android.ndk = 25b

# (bool) Accept SDK license automatically
android.accept_sdk_license = True

# (list) Architectures
android.archs = arm64-v8a

[buildozer]
log_level = 2
warn_on_root = 1
