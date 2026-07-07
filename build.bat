@echo off
echo =========================================
echo   904 Downloader - APK Builder (Windows)
echo =========================================

echo Installing prerequisites...
pip install --upgrade buildozer cython

echo Cleaning previous builds...
if exist .buildozer rmdir /s /q .buildozer
if exist bin rmdir /s /q bin

echo Building APK...
buildozer android debug

if exist bin\*.apk (
    echo ✅ APK built successfully!
    copy bin\*.apk .
    dir *.apk
) else (
    echo ❌ Build failed. Check the error messages above.
)
