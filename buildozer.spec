[app]

# (str) Title of your application
title = Ask Uyumu

# (str) Package name
package.name = askuyumu

# (str) Package domain
package.domain = org.askuyumu

# (str) Source code location
source.dir = .

# (list) Source files to include
source.include_exts = py,png,jpg,kv,atlas,json

# (list) Application requirements
requirements = python3==3.11.0,kivy==2.2.1,pytz,certifi,urllib3,requests,chardet,idna

# (int) Target Android API
android.api = 33

# (int) Minimum API supported
android.minapi = 21

# (str) Android NDK version to use
android.ndk = 25b

# (int) Android NDK API level
android.ndk_api = 21

# (list) Target architecture
android.archs = arm64-v8a

# (bool) Accept SDK license
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 1
