import json
import os
from typing import List, Dict, Union, Any

# =======================================================
# CONFIGURATION
# =======================================================
# กำหนดพาธไปยังโฟลเดอร์ที่เก็บไฟล์ JSON
DATA_FOLDER = 'data' 

# =======================================================
# HELPER FUNCTIONS
# =======================================================

def split_ids(id_string: str) -> List[int]:
    """
    แปลง string ของ IDs ที่คั่นด้วยช่องว่าง (space) เป็น List ของจำนวนเต็ม (integers)
    เช่น: "1 3 5" -> [1, 3, 5]
    """
    if not id_string:
        return []
    try:
        # ใช้ split() เพื่อแยกด้วยช่องว่าง และ list comprehension เพื่อแปลงเป็น int
        return [int(s.strip()) for s in id_string.split() if s.strip().isdigit()]
    except ValueError:
        print(f"Warning: Failed to convert one or more IDs to integer from string: '{id_string}'")
        return []

def lookup_name(lookup_array: List[Dict[str, Any]], id_val: Union[int, str], display_key: str, default: str = '-') -> str:
    """
    ค้นหาชื่อหรือค่าที่ต้องการจาก ID ในตาราง Lookup
    """
    if not lookup_array or (not id_val and id_val != 0):
        return default
    
    # ตรวจสอบว่า ID ที่ส่งเข้ามาเป็น str หรือ int
    target_id = int(id_val) if isinstance(id_val, str) and id_val.isdigit() else id_val
    
    # วนหา ID ที่ตรงกัน
    for item in lookup_array:
        if item.get('id') == target_id:
            return str(item.get(display_key, default))
            
    return default

# =======================================================
# CORE DATA HANDLER FUNCTION
# =======================================================

def load_all_data(base_path: str = DATA_FOLDER) -> Dict[str, Any]:
    """
    โหลดไฟล์ JSON ทั้งหมดเข้าสู่หน่วยความจำ
    
    :param base_path: พาธของโฟลเดอร์ข้อมูล (e.g., 'data')
    :return: Dictionary ที่มีข้อมูลทั้งหมด (stones, groups, days, ...)
    """
    loaded_data = {
        'stones': [],
        'groups': [],
        'days': [],
        'months': [],
        'colors': [],
        'animals': [],
        'signs': [],
        'chakra': [],       
        'elements': [],    
        'numerology': []         
    }
    
    # Map ชื่อไฟล์กับ key ใน Dictionary
    file_map = {
        'stones_main_data.json': 'stones',
        'lookup_groups.json': 'groups',
        'lookup_days.json': 'days',
        'lookup_months.json': 'months',
        'lookup_colors.json': 'colors',
        'lookup_chakra.json': 'chakra',
        'lookup_elements.json': 'elements',
        'lookup_numerology.json': 'numerology',    
    }
    
    print(f"--- กำลังโหลดข้อมูลจาก '{base_path}' ---")

    # 1. โหลดไฟล์ JSON ที่เป็น Array ทั่วไป
    for filename, key in file_map.items():
        file_path = os.path.join(base_path, filename)
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        loaded_data[key] = data
                        print(f"✅ โหลด {filename} ({len(data)} รายการ)")
                    else:
                        print(f"❌ Error: {filename} ไม่ได้เป็น List")
            except json.JSONDecodeError:
                print(f"❌ Error: {filename} รูปแบบ JSON ไม่ถูกต้อง")
            except Exception as e:
                print(f"❌ Error ในการเปิด/อ่าน {filename}: {e}")
        else:
            print(f"⚠️ คำเตือน: ไม่พบไฟล์ {filename} ที่ {file_path}")
            
    # 2. โหลดไฟล์ zodiacs พิเศษ (มี 2 Keys: animals และ signs)
    zodiac_path = os.path.join(base_path, 'lookup_zodiacs.json')
    if os.path.exists(zodiac_path):
        try:
            with open(zodiac_path, 'r', encoding='utf-8') as f:
                zodiac_data = json.load(f)
                loaded_data['animals'] = zodiac_data.get('animals', [])
                loaded_data['signs'] = zodiac_data.get('signs', [])
                print(f"✅ โหลด lookup_zodiacs.json (Animals: {len(loaded_data['animals'])}, Signs: {len(loaded_data['signs'])} รายการ)")
        except Exception as e:
             print(f"❌ Error ในการโหลด/อ่าน lookup_zodiacs.json: {e}")
    else:
        print(f"⚠️ คำเตือน: ไม่พบไฟล์ lookup_zodiacs.json")

    print("--------------------------------------")
    return loaded_data

# =======================================================
# EXAMPLE USAGE (โค้ดสำหรับทดสอบการทำงาน)
# =======================================================

if __name__ == "__main__":
    # 1. โหลดข้อมูลทั้งหมด
    ALL_DATA = load_all_data()

    # 2. ดึงข้อมูลหินตัวอย่าง (เช่น Agate ID: 1)
    agate_stone = ALL_DATA['stones'][0] if ALL_DATA['stones'] else None
    
    if agate_stone:
        print("\n--- ตัวอย่างข้อมูลหิน (ID: 1 - อาเกต) ---")
        print(f"ชื่อ: {agate_stone['thai_name']} ({agate_stone['english_name']})")

        # 3. ทดสอบการแปลง ID และ Lookup
        
        # 3.1 แปลง Group IDs
        group_ids = split_ids(agate_stone['group_ids'])
        group_names = [lookup_name(ALL_DATA['groups'], id, 'name') for id in group_ids]
        print(f"กลุ่มมงคล IDs: {group_ids} -> ชื่อ: {', '.join(group_names)}")
        
        # 3.2 แปลง Color IDs
        color_ids = split_ids(agate_stone['color_ids'])
        color_names = [lookup_name(ALL_DATA['colors'], id, 'name') for id in color_ids]
        print(f"สีมงคล IDs: {color_ids} -> ชื่อ: {', '.join(color_names)}")
        
        # 3.3 แปลง Day ID
        day_ids = split_ids(agate_stone['good_days'])
        day_names = [lookup_name(ALL_DATA['days'], id, 'name') for id in day_ids]
        print(f"วันมงคล IDs: {day_ids} -> ชื่อ: {', '.join(day_names)}")
        
        # 3.4 แปลง Zodiac Animal ID
        animal_ids = split_ids(agate_stone['good_zodiac_animals'])
        animal_names = [lookup_name(ALL_DATA['animals'], id, 'thai_name') for id in animal_ids]
        print(f"ปีนักษัตร IDs: {animal_ids} -> ชื่อ: {', '.join(animal_names)}")
        
        # 3.5 ทดสอบ lookup name ที่ไม่มีอยู่
        missing_name = lookup_name(ALL_DATA['colors'], 999, 'name')
        print(f"\nทดสอบ Lookup ID 999: {missing_name}")
    else:
        print("ไม่พบข้อมูลหินในไฟล์stones_main_data.json, โปรดตรวจสอบไฟล์")