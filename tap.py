import subprocess
import time
import random

import os

# กำหนดที่อยู่ของ adb.exe ในเครื่องคุณ
ADB_PATH = r"C:\LDPlayer\LDPlayer14\adb.exe"

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
    device = os.environ.get("ADB_DEVICE")
    if device:
        cmd = f'"{ADB_PATH}" -s {device} shell input tap {random_x} {random_y}'
    else:
        cmd = f'"{ADB_PATH}" shell input tap {random_x} {random_y}'
    subprocess.run(cmd, shell=True, creationflags=0x08000000)

