import cv2
import numpy as np
import subprocess
import os
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def find_adb_path():
    local_adb = os.path.join(os.path.dirname(__file__), "adb_tools", "adb.exe")
    if os.path.exists(local_adb):
        return local_adb
    candidates = [
        r"C:\LDPlayer\LDPlayer14\adb.exe",
        r"C:\LDPlayer\LDPlayer9\adb.exe",
        r"C:\LDPlayer\LDPlayer4.0\adb.exe",
        r"D:\LDPlayer\LDPlayer14\adb.exe",
        r"D:\LDPlayer\LDPlayer9\adb.exe",
        r"E:\LDPlayer\LDPlayer14\adb.exe",
    ]
    for path in candidates:
        if os.path.exists(path):
            return path
    return "adb"

ADB_PATH = find_adb_path()

def click_event(event, x, y, flags, param):
    """เมื่อคลิกเมาส์ซ้าย จะปริ้นท์พิกัดทันทีแล้วปิดหน้าต่าง"""
    if event == cv2.EVENT_LBUTTONDOWN:
        print("\n==================================================")
        print(f"🎯 พิกัดที่คุณคลิก -> X: {x}, Y: {y}")
        print("--------------------------------------------------")
        print(f"📋 โค้ดสำหรับก๊อปปี้ไปใช้ -> tap({x}, {y})")
        print("==================================================\n")
        cv2.destroyAllWindows()

def main():
    print("📸 กำลังถ่ายภาพหน้าจอสด...")
    adb_bin = find_adb_path()
    device = os.environ.get("ADB_DEVICE")
    if device:
        cmd = f'"{adb_bin}" -s {device} shell screencap -p'
    else:
        cmd = f'"{adb_bin}" shell screencap -p'
    pipe = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, creationflags=0x08000000)
    image_bytes = pipe.stdout.read().replace(b'\r\n', b'\n')
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if img is not None:
        window_name = "Click ONCE to get X, Y coordinate"
        print("🖱️ เอาเมาส์คลิก 1 ครั้งตรงจุดที่ต้องการดูพิกัดได้เลยครับ...")
        cv2.imshow(window_name, img)
        cv2.setMouseCallback(window_name, click_event)
        cv2.waitKey(0)

if __name__ == "__main__":
    main()