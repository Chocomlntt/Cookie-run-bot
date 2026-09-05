@echo off
chcp 65001 > nul
title CookieRun AutoBot Launcher & Auto-Updater
echo ==================================================
echo 🔄 กำลังตรวจสอบและดึงอัปเดตโค้ดล่าสุดจาก GitHub...
echo ==================================================
git pull
echo.
echo 📦 กำลังตรวจสอบและติดตั้งไลบรารีที่จำเป็นอัตโนมัติ...
pip install customtkinter opencv-python pillow numpy
echo.
echo ✅ พร้อมใช้งาน! กำลังเปิดโปรแกรม...
python gui_bot.py
