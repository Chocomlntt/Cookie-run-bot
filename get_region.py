import cv2
import numpy as np
import subprocess

ADB_PATH = r"C:\LDPlayer\LDPlayer14\adb.exe"

def main():
    print("==================================================")
    print("📸 กำลังถ่ายภาพหน้าจอจาก LDPlayer...")
    print("==================================================")

    # 1. ถ่ายภาพหน้าจอสดจาก LDPlayer
    try:
        cmd = f'"{ADB_PATH}" shell screencap -p'
        pipe = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        image_bytes = pipe.stdout.read().replace(b'\r\n', b'\n')
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if img is None:
            print("❌ ไม่สามารถดึงภาพหน้าจอได้ กรุณาเช็คว่าเปิด LDPlayer อยู่หรือไม่")
            return

        print("🖱️ ใช้เมาส์ลากคลุมกรอบพื้นที่โซนที่ต้องการสแกน...")
        print("👉 เมื่อลากคลุมเสร็จแล้ว ให้กดปุ่ม ENTER หรือ Spacebar")

        # 2. เปิดหน้าต่างให้ใช้เมาส์ลากคลุมพื้นที่ (ROI)
        window_name = "Drag mouse to select region (Press ENTER when done)"
        roi = cv2.selectROI(window_name, img, showCrosshair=True)
        cv2.destroyAllWindows()

        x, y, w, h = roi

        # 3. คำนวณค่า x1, x2, y1, y2
        if w > 0 and h > 0:
            x1 = x
            x2 = x + w
            y1 = y
            y2 = y + h

            print("\n==================================================")
            print("🎉 คำนวณพิกัดขอบเขตโซนพื้นที่ (ROI) เรียบร้อยแล้ว!")
            print("==================================================")
            print(f"📍 y1 (ขอบบน)   = {y1}")
            print(f"📍 y2 (ขอบล่าง)  = {y2}")
            print(f"📍 x1 (ขอบซ้าย)  = {x1}")
            print(f"📍 x2 (ขอบขวา)  = {x2}")
            print("--------------------------------------------------")
            print("📋 โค้ดสำหรับก๊อปปี้ไปใช้งานได้ทันที:")
            print(f'find_button_in_region(frame, "templates/btn.png", y1={y1}, y2={y2}, x1={x1}, x2={x2})')
            print("==================================================\n")
        else:
            print("❌ ไม่ได้เลือกพื้นที่")

    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")

if __name__ == "__main__":
    main()