@echo off
chcp 65001 > nul
title CookieRun AutoBot Launcher & Auto-Updater
echo ==================================================
echo 🔄 กำลังตรวจสอบและดึงอัปเดตโค้ดล่าสุดจาก GitHub...
echo ==================================================
git pull
echo.
echo ✅ อัปเดตเสร็จเรียบร้อย! กำลังเปิดโปรแกรม...
python gui_bot.py
