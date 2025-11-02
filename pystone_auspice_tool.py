import datetime
from typing import Dict, List, Any, Union
import re
import os
import json

# สมมติว่า ALL_DATA และ Lookup Functions ถูกโหลด/กำหนดจาก pystone_data_tool.py แล้ว
# (ในแอปพลิเคชันจริง คุณต้องเรียก load_all_data() ก่อน)
# เพื่อให้โค้ดนี้ทำงานได้อิสระในการทดสอบ
# เราจะสร้าง Mock Data/Function Placeholder ไว้ชั่วคราว
# NOTE: ในการใช้งานจริง, คุณควรเรียกใช้ pystone_data_tool.load_all_data()
if __name__ == "__main__":
    print("--- Running Auspice Calculator (Requires pystone_data_tool.py setup) ---")
    # Placeholder: จำลองการโหลดข้อมูล Lookup จากไฟล์
    DATA_FOLDER = 'data'
    ALL_DATA = {}
    try:
        with open(os.path.join(DATA_FOLDER, 'lookup_days.json'), 'r', encoding='utf-8') as f:
            ALL_DATA['days'] = json.load(f)
        with open(os.path.join(DATA_FOLDER, 'lookup_zodiacs.json'), 'r', encoding='utf-8') as f:
            zodiac_data = json.load(f)
            ALL_DATA['signs'] = zodiac_data['signs']
            ALL_DATA['animals'] = zodiac_data['animals']
        with open(os.path.join(DATA_FOLDER, 'lookup_colors.json'), 'r', encoding='utf-8') as f:
            ALL_DATA['colors'] = json.load(f)
    except FileNotFoundError:
        print("Error: ต้องแน่ใจว่าไฟล์ JSON อยู่ในโฟลเดอร์ 'data/'")


# --- Helper Function: Date Conversion ---

def convert_date_th_to_en(date_th: str) -> Union[datetime.date, None]:
    """
    แปลงวันที่ไทย (DD/MM/YYYY พ.ศ.) เป็นวัตถุ datetime.date (ค.ศ.)
    ตัวอย่าง: '25/08/2530' -> date(1987, 8, 25)
    """
    if not re.match(r'^\d{1,2}/\d{1,2}/\d{4}$', date_th):
        return None
    try:
        day, month, year_th = map(int, date_th.split('/'))
        year_en = year_th - 543  # แปลง พ.ศ. เป็น ค.ศ.
        return datetime.date(year_en, month, day)
    except ValueError:
        return None

# --- Core Calculation Functions ---

def get_day_id_from_date(date_en: datetime.date) -> int:
    """
    คำนวณ ID วันของสัปดาห์ (1=อาทิตย์, 2=จันทร์... 8=เสาร์)
    รวมถึงกรณีพิเศษ พุธกลางวัน (4) และ พุธกลางคืน (5)
    """
    # 0=จันทร์, 1=อังคาร, ..., 6=อาทิตย์ (Python weekday())
    python_day_of_week = date_en.weekday() 
    
    # Map Python weekday() (0=Mon to 6=Sun) to Thai Day ID (1=Sun to 8=Sat)
    # [Mon: 0, Tue: 1, Wed: 2, Thu: 3, Fri: 4, Sat: 5, Sun: 6]
    # [2, 3, 4/5, 6, 7, 8, 1]
    
    day_map = { 
        0: 2,  # จันทร์
        1: 3,  # อังคาร
        3: 6,  # พฤหัสบดี
        4: 7,  # ศุกร์
        5: 8,  # เสาร์
        6: 1,  # อาทิตย์
    }
    
    day_id = day_map.get(python_day_of_week)

    if python_day_of_week == 2: # วันพุธ
        # หากไม่สามารถระบุเวลาได้ จะถือเป็นกลางวันเพื่อความปลอดภัย
        # ใน API เดิม โค้ด PHP ใช้เวลา 06:00 - 17:59 เป็นกลางวัน
        # ในบริบทนี้ เราไม่มีเวลา, แต่ถ้าจำเป็นต้องเลือก:
        # การค้นหาตาม วดป. ควรใช้ day_id 4 และ 5 (พุธกลางวัน, กลางคืน) พร้อมกัน
        # แต่เพื่อการคำนวณวันเกิดที่แม่นยำที่สุดตามวันที่ ให้คืนค่า day_id 4
        # NOTE: การค้นหาจะใช้ ID 4 และ 5 ในขั้นตอน Filter
        return 4 
    
    return day_id if day_id else 0


def get_animal_id_from_date(date_en: datetime.date) -> int:
    """
    คำนวณ ID ปีนักษัตรตามปีเกิด (โดยมีเกณฑ์เปลี่ยนปีนักษัตรคือวันสงกรานต์ 13 เมษายน)
    """
    year = date_en.year
    month = date_en.month
    day = date_en.day
    
    # วันเปลี่ยนปีนักษัตรคือ 13 เมษายน
    is_before_songkran = (month < 4) or (month == 4 and day < 13)
    
    if is_before_songkran:
        year -= 1
        
    # สูตรคำนวณ ปีนักษัตร ID (ชวด=1, กุน=12)
    animal_id = ((year + 8) % 12) + 1
    
    return animal_id


