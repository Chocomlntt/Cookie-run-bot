import time
# 📌 ดึง tap จาก Tap.py และ ดึงตา (get_screen, find_button) จาก scan.py มาใช้งาน
from scan import (find_boost_box_button,find_multi_button,find_multi_buy_button,find_play_button,
                  find_fast_start_button,wait_until_still,get_screen,find_confirm_blue_button,
                  find_ok_button,find_open_all_button,find_reley_button,find_play_button_2,find_button,
                  find_reley_button_and_quit,timer_quit,buy_reley,buy_fast_start)
from tap import tap
import random
from check_captcha import check_captcha
from check_popup import check_and_dismiss_popup,check_and_dismiss_x_popup

import json
import os

config = {
    "auto_captcha": True,
    "auto_popup": True,
    "use_fast_start": True,
    "use_relay": True,
    "buy_boost": True,
    "jump_at_start": True,
    "use_relay_quit": False,
    "use_timer_quit": False,
    "timer_sec": 19.0
}

CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'config.json')

def update_config_from_json():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                config.update(data)
        except Exception:
            pass

def main():

    print("==========================================")
    print("🚀 เริ่มทดลองรันไฟล์ใหม่ (run.py)")
    print("==========================================")

    last_state = ""
    state = ""
    loop = 0
    still = 0

    while True:
        update_config_from_json()

        frame = get_screen()
        if frame is None:
            time.sleep(0.5)
            continue
        if config["auto_captcha"]:
            is_cap, _ = check_captcha(frame)
            if is_cap:
                print(f"[{time.strftime('%H:%M:%S')}] 📍 สแกนเจอ CAPTCHA -> กำลังแก้ ")
                time.sleep(1.0)
                continue
        if config["auto_popup"]:
            if check_and_dismiss_popup(frame):
                print(f"[{time.strftime('%H:%M:%S')}] 📍 สแกนเจอ POP UP -> กำลังกด CONFIRM ")
                time.sleep(0.5)
                continue

        # print(state)

        state = ""

        lobby_pos, _   = find_button(frame, "templates/lobby.png", threshold=0.80)
        result_pos, _    = find_button(frame, "templates/result.png", threshold=0.80)
        shop_pos, _ = find_button(frame, "templates/shop.png", threshold=0.80)
        mystery_pos, _ = find_button(frame, "templates/mystery_box.png", threshold=0.80)

        if still >= 10:
            print("⚠️ ค้างหน้าเดิมนานเกินไป -> สั่งรีเซ็ตให้กดปุ่มซ้ำอีกครั้ง!")
            last_state = ""
            still = 0


        #lobby
        #-------------------------------------------------------------
        if lobby_pos:
            state = "LOBBY (หน้าหลัก)"
            if state != last_state:
                print(f"[{time.strftime('%H:%M:%S')}] 📍 สแกนเจอ LOBBY -> กำลังกด Play เข้าหน้าร้านค้า...")
                last_state = state
                print("find_play_button()")
                find_play_button()
                time.sleep(0.5)
            else:
                still = still + 1
                continue
            #-------------------------------------------------------------




        # shop & run
        #-------------------------------------------------------------
        elif shop_pos:
            state = "SHOP (หน้าร้านค้าสุ่มบัฟ)"
            if state != last_state:
                print(f"[{time.strftime('%H:%M:%S')}] 📍 สแกนเจอ SHOP -> กำลังสุ่มบัฟ...")
                last_state = state
                if config["use_fast_start"]:
                    buy_fast_start()
                if config["use_relay"]:
                    buy_reley()
                elif config["use_relay_quit"]:
                    buy_reley()
                if config["buy_boost"]:
                    find_boost_box_button()
                    time.sleep(0.5)
                    find_multi_button()
                    time.sleep(0.5)
                    find_multi_buy_button()
                    wait_until_still(get_screen,504,694,875,1387,1,10)
                find_play_button_2()
                time.sleep(4)
                if config["use_fast_start"]:
                    find_fast_start_button()
                if config["jump_at_start"]:
                    for i in range(10):
                        tap(344,463)
                        time.sleep(random.uniform(0.3,0.6))
                if config["use_relay"]:
                    find_reley_button()
                if config.get("use_timer_quit"):
                    try:
                        sec = float(config.get("timer_sec", 19.0))
                    except ValueError:
                        sec = 19.0
                    print(f"[{time.strftime('%H:%M:%S')}] ⏱️ ตั้งเวลา {sec} วินาทีแล้วกดออก...")
                    timer_quit(sec)
                elif config.get("use_relay_quit"):
                    find_reley_button_and_quit()
            else:
                still = still + 1
                continue
        #-------------------------------------------------------------


        #result
        #-------------------------------------------------------------
        elif result_pos:
            state = "RESULT (หน้าสรุปผลคะแนน)"
            if state != last_state:
                print(f"[{time.strftime('%H:%M:%S')}] 📍 สแกนเจอ RESULT -> กำลังกด OK...")
                time.sleep(1.0)
                last_state = state
                print("find_ok_button()")
                find_ok_button()
                time.sleep(1.0)
                loop = loop + 1
                print(f"[{time.strftime('%H:%M:%S')}] รอบที่ {loop} ")
            else:
                still = still + 1
                continue
        #-------------------------------------------------------------



        #mystery box
        #-------------------------------------------------------------
        elif mystery_pos:
            state = "MYSTERY BOX (หน้ากล่องสุ่ม)"
            if state != last_state:
                print(f"[{time.strftime('%H:%M:%S')}] 📍 สแกนเจอ MYSTERY BOX -> กำลังกด OPEN ALL...")
                last_state = state
                find_open_all_button()
                time.sleep(1.0)
                find_confirm_blue_button()
                time.sleep(5.0)
                loop = loop + 1
                print(f"[{time.strftime('%H:%M:%S')}] รอบที่ {loop} ")
            else:
                still = still + 1
                continue
        #-------------------------------------------------------------
        

        else:
            if check_and_dismiss_x_popup(frame):
                print(f"[{time.strftime('%H:%M:%S')}] 📍 สแกนเจอ POP UP -> กำลังกด X ")
                time.sleep(0.5)
                continue
            if check_and_dismiss_popup(frame):
                print(f"[{time.strftime('%H:%M:%S')}] 📍 สแกนเจอ POP UP -> กำลังกด CONFIRM ")
                time.sleep(0.5)
                continue



        

if __name__ == "__main__":
    main()