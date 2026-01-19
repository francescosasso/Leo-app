[app]
title = Leo
package.name = leo
package.domain = org.sassofrancesco

source.dir = .
source.include_exts = py,png,jpg,json

version = 1.6

requirements = python3,kivy,requests,plyer

orientation = portrait
fullscreen = 0

icon.filename = icon.png

android.permissions = INTERNET

# 🔴 QUI È LA CHIAVE
android.api = 30
android.minapi = 24

android.archs = arm64-v8a,armeabi-v7a
android.allow_backup = True

[buildozer]
log_level = 2
warn_on_root = 1
