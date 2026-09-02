import json
import os
import subprocess
import sys
import threading
import time
from tkinter import filedialog
import tkinter as tk
import customtkinter as ctk
from PIL import Image, ImageTk

ctk.set_appearance_mode('Dark')
ctk.set_default_color_theme('blue')

CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'config.json')
PROFILES_FILE = os.path.join(os.path.dirname(__file__), 'profiles.json')

DEFAULT_PROFILES = {
    "active": "Default Mode",
    "profiles": {
        "Default Mode": {
            "images": [],
            "auto_captcha": True,
            "auto_popup": True,
            "use_fast_start": True,
            "use_relay": True,
            "buy_boost": True,
            "jump_at_start": True,
            "use_relay_quit": False,
            "use_timer_quit": False,
            "timer_sec": 19.0
        },
        "EXP Farming Ep 6 (19 วิ)": {
            "images": [],
            "auto_captcha": True,
            "auto_popup": True,
            "use_fast_start": True,
            "use_relay": False,
            "buy_boost": False,
            "jump_at_start": True,
            "use_relay_quit": False,
            "use_timer_quit": True,
            "timer_sec": 19.0
        },
        "Box Farming Ep 2 (140 วิ)": {
            "images": [],
            "auto_captcha": True,
            "auto_popup": True,
            "use_fast_start": True,
            "use_relay": False,
            "buy_boost": False,
            "jump_at_start": True,
            "use_relay_quit": False,
            "use_timer_quit": True,
            "timer_sec": 140.0
        }
    }
}

class CookieBotGUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title('CookieRun AutoBot Control Panel')
        self.geometry('540x840')
        self.resizable(False, False)

        self.is_running = False
        self.bot_process = None
        self.profile_data = self.load_profiles_file()
        self.current_profile_images = []

        # Header Title
        self.title_label = ctk.CTkLabel(
            self, 
            text='CookieRun AutoBot', 
            font=ctk.CTkFont(size=22, weight='bold')
        )
        self.title_label.pack(pady=(10, 0))

        self.status_label = ctk.CTkLabel(
            self, 
            text='Status: STOPPED', 
            font=ctk.CTkFont(size=13, weight='bold'),
            text_color='#FF5555'
        )
        self.status_label.pack(pady=(0, 2))

        # Main Tabview (2 Pages)
        self.tabview = ctk.CTkTabview(self, width=510, height=760)
        self.tabview.pack(padx=15, pady=(0, 10))

        self.tab_main   = self.tabview.add('🤖 บอท & การตั้งค่า')
        self.tab_images = self.tabview.add('🖼️ ภาพประกอบประจำเซ็ท')

        # ==========================================
        # TAB 1: 🤖 บอท & การตั้งค่า (Controls + Switches + Log)
        # ==========================================
        # Start/Stop Buttons
        self.btn_frame = ctk.CTkFrame(self.tab_main)
        self.btn_frame.pack(pady=4, padx=10, fill='x')

        self.btn_start = ctk.CTkButton(
            self.btn_frame, 
            text='▶️ START BOT', 
            fg_color='#2FA572', 
            hover_color='#1E7A52',
            font=ctk.CTkFont(size=14, weight='bold'),
            command=self.start_bot
        )
        self.btn_start.pack(side='left', expand=True, padx=8, pady=6)

        self.btn_stop = ctk.CTkButton(
            self.btn_frame, 
            text='⏸️ STOP BOT', 
            fg_color='#D32F2F', 
            hover_color='#9A0007',
            font=ctk.CTkFont(size=14, weight='bold'),
            state='disabled',
            command=self.stop_bot
        )
        self.btn_stop.pack(side='right', expand=True, padx=8, pady=6)

        # Profile Selection Bar
        self.profile_frame = ctk.CTkFrame(self.tab_main)
        self.profile_frame.pack(pady=4, padx=10, fill='x')

        self.lbl_profile = ctk.CTkLabel(
            self.profile_frame, 
            text='📁 เซ็ท:', 
            font=ctk.CTkFont(size=13, weight='bold')
        )
        self.lbl_profile.pack(side='left', padx=(10, 3), pady=5)

        profile_names = list(self.profile_data['profiles'].keys())
        active_prof = self.profile_data.get('active', profile_names[0])
        if active_prof not in profile_names:
            active_prof = profile_names[0]

        self.profile_menu = ctk.CTkOptionMenu(
            self.profile_frame, 
            values=profile_names, 
            command=self.on_select_profile,
            width=160
        )
        self.profile_menu.set(active_prof)
        self.profile_menu.pack(side='left', padx=3, pady=5)

        self.btn_save_prof = ctk.CTkButton(
            self.profile_frame, 
            text='💾 บันทึก', 
            width=50, 
            command=self.save_active_profile
        )
        self.btn_save_prof.pack(side='left', padx=2, pady=5)

        self.btn_add_prof = ctk.CTkButton(
            self.profile_frame, 
            text='➕ เพิ่มเซ็ท', 
            width=65, 
            command=self.add_new_profile
        )
        self.btn_add_prof.pack(side='left', padx=2, pady=5)

        self.btn_del_prof = ctk.CTkButton(
            self.profile_frame, 
            text='🗑️', 
            width=30, 
            fg_color='#D32F2F', 
            hover_color='#9A0007',
            command=self.delete_active_profile
        )
        self.btn_del_prof.pack(side='left', padx=2, pady=5)

        # Switches Option Frame
        self.option_frame = ctk.CTkFrame(self.tab_main)
        self.option_frame.pack(pady=4, padx=10, fill='x')

        self.opt_title = ctk.CTkLabel(
            self.option_frame, 
            text='⚙️ สวิตช์ตั้งค่าบอท (8 สวิตช์):', 
            font=ctk.CTkFont(size=13, weight='bold')
        )
        self.opt_title.pack(anchor='w', padx=15, pady=(6, 2))

        # Switch 1: Captcha
        self.switch_captcha = ctk.CTkSwitch(
            self.option_frame, text='🛡️ auto_captcha (แก้บอทเช็ค)', 
            command=self.sync_config
        )
        self.switch_captcha.pack(anchor='w', padx=20, pady=2)

        # Switch 2: Popups
        self.switch_popup = ctk.CTkSwitch(
            self.option_frame, text='🔔 auto_popup (เคลียร์ Pop-up)', 
            command=self.sync_config
        )
        self.switch_popup.pack(anchor='w', padx=20, pady=2)

        # Switch 3: Fast Start
        self.switch_fast_start = ctk.CTkSwitch(
            self.option_frame, text='🚀 use_fast_start (พุ่งตัว Fast Start)', 
            command=self.sync_config
        )
        self.switch_fast_start.pack(anchor='w', padx=20, pady=2)

        # Switch 4: Relay Cookie
        self.switch_relay = ctk.CTkSwitch(
            self.option_frame, text='🏃 use_relay (วิ่งคุกกี้ผลัด 2)', 
            command=self.on_toggle_relay
        )
        self.switch_relay.pack(anchor='w', padx=20, pady=2)

        # Switch 5: Buy Boost
        self.switch_boost = ctk.CTkSwitch(
            self.option_frame, text='🛒 buy_boost (สุ่มกล่องบัฟ)', 
            command=self.sync_config
        )
        self.switch_boost.pack(anchor='w', padx=20, pady=2)

        # Switch 6: Jump at Start
        self.switch_jump = ctk.CTkSwitch(
            self.option_frame, text='🦘 jump_at_start (กระโดดรัวๆ ตอนเริ่ม)', 
            command=self.sync_config
        )
        self.switch_jump.pack(anchor='w', padx=20, pady=2)

        # Switch 7: Relay Quit
        self.switch_relay_quit = ctk.CTkSwitch(
            self.option_frame, text='🏁 use_relay_quit (ผลัด 2 แล้วกดออก)', 
            command=self.on_toggle_relay_quit
        )
        self.switch_relay_quit.pack(anchor='w', padx=20, pady=2)

        # Switch 8: Timer Quit Frame
        self.timer_frame = ctk.CTkFrame(self.option_frame, fg_color="transparent")
        self.timer_frame.pack(anchor='w', padx=20, pady=(2, 6), fill='x')

        self.switch_timer_quit = ctk.CTkSwitch(
            self.timer_frame, text='⏱️ use_timer_quit (จับเวลาแล้วออก)', 
            command=self.on_toggle_timer_quit
        )
        self.switch_timer_quit.pack(side='left')

        self.lbl_sec = ctk.CTkLabel(self.timer_frame, text='เวลา (วิ):', font=ctk.CTkFont(size=12))
        self.lbl_sec.pack(side='left', padx=(15, 5))

        self.entry_timer_sec = ctk.CTkEntry(self.timer_frame, width=70, placeholder_text='19.0')
        self.entry_timer_sec.insert(0, '19.0')
        self.entry_timer_sec.pack(side='left', padx=2)
        self.entry_timer_sec.bind('<KeyRelease>', lambda e: self.sync_config())

        # Log Display Window
        self.log_box = ctk.CTkTextbox(self.tab_main, width=475, height=180, font=ctk.CTkFont(size=12))
        self.log_box.pack(pady=6, padx=10)

        # Build Right-Click Context Menu for Log Box
        self.context_menu = tk.Menu(self, tearoff=0, bg="#2B2B2B", fg="white", activebackground="#1F6AA5", activeforeground="white")
        self.context_menu.add_command(label="📋 คัดลอก (Copy) - Ctrl+C", command=self.copy_selection)
        self.context_menu.add_command(label="📋 คัดลอกทั้งหมด (Copy All)", command=self.copy_all_logs)

        for w in (self.log_box, getattr(self.log_box, '_textbox', None)):
            if w:
                w.bind('<Control-c>', self.copy_selection)
                w.bind('<Control-C>', self.copy_selection)
                w.bind('<<Copy>>', self.copy_selection)
                w.bind('<Button-3>', self.show_context_menu)

        # ==========================================
        # TAB 2: 🖼️ ภาพประกอบประจำเซ็ท (Smooth Fast Scroll without Ghosting)
        # ==========================================
        self.img_header_frame = ctk.CTkFrame(self.tab_images)
        self.img_header_frame.pack(pady=6, padx=10, fill='x')

        self.lbl_img_header = ctk.CTkLabel(
            self.img_header_frame, 
            text='🖼️ ภาพประกอบประจำเซ็ท (1 รูปต่อ 1 แถว):', 
            font=ctk.CTkFont(size=13, weight='bold')
        )
        self.lbl_img_header.pack(side='left', padx=10, pady=6)

        self.btn_add_img = ctk.CTkButton(
            self.img_header_frame, 
            text='➕ เพิ่มรูปภาพ', 
            fg_color='#2FA572', 
            hover_color='#1E7A52',
            font=ctk.CTkFont(size=12, weight='bold'),
            width=110,
            command=self.add_images_to_profile
        )
        self.btn_add_img.pack(side='right', padx=10, pady=6)

        # Scrollable Frame with Native Double-Buffered Image Labels (Zero Ghosting)
        self.scrollable_img_frame = ctk.CTkScrollableFrame(self.tab_images, width=470, height=640)
        self.scrollable_img_frame.pack(pady=5, padx=10, fill='both', expand=True)

        self.log_safe('Welcome to CookieRun AutoBot GUI!')

        # Apply active profile settings to UI
        self.apply_profile_to_switches(active_prof)

    def add_images_to_profile(self):
        """เปิด Dialog เลือกรูปภาพได้ไม่จำกัดจำนวน และเพิ่มเข้าเซ็ทปัจจุบัน"""
        file_paths = filedialog.askopenfilenames(
            title="เลือกรูปภาพประกอบประจำเซ็ท (เลือกได้หลายรูป)",
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.webp"), ("All Files", "*.*")]
        )
        if file_paths:
            active = self.profile_menu.get()
            added_count = 0
            for fp in file_paths:
                if fp not in self.current_profile_images:
                    self.current_profile_images.append(fp)
                    added_count += 1

            if active in self.profile_data['profiles']:
                self.profile_data['profiles'][active]['images'] = self.current_profile_images.copy()
                self.save_profiles_file()

            self.update_image_previews()
            self.log_safe(f"🖼️ เพิ่มรูปภาพจำนวน {added_count} รูปเข้าเซ็ท '{active}' เรียบร้อยแล้ว")

    def remove_image_at_index(self, idx):
        """ลบรูปภาพตามลำดับ Index ออกจากเซ็ท"""
        if 0 <= idx < len(self.current_profile_images):
            removed_path = self.current_profile_images.pop(idx)
            active = self.profile_menu.get()
            if active in self.profile_data['profiles']:
                self.profile_data['profiles'][active]['images'] = self.current_profile_images.copy()
                self.save_profiles_file()

            self.update_image_previews()
            self.log_safe(f"🗑️ ลบรูปภาพ '{os.path.basename(removed_path)}' ออกจากเซ็ทเรียบร้อยแล้ว")

    def update_image_previews(self):
        """เรนเดอร์ภาพแบบ Native tk.Label + ImageTk.PhotoImage ลื่นไหล 100% ไร้ภาพค้างติดตา"""
        for child in self.scrollable_img_frame.winfo_children():
            child.destroy()

        if not self.current_profile_images:
            lbl_empty = ctk.CTkLabel(
                self.scrollable_img_frame, 
                text="📷 ยังไม่มีรูปภาพในเซ็ทนี้\nกดปุ่ม '➕ เพิ่มรูปภาพ' ด้านบนเพื่อเลือกรูปภาพประกอบได้ไม่จำกัด",
                font=ctk.CTkFont(size=13),
                text_color="#888888"
            )
            lbl_empty.pack(pady=40)
            return

        for idx, img_path in enumerate(self.current_profile_images):
            card = ctk.CTkFrame(self.scrollable_img_frame)
            card.pack(pady=6, padx=6, fill='x')

            # Top header of card
            card_top = ctk.CTkFrame(card, fg_color="transparent")
            card_top.pack(fill='x', padx=8, pady=(6, 2))

            lbl_no = ctk.CTkLabel(
                card_top, 
                text=f"รูปที่ {idx+1}: {os.path.basename(img_path)}", 
                font=ctk.CTkFont(size=12, weight='bold')
            )
            lbl_no.pack(side='left')

            btn_del = ctk.CTkButton(
                card_top, 
                text="🗑️ ลบรูปนี้", 
                width=80, 
                height=24,
                fg_color="#D32F2F", 
                hover_color="#9A0007",
                font=ctk.CTkFont(size=11),
                command=lambda i=idx: self.remove_image_at_index(i)
            )
            btn_del.pack(side='right')

            # Native tk.Label image rendering for 60fps smooth scrolling without ghosting
            if img_path and os.path.exists(img_path):
                try:
                    pil_img = Image.open(img_path)
                    orig_w, orig_h = pil_img.size
                    disp_w = 420
                    disp_h = int((orig_h / orig_w) * disp_w) if orig_w > 0 else 240
                    if disp_h > 300:
                        disp_h = 300

                    resized_img = pil_img.resize((disp_w, disp_h), Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(resized_img)

                    img_lbl = tk.Label(card, image=photo, bg='#2B2B2B', bd=0, highlightthickness=0)
                    img_lbl.image = photo  # Prevent garbage collection
                    img_lbl.pack(pady=(2, 8), padx=8)
                except Exception:
                    err_lbl = ctk.CTkLabel(card, text=f"⚠️ ไม่สามารถเปิดรูปภาพนี้ได้ (ไฟล์อาจถูกลบหรือย้าย)", text_color="#FF5555")
                    err_lbl.pack(pady=15)
            else:
                err_lbl = ctk.CTkLabel(card, text=f"⚠️ ไม่พบไฟล์รูปภาพในเครื่องตามพาธนี้", text_color="#FF5555")
                err_lbl.pack(pady=15)

    def load_profiles_file(self):
        if os.path.exists(PROFILES_FILE):
            try:
                with open(PROFILES_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        return DEFAULT_PROFILES.copy()

    def save_profiles_file(self):
        try:
            with open(PROFILES_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.profile_data, f, indent=4, ensure_ascii=False)
        except Exception:
            pass

    def apply_profile_to_switches(self, profile_name):
        prof = self.profile_data['profiles'].get(profile_name)
        if not prof:
            return

        switches = [
            (self.switch_captcha, 'auto_captcha'),
            (self.switch_popup, 'auto_popup'),
            (self.switch_fast_start, 'use_fast_start'),
            (self.switch_relay, 'use_relay'),
            (self.switch_boost, 'buy_boost'),
            (self.switch_jump, 'jump_at_start'),
            (self.switch_relay_quit, 'use_relay_quit'),
            (self.switch_timer_quit, 'use_timer_quit')
        ]

        for sw, key in switches:
            if prof.get(key, False if key == 'use_timer_quit' else True):
                sw.select()
            else:
                sw.deselect()

        sec_val = str(prof.get('timer_sec', '19.0'))
        self.entry_timer_sec.delete(0, 'end')
        self.entry_timer_sec.insert(0, sec_val)

        # Load images list for this profile
        self.current_profile_images = prof.get('images', [])
        self.update_image_previews()

        self.sync_config()
        self.log_safe(f"📁 โหลดเซ็ทการตั้งค่า: '{profile_name}'")

    def on_select_profile(self, selected_profile):
        self.profile_data['active'] = selected_profile
        self.save_profiles_file()
        self.apply_profile_to_switches(selected_profile)

    def save_active_profile(self):
        active = self.profile_menu.get()
        self.profile_data['profiles'][active] = self.get_current_switches_dict()
        self.profile_data['active'] = active
        self.save_profiles_file()
        self.log_safe(f"💾 บันทึกค่าลงเซ็ท '{active}' เรียบร้อยแล้ว")

    def add_new_profile(self):
        dialog = ctk.CTkInputDialog(text="กรอกชื่อเซ็ทการตั้งค่าใหม่:", title="เพิ่มเซ็ทใหม่")
        new_name = dialog.get_input()
        if new_name and new_name.strip():
            new_name = new_name.strip()
            self.profile_data['profiles'][new_name] = self.get_current_switches_dict()
            self.profile_data['active'] = new_name
            self.save_profiles_file()

            names = list(self.profile_data['profiles'].keys())
            self.profile_menu.configure(values=names)
            self.profile_menu.set(new_name)
            self.log_safe(f"➕ สร้างเซ็ทการตั้งค่าใหม่: '{new_name}' เรียบร้อยแล้ว")

    def delete_active_profile(self):
        active = self.profile_menu.get()
        names = list(self.profile_data['profiles'].keys())
        if len(names) <= 1:
            self.log_safe("⚠️ ไม่สามารถลบเซ็ทสุดท้ายได้")
            return

        del self.profile_data['profiles'][active]
        new_active = list(self.profile_data['profiles'].keys())[0]
        self.profile_data['active'] = new_active
        self.save_profiles_file()

        self.profile_menu.configure(values=list(self.profile_data['profiles'].keys()))
        self.profile_menu.set(new_active)
        self.apply_profile_to_switches(new_active)
        self.log_safe(f"🗑️ ลบเซ็ท '{active}' เรียบร้อยแล้ว")

    def get_current_switches_dict(self):
        try:
            sec = float(self.entry_timer_sec.get())
        except ValueError:
            sec = 19.0

        return {
            'images': self.current_profile_images.copy(),
            'auto_captcha': bool(self.switch_captcha.get()),
            'auto_popup': bool(self.switch_popup.get()),
            'use_fast_start': bool(self.switch_fast_start.get()),
            'use_relay': bool(self.switch_relay.get()),
            'buy_boost': bool(self.switch_boost.get()),
            'jump_at_start': bool(self.switch_jump.get()),
            'use_relay_quit': bool(self.switch_relay_quit.get()),
            'use_timer_quit': bool(self.switch_timer_quit.get()),
            'timer_sec': sec
        }

    def show_context_menu(self, event):
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()

    def copy_selection(self, event=None):
        try:
            _tb = getattr(self.log_box, '_textbox', self.log_box)
            if _tb.tag_ranges("sel"):
                selected_text = _tb.get("sel.first", "sel.last")
                if selected_text:
                    self.clipboard_clear()
                    self.clipboard_append(selected_text)
                    self.update()
        except Exception:
            pass
        return "break"

    def copy_all_logs(self, event=None):
        try:
            _tb = getattr(self.log_box, '_textbox', self.log_box)
            all_text = _tb.get("1.0", "end-1c")
            if all_text:
                self.clipboard_clear()
                self.clipboard_append(all_text)
                self.update()
        except Exception:
            pass
        return "break"

    def on_toggle_relay(self):
        if self.switch_relay.get() == 1:
            self.switch_relay_quit.deselect()
            self.switch_timer_quit.deselect()
        self.sync_config()

    def on_toggle_relay_quit(self):
        if self.switch_relay_quit.get() == 1:
            self.switch_relay.deselect()
            self.switch_timer_quit.deselect()
        self.sync_config()

    def on_toggle_timer_quit(self):
        if self.switch_timer_quit.get() == 1:
            self.switch_relay.deselect()
            self.switch_relay_quit.deselect()
        self.sync_config()

    def sync_config(self):
        config_data = self.get_current_switches_dict()
        try:
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=4)
        except Exception:
            pass

    def log_safe(self, message):
        t_str = time.strftime('%H:%M:%S')
        msg_line = f"[{t_str}] {message}\n"
        self.log_box.insert('end', msg_line)
        self.log_box.see('end')

    def start_bot(self):
        self.is_running = True
        self.btn_start.configure(state='disabled')
        self.btn_stop.configure(state='normal')
        self.status_label.configure(text='Status: RUNNING', text_color='#2FA572')
        self.log_safe('Started run.py subprocess...')
        self.sync_config()

        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"

        CREATE_NO_WINDOW = 0x08000000
        run_py_path = os.path.join(os.path.dirname(__file__), 'run.py')
        try:
            self.bot_process = subprocess.Popen(
                [sys.executable, '-u', run_py_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding='utf-8',
                errors='replace',
                creationflags=CREATE_NO_WINDOW,
                cwd=os.path.dirname(__file__),
                env=env
            )
            threading.Thread(target=self.read_bot_logs, daemon=True).start()
        except Exception as e:
            self.log_safe(f"Error starting run.py: {e}")

    def read_bot_logs(self):
        if self.bot_process and self.bot_process.stdout:
            for line in iter(self.bot_process.stdout.readline, ''):
                if line:
                    self.after(0, self.log_safe, line.strip())
            self.bot_process.stdout.close()

    def stop_bot(self):
        self.is_running = False
        if hasattr(self, 'bot_process') and self.bot_process:
            try:
                self.bot_process.terminate()
                self.bot_process.wait(timeout=1.0)
            except Exception:
                pass
            self.bot_process = None

        self.btn_start.configure(state='normal')
        self.btn_stop.configure(state='disabled')
        self.status_label.configure(text='Status: STOPPED', text_color='#FF5555')
        self.log_safe('Stopped run.py immediately.')

if __name__ == '__main__':
    app = CookieBotGUI()
    app.mainloop()
