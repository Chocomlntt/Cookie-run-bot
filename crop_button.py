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

def crop_with_mouse(filename="confirm_green_2.png"):
    # 1. ถ่ายภาพหน้าจอสดจาก LDPlayer
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

    if frame is not None:
        print("🖱️ ใช้เมาส์ลากกรอบครอบปุ่มที่ต้องการ (ลากเสร็จแล้วกดปุ่ม Enter หรือ สเปซบาร์)...")
        roi = cv2.selectROI("Drag mouse to crop button (Press ENTER when done)", frame, showCrosshair=True)
        cv2.destroyAllWindows()

        x, y, w, h = roi
        if w > 0 and h > 0:
            crop_img = frame[y:y+h, x:x+w]
            if not filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                filename += ".png"
            os.makedirs("templates", exist_ok=True)
            save_path = os.path.join("templates", os.path.basename(filename))
            cv2.imwrite(save_path, crop_img)
            print(f"✅ บันทึกรูปปุ่ม '{save_path}' คมชัด 100% เรียบร้อยแล้ว! (ขนาด {w}x{h} พิกเซล)")
            return save_path
    return None

if __name__ == "__main__":
    crop_with_mouse()