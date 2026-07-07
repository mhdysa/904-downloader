#!/bin/bash

echo "========================================="
echo "  904 Downloader - Dev Container Setup"
echo "========================================="

echo "📦 Installing system dependencies..."
sudo apt update
sudo apt install -y git zip unzip openjdk-17-jdk python3-pip autoconf libtool pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev libtinfo5 cmake libffi-dev libssl-dev

echo "📦 Installing Python packages..."
pip install --upgrade pip
pip install kivy==2.1.0 requests==2.31.0 pytube==15.0.0 buildozer cython

echo "✅ Setup complete!"
echo ""
echo "🚀 To build APK:"
echo "   buildozer android debug"