def get_sign_id_from_date(date_en: datetime.date) -> int:
    """
    คำนวณ ID ราศี (1=เมษ ถึง 12=มีน)
    """
    month = date_en.month
    day = date_en.day
    
    zodiac_signs = ALL_DATA.get('signs', [])
    
    for sign in zodiac_signs:
        start_m = sign['start_month']
        start_d = sign['start_day']
        end_m = sign['end_month']
        end_d = sign['end_day']
        sign_id = sign['id']
        
        if start_m > end_m:  # กรณีข้ามปี (ธนู/มังกร/กุมภ์/มีน)
            # เช่น ธนู: Dec 16 - Jan 14
            if (month == start_m and day >= start_d) or (month == end_m and day <= end_d):
                return sign_id
        elif (month == start_m and day >= start_d) and (month == end_m and day <= end_d):
            return sign_id
            
    return 0


def calculate_auspice_ids(date_th: str) -> Dict[str, Union[int, str]]:
    """
    ฟังก์ชันหลักในการแปลงวันเกิดเป็น ID โหราศาสตร์ทั้งหมด
    """
    date_en = convert_date_th_to_en(date_th)
    
    if not date_en:
        return {'error': "รูปแบบวันที่ไม่ถูกต้อง (คาดหวัง DD/MM/YYYY พ.ศ.)"}
        
    day_id = get_day_id_from_date(date_en)
    month_id = date_en.month # ID เดือนตรงกับเลขเดือน 1-12
    animal_id = get_animal_id_from_date(date_en)
    sign_id = get_sign_id_from_date(date_en)
    
    return {
        'date_en': date_en.strftime('%Y-%m-%d'),
        'day_id': day_id,
        'month_id': month_id,
        'animal_id': animal_id,
        'sign_id': sign_id
    }
    
# --- Unlucky Color Checker Function ---

def check_unlucky_color(stone_color_ids: str, day_id: int) -> Dict[str, Union[bool, str]]:
    """
    ตรวจสอบว่าหินมีสีอัปมงคลจากวันเกิด/วันเงื่อนไขหรือไม่
    
    :param stone_color_ids: ID สีของหิน (str, space separated)
    :param day_id: ID ของวันเกิด/วันค้นหา (1-8)
    :return: Dict {'is_unlucky': bool, 'unlucky_colors_found': str}
    """
    if day_id == 0:
        return {'is_unlucky': False, 'unlucky_colors_found': ''}

    # 1. ดึงข้อมูลสีอัปมงคลตาม day_id
    day_data = next((d for d in ALL_DATA.get('days', []) if d['id'] == day_id), None)
    if not day_data or not day_data.get('unlucky_color'):
        return {'is_unlucky': False, 'unlucky_colors_found': ''}
        
    unlucky_color_names_str = day_data['unlucky_color']
    unlucky_color_names = [name.strip() for name in unlucky_color_names_str.split(',') if name.strip()]
    
    # 2. แปลงชื่อสีอัปมงคลเป็น ID
    unlucky_color_ids = set()
    for name in unlucky_color_names:
        color_item = next((c for c in ALL_DATA.get('colors', []) if c['name'] == name), None)
        if color_item:
            unlucky_color_ids.add(color_item['id'])
            
    if not unlucky_color_ids:
        return {'is_unlucky': False, 'unlucky_colors_found': ''}

    # 3. ตรวจสอบหิน
    stone_ids_list = [str(id) for id in split_ids(stone_color_ids)]

    unlucky_colors_found = []
    
    for stone_id in stone_ids_list:
        if int(stone_id) in unlucky_color_ids:
            # ใช้ Lookup Name เพื่อให้ได้ชื่อที่ชัดเจนในการรายงาน
            unlucky_colors_found.append(next((c['name'] for c in ALL_DATA['colors'] if c['id'] == int(stone_id)), f"ID:{stone_id}"))

    return {
        'is_unlucky': len(unlucky_colors_found) > 0,
        'unlucky_colors_found': ', '.join(unlucky_colors_found)
    }

# --- Example of How to Use the Functions ---
if __name__ == "__main__":
    
    print("\n--- TEST: Auspice ID Calculation (วันอังคาร 25/08/2530) ---")
    birth_date = '25/08/2530' # วันที่ 25 ส.ค. 1987 (อังคาร)
    auspice_result = calculate_auspice_ids(birth_date)
    print(f"ผลลัพธ์: {auspice_result}")
    
    if 'day_id' in auspice_result:
        # ทดสอบ Lookup Name เพื่อยืนยัน
        mock_day_id = auspice_result['day_id']
        mock_day_name = next((d['name'] for d in ALL_DATA['days'] if d['id'] == mock_day_id), 'N/A')
        print(f"ยืนยัน Day ID: {mock_day_id} ({mock_day_name})")
    
    print("\n--- TEST: Unlucky Color Check (วันอังคาร: สีอัปมงคลคือ ขาว/เหลืองนวล) ---")
    
    # Stone ID 1 (Agate) colors: 1, 2, 3, 6, 7, 9, 10, 11, 12 (มี 9 = ขาว)
    agate_colors = "1 2 3 6 7 9 10 11 12" 
    
    # Day ID 3 (อังคาร) อัปมงคล: ขาว, เหลืองนวล (ID 9, 5)
    unlucky_check = check_unlucky_color(agate_colors, 3) 
    print(f"Agate (มีสีขาว) vs วันอังคาร: {unlucky_check}")
    
    # Day ID 6 (พฤหัสบดี) อัปมงคล: ดำ, ม่วง (ID 10, 8)
    unlucky_check_safe = check_unlucky_color(agate_colors, 6) 
    print(f"Agate (มีสีดำ) vs วันพฤหัส: {unlucky_check_safe}")