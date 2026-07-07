#!/bin/bash

echo "========================================="
echo "  904 Downloader - APK Builder"
echo "========================================="

# نصب پیش‌نیازها
echo "📦 Installing prerequisites..."
sudo apt update
sudo apt install -y git zip unzip openjdk-17-jdk python3-pip autoconf libtool pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev libtinfo5 cmake libffi-dev libssl-dev

# نصب Buildozer
echo "📦 Installing Buildozer..."
pip3 install --user --upgrade buildozer cython

# پاکسازی build قبلی
echo "🧹 Cleaning previous builds..."
rm -rf .buildozer
rm -rf bin

# ساخت APK
echo "🔨 Building APK..."
buildozer android debug

# کپی APK به پوشه اصلی
if ls bin/*.apk 1> /dev/null 2>&1; then
    echo "✅ APK built successfully!"
    echo "📱 APK file: $(ls bin/*.apk)"
    cp bin/*.apk .
else
    echo "❌ Build failed. Check the error messages above."
    exit 1
fi
