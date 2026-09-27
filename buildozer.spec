[app]

# Uygulama Bilgileri
title = Ask Uyumu
package.name = askuyumu
package.domain = org.askuyumu
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json

# Versiyon
version = 0.1

# Bağımlılıklar (Gstreamer çakışmalarını önlemek için sade tutulmuştur)
requirements = python3==3.11.0,kivy==2.2.1,pytz,certifi,urllib3,requests,chardet,idna

# Oryantasyon
orientation = portrait

# Android Ayarları
osx.kivy_version = 2.2.1
fullscreen = 0
android.api = 33
android.minapi = 21
android.ndk = 25b
android.ndk_api = 21
android.archs = arm64-v8a
android.accept_sdk_license = True
android.skip_update = False

[buildozer]
log_level = 2
warn_on_root = 1
