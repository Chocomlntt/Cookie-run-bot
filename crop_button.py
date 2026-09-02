import cv2
import numpy as np
import subprocess

ADB_PATH = r"C:\LDPlayer\LDPlayer14\adb.exe"

def crop_with_mouse():
    # 1. ถ่ายภาพหน้าจอสดจาก LDPlayer
    cmd = f'"{ADB_PATH}" shell screencap -p'
    pipe = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, creationflags=0x08000000)
    image_bytes = pipe.stdout.read().replace(b'\r\n', b'\n')
    nparr = np.frombuffer(image_bytes, np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if frame is not None:
        print("🖱️ ใช้เมาส์ลากกรอบครอบปุ่มที่ต้องการ (ลากเสร็จแล้วกดปุ่ม Enter หรือ สเปซบาร์)...")
        # เปิดหน้าต่างให้ใช้เมาส์ลากครอบตัดรูปภาพสดๆ
        roi = cv2.selectROI("Drag mouse to crop button (Press ENTER when done)", frame, showCrosshair=True)
        cv2.destroyAllWindows()

        x, y, w, h = roi
        if w > 0 and h > 0:
            crop_img = frame[y:y+h, x:x+w]
            cv2.imwrite("templates/confirm_green_2.png", crop_img)
            print(f"✅ บันทึกรูปปุ่มคมชัด 100% เรียบร้อยแล้ว! (ขนาด {w}x{h} พิกเซล)")

if __name__ == "__main__":
    crop_with_mouse()