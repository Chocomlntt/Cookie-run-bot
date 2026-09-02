import time
from check_captcha import check_captcha
from check_popup import check_and_dismiss_popup
import cv2
import numpy as np
from tap import tap
from base_vision import get_screen, find_button

ADB_PATH = r"C:\LDPlayer\LDPlayer14\adb.exe"

def wait_until_still(get_screen_func, y1, y2, x1, x2, wait_still_sec=2.0, max_timeout_sec=10.0):
    """
    เฝ้ามองพื้นที่ (y1..y2, x1..x2) หากไม่มีการเปลี่ยนแปลงของพิกเซลติดต่อกันครบ wait_still_sec วินาที
    จะคืนค่า True เพื่อให้ทำขั้นตอนถัดไป
    """
    print(f"🔎 เริ่มเฝ้ามองโซนพื้นที่ [{y1}:{y2}, {x1}:{x2}] รอภาพนิ่งสนิท {wait_still_sec} วินาที...")
    last_frame_crop = None
    still_start_time = None
    start_wait_time = time.time()
    while True:
        # 1. เช็คว่ารอนานเกินเวลา Timeout รวมหรือไม่ (ป้องกันบอทค้าง)
        if (time.time() - start_wait_time) > max_timeout_sec:
            print(f"⚠️ รอนานเกิน {max_timeout_sec} วินาที -> ข้ามไปทำขั้นตอนถัดไป")
            return False
        # 2. ดึงภาพหน้าจอสด และตัดเฉพาะโซนพื้นที่ที่กำหนด
        screen = get_screen_func()
        if screen is None:
            time.sleep(0.1)
            continue
        h, w = screen.shape[:2]
        crop = screen[max(0, y1):min(h, y2), max(0, x1):min(w, x2)]
        
        # แปลงเป็นภาพขาวดำเพื่อคำนวณความต่างของพิกเซลได้รวดเร็ว
        gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
        # 3. ถ้าเป็นภาพแรก ให้บันทึกไว้ก่อน
        if last_frame_crop is None:
            last_frame_crop = gray
            still_start_time = time.time()
            time.sleep(0.1)
            continue
        # 4. คำนวณหาผลต่างพิกเซลระหว่างภาพก่อนหน้ากับภาพปัจจุบัน (Motion Difference)
        diff = cv2.absdiff(last_frame_crop, gray)
        _, thresh_diff = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)
        pixel_changes = np.sum(thresh_diff > 0) # นับจำนวนพิกเซลที่มีการเปลี่ยนแปลง
        last_frame_crop = gray # อัปเดตภาพล่าสุด
        # 5. ตรวจสอบว่าพิกเซลนิ่ง หรือ มีการเคลื่อนไหว
        if pixel_changes < 50: # ค่าพิกเซลเปลี่ยนน้อยมาก = ภาพนิ่งสนิท
            if still_start_time is None:
                still_start_time = time.time()
            elapsed_still = time.time() - still_start_time
            print(f"⏳ ภาพนิ่งสนิทแล้วเป็นเวลา {elapsed_still:.1f} / {wait_still_sec} วินาที...")
            # 🎯 ถ้านิ่งติดต่อกันครบตามเวลาที่ตั้งไว้ (เช่น 2.0 วินาที)
            if elapsed_still >= wait_still_sec:
                print(f"✅ ภาพในโซนหยุดนิ่งสนิทครบ {wait_still_sec} วินาทีแล้ว! -> ไปขั้นตอนถัดไป")
                return True
        else: # มีการขยับ/อนิเมชันกำลังเคลื่อนไหว -> รีเซ็ตนับเวลาใหม่!
            if still_start_time is not None:
                print(f"🔄 มีการเคลื่อนไหวของพิกเซล ({pixel_changes} px) -> รีเซ็ตเริ่มนับเวลานิ่งใหม่...")
            still_start_time = None
        time.sleep(0.1) # พักสแกนทุกๆ 0.1 วินาที

def find_play_button():
    while True:
        screen = get_screen()

        # # 🚨 1. เช็ค Captcha ระหว่างรอ
        # is_cap, _ = check_captcha(screen)
        # if is_cap:
        #     time.sleep(1.0)
        #     continue

            # 🔔 2. เช็คป๊อปอัปแจ้งเตือน/ปุ่ม X ระหว่างรอ
        popup_closed = check_and_dismiss_popup(screen)
        if popup_closed:
            time.sleep(0.5)
            continue

        pos, conf = find_button(screen, "templates/play.png")
        if pos:
            print(f"🎯 เจอพิกัดปุ่ม Play แล้วที่ X:{pos[0]}, Y:{pos[1]} (ความแม่นยำ {conf:.2f})")
            tap(pos[0],pos[1])
            break

