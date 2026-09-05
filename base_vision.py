import cv2
import numpy as np
import subprocess

import os

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

def get_screen():
    """ดึงภาพหน้าจอสดจาก LDPlayer เข้ามาใน Python"""
    adb_bin = find_adb_path()
    device = os.environ.get("ADB_DEVICE")
    if device:
        cmd = f'"{adb_bin}" -s {device} shell screencap -p'
    else:
        cmd = f'"{adb_bin}" shell screencap -p'
    pipe = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, creationflags=0x08000000)
    image_bytes = pipe.stdout.read().replace(b'\r\n', b'\n')
    
    nparr = np.frombuffer(image_bytes, np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return frame

def find_button(screen_frame, template_path, threshold=0.85):
    """สแกนหาตำแหน่งปุ่ม คืนค่า (X, Y) ศูนย์กลางของปุ่ม และความแม่นยำ (0.0 - 1.0)"""
    template = cv2.imread(template_path)
    if screen_frame is None or template is None:
        return None, 0.0

    # ค้นหาภาพเป้าหมายในหน้าจอ
    result = cv2.matchTemplate(screen_frame, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

    if max_val >= threshold:
        h, w = template.shape[:2]
        # คำนวณจุดศูนย์กลางของปุ่ม
        center_x = max_loc[0] + (w // 2)
        center_y = max_loc[1] + (h // 2)
        return (center_x, center_y), max_val

    return None, max_val

def find_button_in_region(screen_frame, template_path, y1, y2, x1, x2, threshold=0.85):
    if screen_frame is None:
        return None, 0.0
    # ตัดเอาเฉพาะโซนภาพที่ต้องการสแกน [Y_บน : Y_ล่าง , X_ซ้าย : X_ขวา]
    crop_zone = screen_frame[y1:y2, x1:x2]
    pos, max_val = find_button(crop_zone, template_path, threshold)
    # แปลงพิกัดกลับมาเป็นพิกัดหน้าจอจริง
    if pos is not None:
        real_x = pos[0] + x1
        real_y = pos[1] + y1
        return (real_x, real_y), max_val
    return None, max_val
