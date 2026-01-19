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

# 🔴 FONDAMENTALE: API 30 (NO AIDL)
android.api = 30
android.minapi = 21

# NON specificare NDK → buildozer sceglie quello giusto
# NON specificare build-tools

android.archs = arm64-v8a

android.allow_backup = True


[buildozer]
log_level = 2
warn_on_root = 1
