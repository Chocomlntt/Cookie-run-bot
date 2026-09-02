import cv2
import numpy as np
import subprocess

ADB_PATH = r"C:\LDPlayer\LDPlayer14\adb.exe"

def click_event(event, x, y, flags, param):
    """เมื่อคลิกเมาส์ซ้าย จะปริ้นท์พิกัดทันทีแล้วปิดหน้าต่าง"""
    if event == cv2.EVENT_LBUTTONDOWN:
        print("\n==================================================")
        print(f"🎯 พิกัดที่คุณคลิก -> X: {x}, Y: {y}")
        print("--------------------------------------------------")
        print(f"📋 โค้ดสำหรับก๊อปปี้ไปใช้ -> tap({x}, {y})")
        print("==================================================\n")
        # ปิดหน้าต่างทันทีหลังจากคลิก
        cv2.destroyAllWindows()

def main():
    print("📸 กำลังถ่ายภาพหน้าจอสด...")
    cmd = f'"{ADB_PATH}" shell screencap -p'
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