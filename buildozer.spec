[app]

# اطلاعات برنامه
title = 904 Downloader
package.name = downloader904
package.domain = org.downloader

# نسخه
version = 1.0.0

# فایل‌های منبع
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
source.exclude_exts = spec,pyc,pyo,pyd,db,db-journal,apk,aab,dex,class

# کتابخانه‌های مورد نیاز
requirements = python3,kivy==2.1.0,requests==2.31.0,pytube==15.0.0

# تنظیمات نمایش
orientation = portrait
fullscreen = 0

# آیکون
icon.filename = icon.ico

# لوگوی splash screen
presplash.filename = logo.png

# مجوزهای اندروید
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,FOREGROUND_SERVICE,ACCESS_NETWORK_STATE

android.api = 30
android.minapi = 21
android.ndk = 23b
android.sdk = 30

android.gradle_dependencies = 
android.enable_androidx = True
android.allow_backup = True
android.uses_cleartext_traffic = True

# متادیتا
android.meta_data = 
android.app_library = True

# تنظیمات iOS
ios.kivy_ios_version = 2021.1
ios.deployment_target = 13.0
ios.pods = 

# تنظیمات دیگر
win_icon = icon.ico
