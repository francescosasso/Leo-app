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

# ---------------- ANDROID ----------------
android.api = 33
android.minapi = 21
android.ndk_version = 25.2.9519653
android.build_tools_version = 33.0.2

android.archs = arm64-v8a,armeabi-v7a

android.allow_backup = True
android.enable_androidx = True

# ---------------- FIX KIVY (CRITICO) ----------------
# Disabilita completamente pygame
android.disable_pygame = True

# Escludi TUTTI i provider NON Android
android.blacklist_src = \
    **/pygame/**,\
    **/audio_pygame.py,\
    **/camera/**,\
    **/camera_picamera.py,\
    **/camera_opencv.py,\
    **/img_dds.py,\
    **/img_ffpyplayer.py,\
    **/ffpyplayer/**

# Forza uso provider Android
android.add_jars = android-support-v4.jar

[buildozer]
log_level = 2
warn_on_root = 1
