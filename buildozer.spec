[app]
title = 本地音频播放器
package.name = localaudioplayer
package.domain = org.audioplayer
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json
version = 1.0

requirements = python3,kivy==2.3.0,kivymd==1.2.0,plyer,android,pyjnius,certifi

orientation = portrait
fullscreen = 0
android.permissions = READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,READ_MEDIA_AUDIO,FOREGROUND_SERVICE,WAKE_LOCK
android.api = 33
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a, armeabi-v7a
android.accept_sdk_license = True

ios.kivy_ios_url = https://github.com/kivy/kivy-ios
ios.kivy_ios_branch = master
ios.ios_deploy_url = https://github.com/phonegap/ios-deploy
ios.ios_deploy_branch = 1.10.0
ios.codesign.allowed = no

[buildozer]
log_level = 2
warn_on_root = 1
