import subprocess
import time
import random

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

def tap(x, y, jitter=15):
    """
    ฟังก์ชันสั่งแตะหน้าจอแบบสุ่มพิกัดรอบๆ จุดเป้าหมาย (Humanlike Tap)
    jitter=15 หมายถึง สุ่มรัศมีรอบๆ ปุ่ม +- 15 พิกเซล
    """
    # 2. สุ่มพิกัด X และ Y เบี่ยงเบนรอบๆ จุดเป้าหมาย
    offset_x = random.randint(-jitter, jitter)
    offset_y = random.randint(-jitter, jitter)
    random_x = int(x + offset_x)
    random_y = int(y + offset_y)
    # 3. สั่งกดพิกัดที่สุ่มได้
    adb_bin = find_adb_path()
    device = os.environ.get("ADB_DEVICE")
    if device:
        cmd = f'"{adb_bin}" -s {device} shell input tap {random_x} {random_y}'
    else:
        cmd = f'"{adb_bin}" shell input tap {random_x} {random_y}'
    subprocess.run(cmd, shell=True, creationflags=0x08000000)

