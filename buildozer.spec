[app]

# (str) Title of your application
title = Ask Uyumu

# (str) Package name
package.name = askuyumu

# (str) Package domain (needed for android/ios packaging)
package.domain = org.askuyumu

# (str) Source code where the main.py lives
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas

# (list) Application requirements
requirements = python3==3.11.0,kivy==2.2.1,pytz,certifi,urllib3,requests,chardet,idna

# (int) Target Android API, should be as high as possible.
android.api = 33

# (int) Minimum API required
android.minapi = 21

# (str) Android NDK version to use (Sadece 25b girilmelidir)
android.ndk = 25b

# (int) Android NDK API to use
android.ndk_api = 21

# (list) The Android archs to build for
android.archs = arm64-v8a

# (bool) Accept SDK license
android.accept_sdk_license = True
