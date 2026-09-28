[app]

# (str) Title of your application
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
requirements = python3,kivy,pytz,certifi,urllib3,requests,chardet,idna

# (str) Supported orientation
orientation = portrait

# (bool) Fullscreen
fullscreen = 0

# (str) Icon filename (Türkçe karakter ve parantez içermeyen temiz dosya)
icon.filename = %(source.dir)s/icon.png

# (list) Permissions
internet = INTERNET, ACCESS_NETWORK_STATE

# (int) Minimum & Target Android API
android.minapi = 21
android.api = 33

# (bool) Accept SDK license automatically
android.accept_sdk_license = True

# (list) Architectures
android.archs = arm64-v8a

[buildozer]
log_level = 2
warn_on_root = 1
