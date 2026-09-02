import os
import time
import cv2
import numpy as np
from tap import tap

def check_captcha(screen=None):
    """
    1. สแกนหา Captcha (บอทเช็ค) บนจอ
    คืนค่า (True, พิกัด) หากเจอ และจะทำการแก้ Captcha อัตโนมัติทันที
    """
    from scan import get_screen, find_button

    if screen is None:
        screen = get_screen()

    if screen is None:
        return False, None

    # สแกนหาภาพสัญลักษณ์ Captcha
    cap_pos, cap_score = find_button(screen, "templates/captcha.png", threshold=0.60)

    if cap_pos:
        print(f"🚨 🎯 เตือนภัย! เจอ Captcha (บอทเช็ค) ที่พิกัด {cap_pos} (conf: {cap_score:.2f}) -> เริ่มระบบแก้ Captcha อัตโนมัติ!")
        solve_captcha()
        return True, cap_pos

    return False, None

def solve_captcha():
    """
    2. ฟังก์ชันแก้ Captcha อัตโนมัติ (Original Silhouette Card Solver):
    สกัดเงาตัวละคร ตัดสีพื้นหลังไดนามิก และคัดเลือกกดการ์ดที่สไลด์/กระโดด 2 ใบแรกที่มีคะแนนสูงสุด!
    """
    from scan import get_screen, find_button

    print("🛡️ [CAPTCHA] เริ่มต้นกระบวนการวิเคราะห์เงาการ์ด 6 ใบ (Silhouette Contour Matcher)...")

    max_rounds = 10
    for round_num in range(1, max_rounds + 1):
        screen = get_screen()
        if screen is None:
            time.sleep(0.5)
            continue

        # เช็คว่า Captcha หายไปจากจอแล้วหรือยัง
        cap_pos, cap_score = find_button(screen, "templates/captcha.png", threshold=0.60)
        if not cap_pos:
            print("✅ [CAPTCHA] แก้ Captcha เรียบร้อยแล้ว! กลับเข้าสู่การทำงานปกติ")
            time.sleep(1.0)
            return True

        print(f"🔍 [CAPTCHA] รอบที่ {round_num}: กำลังวิเคราะห์เงาลักษณะตัวละครของการ์ด 6 ใบ...")

        # วิเคราะห์การ์ดทั้ง 6 ใบ
        card_results = _analyze_cards(screen)
        card_results.sort(key=lambda x: x["score"], reverse=True)

        # เลือกกดการ์ดที่มีคะแนนสูงสุด 2 ใบแรก
        targets = [c for c in card_results if c["score"] >= 2.0]
        if len(targets) == 0:
            targets = card_results[:2]
        elif len(targets) > 2:
            targets = targets[:2]

        for card in targets:
            cx, cy = card["pos"]
            print(f"   👉 [CAPTCHA] กดเลือกการ์ดใบที่ #{card['idx']+1} ที่พิกัด ({cx}, {cy}) [Silhouette Score: {card['score']:.2f}, W/H Ratio: {card['ratio']:.2f}]")
            tap(cx, cy)
            time.sleep(0.4)

        time.sleep(1.2)

    print("⚠️ [CAPTCHA] สิ้นสุดลูปแก้ Captcha")
    return False

def _analyze_cards(frame):
    """สกัดกรอบพิกัดกึ่งกลางการ์ด 6 ใบ บนหน้าจอมาตรฐาน 1600x900"""
    h, w = frame.shape[:2]

    # พิกัดกึ่งกลางการ์ด 6 ใบตรงตามระบบต้นฉบับ
    # Row 1: y=372 (0.4133), Row 2: y=692 (0.7689)
    # Col 1: x=543 (0.3394), Col 2: x=787 (0.4919), Col 3: x=1031 (0.6444)
    col_pcts = [0.3394, 0.4919, 0.6444]
    row_pcts = [0.4133, 0.7689]

    half_w = int(w * (90.0 / 1600.0))    # ~90px inner crop
    half_h = int(h * (125.0 / 900.0))   # ~125px inner crop

    results = []
    for r_idx, r_pct in enumerate(row_pcts):
        for c_idx, c_pct in enumerate(col_pcts):
            idx = r_idx * 3 + c_idx
            cx = int(w * c_pct)
            cy = int(h * r_pct)

            y1 = max(0, cy - half_h)
            y2 = min(h, cy + half_h)
            x1 = max(0, cx - half_w)
            x2 = min(w, cx + half_w)
            crop = frame[y1:y2, x1:x2]

            ratio, bh, score = _get_silhouette_score(crop)
            results.append({
                "idx": idx,
                "pos": (cx, cy),
                "ratio": ratio,
                "height": bh,
                "score": score
            })

    return results

def _get_silhouette_score(crop):
    """ดึงสีพื้นหลังจากมุมทั้ง 4 ด้าน ตัดพื้นหลังออกเพื่อให้ได้เงาตัวละครสีดำล้วน (Silhouette Mask)"""
    if crop is None or crop.size == 0:
        return 0.0, 0, 0.0

    ch, cw = crop.shape[:2]
    corner_sz = min(10, ch // 4, cw // 4)
    corners = np.concatenate([
        crop[:corner_sz, :corner_sz],
        crop[:corner_sz, -corner_sz:],
        crop[-corner_sz:, :corner_sz],
        crop[-corner_sz:, -corner_sz:]
    ], axis=0)
    
    # คำนวณหาค่าเฉลี่ยสีพื้นหลังจากมุมทั้ง 4
    bg_color = np.median(corners.reshape(-1, 3), axis=0)

    # คำนวณระยะห่างความต่างสี เพื่อแยกตัวละครออกจากพื้นหลัง
    diff = np.linalg.norm(crop.astype(np.float32) - bg_color, axis=2)
    char_mask = (diff > 20).astype(np.uint8) * 255

    # หาขอบเขตภาพเงาตัวละคร
    cnts, _ = cv2.findContours(char_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if cnts:
        valid_cnts = [c for c in cnts if cv2.contourArea(c) > 100]
        if valid_cnts:
            all_pts = np.concatenate(valid_cnts)
            bx, by, bw, bh = cv2.boundingRect(all_pts)
            if bh > 0:
                ratio = float(bw) / float(bh)
                # สูตรคะแนนสไลด์/กระโดดต้นฉบับ: สัดส่วนความกว้างต่อความสูง * ความเตี้ย
                score = ratio * (100.0 / bh)
                return ratio, bh, score

    return 0.0, 0, 0.0


