[app]

# Uygulama Başlığı ve Paket Bilgileri
title = Ask Uyumu
package.name = askuyumu
package.domain = org.askuyumu
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json

# Versiyon Bilgisi
version = 0.1

# Uygulama Bağımlılıkları (swisseph derleme reçetesi eklenmiştir)
requirements = python3==3.11.0,kivy==2.2.1,pytz,certifi,urllib3,requests,chardet,idna,sqlite3,swisseph

# Oryantasyon ve Ekran Ayarları
orientation = portrait
fullscreen = 0

# Android SDK / NDK Yapılandırması
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
