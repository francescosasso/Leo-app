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

# Impostiamo l'API 34 per il Play Store
android.api = 34
android.minapi = 21

# Lasciamo che buildozer scelga le versioni migliori di NDK e build-tools
android.archs = arm64-v8a
android.allow_backup = True

# Aggiungiamo questa riga per generare il file per il Play Store
android.release_artifact = aab

[buildozer]
log_level = 2
warn_on_root = 1
