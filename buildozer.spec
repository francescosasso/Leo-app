[app]

title = Leó
package.name = leo
package.domain = org.sassofrancesco

source.dir = .
source.include_exts = py,png,jpg,json

version = 1.6

# ===============================
# PYTHON REQUIREMENTS
# ===============================
requirements = python3,kivy,requests,plyer,cython==0.29.36

# ===============================
# UI
# ===============================
orientation = portrait
fullscreen = 0

icon.filename = icon.png

# ===============================
# ANDROID
# ===============================
android.permissions = INTERNET

# ⚠️ BUILD O Z E R COMPATIBILE
android.api = 30
android.minapi = 24
android.build_tools_version = 30.0.3

# USA SDK INSTALLATO DAL WORKFLOW
android.sdk = /home/runner/android-sdk

android.ndk = 25b
android.archs = arm64-v8a,armeabi-v7a

android.allow_backup = True

# ===============================
# BUILDOZER
# ===============================
[buildozer]

log_level = 2
warn_on_root = 1
