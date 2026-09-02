import time
from tap import tap
from base_vision import get_screen, find_button

def check_and_dismiss_popup(screen=None):
    """
    สแกนหาป๊อปอัปแจ้งเตือน / ปุ่มปิด X / ปุ่ม Confirm เช็คอิน อย่างเดียว
    หากเจอจะกดปิดให้อัตโนมัติทันที
    """
    if screen is None:
        screen = get_screen()

    # 1. เช็คปุ่ม Confirm / OK หน้าเช็คอิน / ป๊อปอัปทั่วไป
    conf_pos, c_score = find_button(screen, "templates/confirm_green.png", threshold=0.80)
    if not conf_pos:
        conf_pos, c_score = find_button(screen, "templates/cancle.png", threshold=0.80)

    if conf_pos:
        print(f"🔔 🎯 เจอป๊อปอัป Confirm/OK ที่พิกัด {conf_pos} (conf: {c_score:.2f}) -> สั่งกดตกลง")
        tap(conf_pos[0], conf_pos[1])
        time.sleep(0.8) # พักรอป๊อปอัปปิด
        return True

    conf_pos, c_score = find_button(screen, "templates/confirm_green_2.png", threshold=0.80)
    if not conf_pos:
        conf_pos, c_score = find_button(screen, "templates/cancle.png", threshold=0.80)

    if conf_pos:
        print(f"🔔 🎯 เจอป๊อปอัป Confirm/OK ที่พิกัด {conf_pos} (conf: {c_score:.2f}) -> สั่งกดตกลง")
        tap(conf_pos[0], conf_pos[1])
        time.sleep(0.8) # พักรอป๊อปอัปปิด
        return True

    return False

def check_and_dismiss_x_popup(screen=None):
    """
    สแกนหาป๊อปอัปแจ้งเตือน / ปุ่มปิด X / ปุ่ม Confirm เช็คอิน อย่างเดียว
    หากเจอจะกดปิดให้อัตโนมัติทันที
    """
    if screen is None:
        screen = get_screen()
    # 2. เช็คปุ่มปิด X มุมป๊อปอัป
    close_x, x_score = find_button(screen, "templates/close_x.png", threshold=0.85)
    if close_x:
        print(f"✖️ 🎯 เจอปุ่มปิด X ที่พิกัด {close_x} (conf: {x_score:.2f}) -> สั่งกดปิด X")
        tap(close_x[0], close_x[1])
        time.sleep(0.8) # พักรอป๊อปอัปปิด
        return True

    return False

    # # 2. เช็คปุ่มปิด X มุมป๊อปอัป (พร้อมระบบกันกดโดนปุ่มตั้งค่า)
    #     close_x, x_score = find_button(screen, "templates/close_x.png", threshold=0.75)
    #     if close_x:
    #         # 📌 เพิ่มเงื่อนไขนี้: ถ้าพิกัดไม่อยู่มุมขวาบนสุด (X > 1300 และ Y < 150) ค่อยสั่งกดปิด
    #         if not (close_x[0] > 1300 and close_x[1] < 150):
    #             print(f"✖️ 🎯 เจอปุ่มปิด X ที่พิกัด {close_x} (conf: {x_score:.2f}) -> สั่งกดปิด X")
    #             tap(close_x[0], close_x[1])
    #             time.sleep(0.8) # พักรอป๊อปอัปปิด
    #             return True
    #         else:
    #             print("⚠️ [Safety Guard] ข้ามการกด X เนื่องจากตรงกับตำแหน่งปุ่มตั้งค่ามุมขวาบนสุด")

