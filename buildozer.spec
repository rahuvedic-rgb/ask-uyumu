[app]

# (str) Application title
title = AskUyumu

# (str) Package name
package.name = askuyumu

# (str) Package domain
package.domain = com.rahuvedic.askuyumu

# (str) Source code directory
source.dir = .

# (list) Source files to include
source.include_exts = py,png,jpg,kv,atlas,json,bsp

# (str) Application versioning
version = 1.0.0

# (list) Application requirements
# Skyfield, pytz ve timezonefinder gereksinimleri tanımlandı
requirements = python3,kivy==2.2.1,skyfield,pytz,timezonefinder,certifi,urllib3,requests,chardet,idna

# (str) Supported orientation
orientation = portrait

# (bool) Fullscreen
fullscreen = 0

# (str) Application Icon
icon.filename = %(source.dir)s/1uyum (1).jpg

# (list) Permissions
internet = INTERNET, ACCESS_NETWORK_STATE

# (int) Minimum and Target Android API
android.minapi = 21
android.api = 33
android.ndk = 25b

# (bool) Accept SDK license automatically
android.accept_sdk_license = True

# (list) Architectures
android.archs = arm64-v8a

[buildozer]

# (int) Log level
log_level = 2

# (int) Display warning if run as root
warn_on_root = 1
