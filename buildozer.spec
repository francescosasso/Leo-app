[app]
title = Leo
package.name = leo
package.domain = org.sassofrancesco

source.dir = .
source.include_exts = py,png,jpg,json

version = 1.6

requirements = python3,kivy,requests

orientation = portrait
fullscreen = 0

icon.filename = icon.png

android.permissions = INTERNET

# -------------------------
# ANDROID (VERSIONI STABILI)
# -------------------------

android.api = 33
android.minapi = 21

android.ndk_version = 25.2.9519653
android.build_tools_version = 33.0.2

android.archs = arm64-v8a

android.allow_backup = True
android.enable_androidx = True

# -------------------------
# BUILD / LOG
# -------------------------

[buildozer]
log_level = 2
warn_on_root = 1