def find_boost_box_button():
    screen = get_screen()
    pos, conf = find_button(screen, "templates/boost_box.png")
    if pos:
        print(f"🎯 เจอพิกัดปุ่ม boost box แล้วที่ X:{pos[0]}, Y:{pos[1]} (ความแม่นยำ {conf:.2f})")
        tap(pos[0],pos[1])

def find_multi_button():
    screen = get_screen()
    pos, conf = find_button(screen, "templates/multi.png")
    if pos:
        print(f"🎯 เจอพิกัดปุ่ม multi แล้วที่ X:{pos[0]}, Y:{pos[1]} (ความแม่นยำ {conf:.2f})")
        tap(pos[0],pos[1])

def find_multi_buy_button():
    screen = get_screen()
    pos, conf = find_button(screen, "templates/multi_buy.png")
    if pos:
        print(f"🎯 เจอพิกัดปุ่ม multi buy แล้วที่ X:{pos[0]}, Y:{pos[1]} (ความแม่นยำ {conf:.2f})")
        tap(pos[0],pos[1])

def find_ok_button():
    while True:
        screen = get_screen()

        # 🚨 1. เช็ค Captcha ระหว่างรอ
        is_cap, _ = check_captcha(screen)
        if is_cap:
            time.sleep(1.0)
            continue
                
        # 🔔 2. เช็คป๊อปอัปแจ้งเตือน/ปุ่ม X ระหว่างรอ
        popup_closed = check_and_dismiss_popup(screen)
        if popup_closed:
            time.sleep(0.5)
            continue
        
        pos, conf = find_button(screen, "templates/ok.png")
        if pos:
            print(f"🎯 เจอพิกัดปุ่ม ok แล้วที่ X:{pos[0]}, Y:{pos[1]} (ความแม่นยำ {conf:.2f})")
            tap(pos[0],pos[1])
            break

def find_open_all_button():
    screen = get_screen()
    pos, conf = find_button(screen, "templates/open_all.png")
    if pos:
        print(f"🎯 เจอพิกัดปุ่ม open all แล้วที่ X:{pos[0]}, Y:{pos[1]} (ความแม่นยำ {conf:.2f})")
        tap(pos[0],pos[1])
        return pos
    return None

def find_confirm_blue_button():
    while True:
        screen = get_screen()
        pos, conf = find_button(screen, "templates/confirm_blue.png")
        if pos:
            print(f"🎯 เจอพิกัดปุ่ม confirm แล้วที่ X:{pos[0]}, Y:{pos[1]} (ความแม่นยำ {conf:.2f})")
            tap(pos[0],pos[1])
            break

def find_fast_start_button():
    loop = 0
    while loop <= 20:
        tap(818,426)
        loop=loop+1

def find_reley_button():
    while True:
        screen = get_screen()
        pos, conf = find_button(screen, "templates/reley.png")
        if pos:
            print(f"🎯 เจอพิกัดปุ่ม reley แล้วที่ X:{pos[0]}, Y:{pos[1]} (ความแม่นยำ {conf:.2f})")
            tap(pos[0],pos[1])
            break

def find_play_button_2():
        screen = get_screen()
        pos, conf = find_button(screen, "templates/play.png")
        if pos:
            print(f"🎯 เจอพิกัดปุ่ม Play แล้วที่ X:{pos[0]}, Y:{pos[1]} (ความแม่นยำ {conf:.2f})")
            tap(pos[0],pos[1])

def find_reley_button_and_quit():
    while True:
        screen = get_screen()
        pos, conf = find_button(screen, "templates/reley.png")
        if pos:
            print(f"🎯 เจอพิกัดปุ่ม reley แล้วที่ X:{pos[0]}, Y:{pos[1]} (ความแม่นยำ {conf:.2f})")
            tap(pos[0],pos[1])
            time.sleep(1.0)
            tap(1494,45)
            time.sleep(0.3)
            tap(786,533)
            time.sleep(0.3)
            tap(788,475)
            break

def timer_quit(input):
    time.sleep(input)
    tap(1494,45)
    time.sleep(0.3)
    tap(786,533)
    time.sleep(0.3)
    tap(788,475)

def buy_reley():
    print("ซื้อ reley")
    tap(478,743)
    time.sleep(0.3)
    tap(1150,362)
    time.sleep(1)

def buy_fast_start():
    print("ซื้อ fast start")
    tap(268,748)
    time.sleep(0.3)
    tap(1150,362)
    time.sleep(1)