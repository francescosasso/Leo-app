[app]
title = Leo
package.name = leo
package.domain = org.sassofrancesco
version = 1.6

source.dir = .
source.include_exts = py,png,jpg,json

requirements = python3,kivy,requests,openssl

orientation = portrait
fullscreen = 0
icon.filename = icon.png

android.permissions = INTERNET

# ANDROID
android.api = 33
android.minapi = 21
android.ndk_version = 25.2.9519653
android.build_tools_version = 33.0.2

android.archs = arm64-v8a,armeabi-v7a

android.allow_backup = True
android.enable_androidx = True

# 🔥 DISABILITA MODULI NON SUPPORTATI SU ANDROID
android.disable_pygame = True

# 🔥 ESCLUDI PROVIDER VIDEO / IMAGE PROBLEMATICI
android.blacklist_src = \
    **/audio_pygame.py,\
    **/camera,\
    **/pygame,\
    **/ffpyplayer,\
    **/img_dds.py,\
    **/img_ffpyplayer.py

[buildozer]
log_level = 2
warn_on_root = 1
