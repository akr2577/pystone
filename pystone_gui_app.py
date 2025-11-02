import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import webbrowser
import os
import math
from typing import Dict, List, Any, Union
import json
import re 
import datetime 

# ----------------------------------------------------------------------
# 1. UTILITY FUNCTIONS (Defined FIRST for correct scope)
# ----------------------------------------------------------------------
DATA_FOLDER = 'data'
if not os.path.isdir(DATA_FOLDER): os.makedirs(DATA_FOLDER) # FIX: แก้ไข osmakedirs เป็น os.makedirs

# --- Data Loading (ROBUSTLY CHECKING JSON ERRORS) ---
def load_all_data():
    """โหลดไฟล์ JSON ทั้งหมดเข้าสู่หน่วยความจำ พร้อมตรวจสอบ JSON Error อย่างละเอียด"""
    data = {}
    files = ['stones_main_data.json', 'lookup_groups.json', 'lookup_days.json', 
             'lookup_months.json', 'lookup_colors.json', 'lookup_zodiacs.json',
             'lookup_element.json', 'lookup_chakra.json', 'lookup_numerology.json']
    
    for f in files:
        # Determine the dictionary key
        if f == 'lookup_element.json':
            key = 'element' # FIX: ใช้คีย์ 'element' (ไม่มี s)
        elif 'lookup' in f:
            key = f.split('_')[1].split('.')[0]
        else:
            key = 'stones'
            
        path = os.path.join(DATA_FOLDER, f)
        
        if 'zodiacs' in f:
            if os.path.exists(path):
                try:
                    with open(path, 'r', encoding='utf-8') as file:
                        zdata = json.load(file)
                        data['animals'] = zdata.get('animals', [])
                        data['signs'] = zdata.get('signs', [])
                except json.JSONDecodeError as e:
                    messagebox.showerror("JSON Error", f"❌ ไฟล์ {f} (Zodiacs) มีรูปแบบ JSON ไม่ถูกต้อง: {e}")
                    return None
                except Exception as e:
                    messagebox.showerror("Load Error", f"❌ เกิดข้อผิดพลาดในการโหลดไฟล์ {f}: {e}")
                    return None
        
        elif os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as file:
                    data[key] = json.load(file)
            except json.JSONDecodeError as e:
                messagebox.showerror("JSON Error", f"❌ ไฟล์ {f} มีรูปแบบ JSON ไม่ถูกต้อง: {e}")
                return None
            except Exception as e:
                messagebox.showerror("Load Error", f"❌ เกิดข้อผิดพลาดในการโหลดไฟล์ {f}: {e}")
                return None
        
        elif f == 'stones_main_data.json':
            messagebox.showinfo("Data Load", "⚠️ ไม่พบไฟล์ stones_main_data.json")

    # ตรวจสอบว่าหินหลักโหลดหรือไม่
    if not data.get('stones'):
        messagebox.showinfo("Data Load", "Cannot run without stones_main_data.json.")
        return None
    return data

# --- JSON File Handler ---
def save_stones_to_json(stones_data: List[Dict[str, Any]]):
    """บันทึกข้อมูลหินทั้งหมดกลับไปยังไฟล์ JSON หลัก"""
    file_path = os.path.join(DATA_FOLDER, 'stones_main_data.json')
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(stones_data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        messagebox.showerror("Save Error", f"ไม่สามารถบันทึกไฟล์ {file_path} ได้: {e}")
        return False

def generate_new_id(stones: List[Dict[str, Any]]) -> int:
    """สร้าง ID ใหม่โดยการหา ID ที่มีค่าสูงสุดแล้วบวก 1"""
    if not stones:
        return 1
    max_id = max(stone.get('id', 0) for stone in stones)
    return max_id + 1

# --- Helper Functions ---
def split_ids(id_string: str) -> List[int]:
    if not id_string: return []
    try: return [int(s.strip()) for s in id_string.split() if s.strip().isdigit()]
    except: return []
    
def lookup_name(lookup_array: List[Dict[str, Any]], id_val: Union[int, str], display_key: str, default: str = '-') -> str:
    if not lookup_array or (not id_val and id_val != 0): return default
    
    target_id = None
    if isinstance(id_val, str) and id_val.isdigit():
        target_id = int(id_val)
    elif isinstance(id_val, int):
         target_id = id_val
    
    if target_id is None:
        return default

    for item in lookup_array:
        if item.get('id') == target_id:
            if display_key == 'number_value':
                 return str(item.get('number_value', default))
            return str(item.get(display_key, default))
    return default

def format_lookup_list(ids_str, lookup_data, display_key):
    ids = split_ids(ids_str)
    names = [lookup_name(lookup_data, id, display_key) for id in ids]
    return ', '.join(names) if names else '-'


# --- Auspice Calculation Functions ---
def convert_date_th_to_en(date_th: str) -> Union[datetime.date, None]:
    if not re.match(r'^\d{1,2}/\d{1,2}/\d{4}$', date_th): return None
    try:
        day, month, year_th = map(int, date_th.split('/'))
        year_en = year_th - 543
        return datetime.date(year_en, month, day)
    except ValueError:
        return None

def get_day_id_from_date(date_en: datetime.date) -> int:
    python_day_of_week = date_en.weekday() 
    
    day_map = { 0: 2, 1: 3, 3: 6, 4: 7, 5: 8, 6: 1 }

    if python_day_of_week == 2: return 4 
    
    return day_map.get(python_day_of_week, 0)

def get_animal_id_from_date(date_en: datetime.date, all_data: Dict[str, Any]) -> int:
    year = date_en.year
    month = date_en.month
    day = date_en.day
    
    is_before_songkran = (month < 4) or (month == 4 and day < 13)
    if is_before_songkran: year -= 1
        
    animal_id = ((year + 8) % 12) + 1
    return animal_id

def get_sign_id_from_date(date_en: datetime.date, all_data: Dict[str, Any]) -> int:
    month = date_en.month
    day = date_en.day
    zodiac_signs = all_data.get('signs', [])
    
    for sign in zodiac_signs:
        start_m, start_d = sign['start_month'], sign['start_day']
        end_m, end_d = sign['end_month'], sign['end_day']
        sign_id = sign['id']
        
        if start_m > end_m: 
            is_start_month = (month == start_m and day >= start_d)
            is_end_month = (month == end_m and day <= end_d)
            if is_start_month or is_end_month:
                return sign_id
        else:
            is_start_month = (month == start_m and day >= start_d)
            is_end_month = (month == end_m and day <= end_d)
            is_mid_month = (month > start_m and month < end_m)
            
            if is_start_month or is_end_month or is_mid_month:
                 return sign_id
            
    return 0

def calculate_auspice_ids(date_th: str, all_data: Dict[str, Any]) -> Dict[str, Union[int, str]]:
    date_en = convert_date_th_to_en(date_th)
    if not date_en: return {'error': "รูปแบบวันที่ไม่ถูกต้อง (DD/MM/YYYY พ.ศ.)"}
        
    day_id = get_day_id_from_date(date_en)
    month_id = date_en.month
    animal_id = get_animal_id_from_date(date_en, all_data)
    sign_id = get_sign_id_from_date(date_en, all_data)
    
    return {
        'date_en': date_en.strftime('%Y-%m-%d'),
        'day_id': day_id,
        'month_id': month_id,
        'animal_id': animal_id,
        'sign_id': sign_id
    }

def get_lucky_color_ids(day_id: int, all_data: Dict[str, Any]) -> List[str]:
    """
    ดึง ID สีมงคลของวันนั้นๆ
    """
    if day_id == 0: return []

    day_data = next((d for d in all_data.get('days', []) if d['id'] == day_id), None)
    if not day_data or not day_data.get('lucky_color'): return []
        
    lucky_color_names_str = day_data['lucky_color']
    lucky_color_names = [name.strip() for name in lucky_color_names_str.split(',') if name.strip()]
    
    lucky_color_ids = set()
    for name in lucky_color_names:
        color_item = next((c for c in all_data.get('colors', []) if c['name'] == name), None)
        if color_item:
            # เก็บเป็น str ID เพื่อให้เข้ากันกับ stone_ids ใน apply_auspice_filter
            lucky_color_ids.add(str(color_item['id'])) 
            
    return list(lucky_color_ids)

def check_unlucky_color(stone_color_ids: str, day_id: int, all_data: Dict[str, Any]) -> Dict[str, Union[bool, str]]:
    if day_id == 0: return {'is_unlucky': False, 'unlucky_colors_found': ''}

    day_data = next((d for d in all_data.get('days', []) if d['id'] == day_id), None)
    if not day_data or not day_data.get('unlucky_color'): return {'is_unlucky': False, 'unlucky_colors_found': ''}
        
    unlucky_color_names_str = day_data['unlucky_color']
    unlucky_color_names = [name.strip() for name in unlucky_color_names_str.split(',') if name.strip()]
    
    unlucky_color_ids = set()
    for name in unlucky_color_names:
        color_item = next((c for c in all_data.get('colors', []) if c['name'] == name), None)
        if color_item:
            unlucky_color_ids.add(color_item['id'])
            
    if not unlucky_color_ids: return {'is_unlucky': False, 'unlucky_colors_found': ''}

    stone_ids_list = [str(id) for id in split_ids(stone_color_ids)]

    unlucky_colors_found = []
    
    for stone_id in stone_ids_list:
        if int(stone_id) in unlucky_color_ids:
            unlucky_colors_found.append(next((c['name'] for c in all_data['colors'] if c['id'] == int(stone_id)), f"ID:{stone_id}"))

    return {
        'is_unlucky': len(unlucky_colors_found) > 0,
        'unlucky_colors_found': ', '.join(unlucky_colors_found)
    }

# --- New Helper Function for Export ---

def export_to_file(content: str, filename_base: str, file_type: str):
    """
    Export content to a Text (.txt) or PDF (.pdf) file.
    Note: For PDF, it uses a very basic text-to-PDF conversion method
    that doesn't require external libraries (just simple placeholder).
    """
    if file_type == 'text':
        file_extension = '.txt'
        filetypes = [("Text files", "*.txt")]
    elif file_type == 'pdf':
        file_extension = '.pdf'
        filetypes = [("PDF files", "*.pdf")]
    else:
        messagebox.showerror("Export Error", "File type not supported.")
        return

    # Open save dialog
    file_path = filedialog.asksaveasfilename(
        defaultextension=file_extension,
        initialfile=f"{filename_base}{file_extension}",
        filetypes=filetypes
    )

    if file_path:
        try:
            if file_type == 'text':
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
            elif file_type == 'pdf':
                # Simple PDF Placeholder: Create a dummy PDF file path and save content as text
                # NOTE: For real PDF generation, you need libraries like reportlab or fpdf.
                # Here, we save as a text file and name it .pdf for simplicity.
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(f"--- PDF Simulation (Content Saved as Text) ---\n\n")
                    f.write(content)

            messagebox.showinfo("Export Success", f"บันทึกไฟล์ {os.path.basename(file_path)} เรียบร้อยแล้ว")
        except Exception as e:
            messagebox.showerror("Export Error", f"ไม่สามารถบันทึกไฟล์ได้: {e}")


# ----------------------------------------------------------------------
# 2. CRUD MODAL CLASSES
# ----------------------------------------------------------------------

class MultiSelectModal(tk.Toplevel):
    """
    Modal สำหรับเลือก ID หลายรายการจาก Listbox (สำหรับความสัมพันธ์ Many-to-Many)
    """
    def __init__(self, parent, title, data_list, display_key, initial_ids: str):
        super().__init__(parent)
        self.title(title)
        self.data_list = data_list
        self.display_key = display_key
        self.selected_ids = set(split_ids(initial_ids))
        self.result_ids = None # Output
        
        self.geometry("400x400")
        self.transient(parent)
        self.grab_set()

        self.listbox_frame = ttk.Frame(self)
        self.listbox_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.listbox = tk.Listbox(self.listbox_frame, selectmode=tk.MULTIPLE, height=15)
        self.listbox.pack(side="left", fill="both", expand=True)

        for item in self.data_list:
            display_name = str(item.get(self.display_key, '-'))
            self.listbox.insert(tk.END, f"ID {item['id']}: {display_name}")
            
            # Pre-select items
            if item['id'] in self.selected_ids:
                idx = self.data_list.index(item)
                self.listbox.selection_set(idx)

        # Buttons
        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="ตกลง", command=self.on_ok).pack(side='left', padx=10)
        ttk.Button(btn_frame, text="ยกเลิก", command=self.destroy).pack(side='left', padx=10)
        
        self.wait_window(self)

    def on_ok(self):
        selected_indices = self.listbox.curselection()
        new_ids = []
        for index in selected_indices:
            item = self.data_list[index]
            new_ids.append(str(item['id']))
        
        self.result_ids = ' '.join(new_ids)
        self.destroy()

class AddColorModal(tk.Toplevel):
    """
    Modal สำหรับเพิ่มสีใหม่ลงใน Lookup Colors และบันทึกไฟล์
    """
    def __init__(self, parent):
        super().__init__(parent)
        self.title("เพิ่มสีใหม่")
        self.parent_app = parent.parent
        self.new_color_id = 0
        self.geometry("300x200")
        self.transient(parent)
        self.grab_set()
        
        frame = ttk.Frame(self, padding=10)
        frame.pack(fill='both', expand=True)
        
        # Name
        ttk.Label(frame, text="ชื่อสี (ไทย)*:").grid(row=0, column=0, sticky='w')
        self.name_th_entry = ttk.Entry(frame, width=20)
        self.name_th_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # Hex Code
        ttk.Label(frame, text="โค้ด Hex (เช่น #FF0000)*:").grid(row=1, column=0, sticky='w')
        self.hex_entry = ttk.Entry(frame, width=20)
        self.hex_entry.grid(row=1, column=1, padx=5, pady=5)
        
        # FIX: ใช้ Style ปุ่มค้นหาใหม่
        ttk.Button(frame, text="บันทึกสี", command=self.save_new_color, style='SearchButton.TButton').grid(row=2, column=0, columnspan=2, pady=5)
        
        self.wait_window(self)

    def save_new_color(self):
        name_th = self.name_th_entry.get().strip()
        hex_code = self.hex_entry.get().strip().upper()
        
        if not name_th or not re.match(r'#([0-9A-F]{6})', hex_code):
            messagebox.showerror("Error", "กรุณาระบุชื่อสีและโค้ด Hex (เช่น #FF0000) ให้ถูกต้อง")
            return

        # Generate ID and save
        colors_data = self.parent_app.ALL_DATA['colors']
        new_id = generate_new_id(colors_data)
        
        new_color = {
            "id": new_id,
            "name": name_th,
            "english_name": "", 
            "hex_code": hex_code
        }
        
        colors_data.append(new_color)
        
        # Save color lookup file
        file_path = os.path.join(DATA_FOLDER, 'lookup_colors.json')
        try:
             with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(colors_data, f, ensure_ascii=False, indent=2)
             messagebox.showinfo("สำเร็จ", f"เพิ่มสี '{name_th}' (ID: {new_id}) แล้ว")
             
             # FIX: ต้องโหลดข้อมูลหลักใหม่เพื่อให้ lookup_colors ใน PyStoneApp อัปเดต
             self.parent_app.ALL_DATA = load_all_data() 
             
             self.new_color_id = new_id
             self.destroy()
        except Exception as e:
             messagebox.showerror("Save Error", f"ไม่สามารถบันทึกไฟล์ Lookup สีได้: {e}")


class StoneCrudModal(tk.Toplevel):
    """
    Modal Dialog สำหรับเพิ่ม แก้ไข ข้อมูลหินมงคล
    """
    def __init__(self, parent: 'PyStoneApp', mode: str, stone_data: Dict[str, Any]):
        super().__init__(parent)
        self.parent = parent
        self.mode = mode
        self.stone = stone_data
        self.title(f"{'แก้ไข' if mode == 'edit' else 'เพิ่ม'} ข้อมูลหินมงคล")
        self.geometry("900x500")
        self.resizable(False, False)
        self.grab_set()
        
        # FIX: กำหนด Style ปุ่มค้นหาใหม่
        self.style = ttk.Style(self)
        self.style.configure('SearchButton.TButton', 
                             font=('Tahoma', 12, 'bold'), 
                             background="#E0D4D4", 
                             foreground="#D10909", 
                             padding=[6, 3]) 
        self.style.map('SearchButton.TButton', 
                       background=[('active', "#C70B0B")], 
                       foreground=[('active', "#090909")]) # สีขณะคลิก/ชี้
        
        self.create_form()
        self.load_data()

    def create_form(self):
        main_frame = ttk.Frame(self, padding="12")
        main_frame.pack(fill='both', expand=True)

        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill='x', pady=10)
        
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_columnconfigure(1, weight=1, minsize=300)

        # --- LEFT SIDE: Main Info ---
        main_info_frame = ttk.LabelFrame(content_frame, text="ข้อมูลหลัก", padding="10")
        main_info_frame.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)
        
        ttk.Label(main_info_frame, text="ID:").grid(row=0, column=0, sticky='w')
        self.id_entry = ttk.Entry(main_info_frame, width=5)
        self.id_entry.grid(row=0, column=1, sticky='w', padx=5, pady=2)
        self.id_entry.config(state='readonly')

        ttk.Label(main_info_frame, text="ชื่อไทย*:", font=('Tahoma', 10, 'bold')).grid(row=1, column=0, sticky='w')
        self.thai_name_entry = ttk.Entry(main_info_frame, width=30)
        self.thai_name_entry.grid(row=1, column=1, sticky='we', padx=5, pady=2)
        
        ttk.Label(main_info_frame, text="ชื่ออังกฤษ*:", font=('Tahoma', 10, 'bold')).grid(row=2, column=0, sticky='w')
        self.english_name_entry = ttk.Entry(main_info_frame, width=30)
        self.english_name_entry.grid(row=2, column=1, sticky='we', padx=5, pady=2)
        
        ttk.Label(main_info_frame, text="ชื่ออื่น ๆ (คั่นด้วย ,):").grid(row=3, column=0, sticky='w')
        self.other_names_entry = ttk.Entry(main_info_frame, width=30)
        self.other_names_entry.grid(row=3, column=1, sticky='we', padx=5, pady=2)

        ttk.Label(main_info_frame, text="คำอธิบาย:").grid(row=4, column=0, sticky='nw')
        self.description_text = tk.Text(main_info_frame, wrap="word", height=8, width=30)
        self.description_text.grid(row=5, column=0, columnspan=2, sticky='nsew', padx=5, pady=5)


        # --- RIGHT SIDE: Relations (ใช้ Grid สำหรับความสัมพันธ์และปุ่ม) ---
        relations_frame = ttk.LabelFrame(content_frame, text="ความสัมพันธ์ (IDs คั่นด้วย Space/Comma)", padding="10")
        relations_frame.grid(row=0, column=1, sticky='nsew', padx=5, pady=5)
        
        self.relation_widgets = {}
        
        relations_list = [
            ('group_ids', 'กลุ่มมงคล', 'groups', 'name'), 
            ('color_ids', 'สี', 'colors', 'name'), 
            ('good_days', 'วันมงคล', 'days', 'name'), 
            ('good_months', 'เดือนมงคล', 'months', 'name'), 
            ('good_zodiac_animals', 'นักษัตร', 'animals', 'thai_name'), 
            ('good_zodiac_signs', 'ราศี', 'signs', 'name'),
            ('chakra_ids', 'จักระ', 'chakra', 'name_th'),
            ('element_ids', 'ธาตุ', 'element', 'name_th'),
            ('numerology_ids', 'เลขมงคล', 'numerology', 'number_value')
        ]
        
        for i, (key, label, map_key, display_key) in enumerate(relations_list):
            ttk.Label(relations_frame, text=f"{label} ID:").grid(row=i, column=0, sticky='w', padx=2, pady=3)
            
            entry = ttk.Entry(relations_frame, width=20)
            entry.grid(row=i, column=1, sticky='we', padx=5, pady=3)
            self.relation_widgets[key] = entry
            
            # ปุ่มเลือกรายการ/เพิ่มสี
            if key == 'color_ids':
                 color_btn_frame = ttk.Frame(relations_frame)
                 color_btn_frame.grid(row=i, column=2, sticky='w', padx=5, pady=3)
                 ttk.Button(color_btn_frame, 
                            text="[เลือก]", 
                            command=lambda k=key, mk=map_key, dk=display_key: self.open_select_modal(k, mk, dk),
                            width=6).pack(side='left', padx=1)
                 ttk.Button(color_btn_frame, 
                            text="[+เพิ่มสี]", 
                            command=self.open_add_color_modal,
                            width=6).pack(side='left', padx=1)
            else:
                 ttk.Button(relations_frame, 
                            text="[เลือกรายการ]", 
                            command=lambda k=key, mk=map_key, dk=display_key: self.open_select_modal(k, mk, dk),
                            width=12).grid(row=i, column=2, sticky='w', padx=5, pady=3)


        # --- BOTTOM: Control Buttons ---
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill='x', pady=10)
        
        # FIX: ใช้ Style ปุ่มค้นหาใหม่
        save_text = "บันทึกข้อมูล" if self.mode == 'add' else "อัปเดตข้อมูล"
        ttk.Button(control_frame, 
                   text=save_text, 
                   command=self.save_stone,
                   style='SearchButton.TButton').pack(side='left', padx=10, fill='x', expand=True)

        ttk.Button(control_frame, text="ยกเลิก", command=self.destroy).pack(side='right', padx=10, fill='x', expand=True)


    def load_data(self):
        """โหลดข้อมูลหินที่มีอยู่เข้าสู่ฟอร์ม (เฉพาะโหมด Edit)"""
        if self.mode == 'edit' and self.stone:
            self.id_entry.config(state='normal')
            self.id_entry.insert(0, self.stone.get('id', 'N/A'))
            self.id_entry.config(state='readonly')

            self.thai_name_entry.insert(0, self.stone.get('thai_name', ''))
            self.english_name_entry.insert(0, self.stone.get('english_name', ''))
            self.other_names_entry.insert(0, self.stone.get('other_names', ''))
            self.description_text.insert('1.0', self.stone.get('description', ''))
            
            # Load Relation IDs (Replace space with comma for editing clarity)
            for key, entry in self.relation_widgets.items():
                ids_str = self.stone.get(key, '').replace(' ', ', ')
                entry.insert(0, ids_str)
        elif self.mode == 'add':
             # ตั้งค่า ID สำหรับโหมดเพิ่ม
             new_id = generate_new_id(self.parent.all_stones)
             self.id_entry.config(state='normal')
             self.id_entry.insert(0, str(new_id))
             self.id_entry.config(state='readonly')


    def open_select_modal(self, key: str, map_key: str, display_key: str):
        """เปิด Modal เลือกรายการหลายรายการ"""
        current_ids = self.relation_widgets[key].get()
        
        # เปิด Modal
        modal = MultiSelectModal(self, 
                                 f"เลือก {key}", 
                                 self.parent.ALL_DATA[map_key], 
                                 display_key, 
                                 current_ids)
                                 
        # เมื่อ Modal ปิด ให้ดึงผลลัพธ์กลับมาใส่ใน Entry
        if modal.result_ids is not None:
             self.relation_widgets[key].delete(0, tk.END)
             self.relation_widgets[key].insert(0, modal.result_ids)

    def open_add_color_modal(self):
        """เปิด Modal เพิ่มสีใหม่"""
        modal = AddColorModal(self)
        
        # หากมีการเพิ่มสีใหม่ ให้โหลดข้อมูลหลักใหม่ทั้งหมด
        if modal.new_color_id > 0:
            self.parent.ALL_DATA = load_all_data() # โหลดข้อมูลหลักใหม่
            
            messagebox.showinfo("Info", "ข้อมูลสีถูกอัปเดตแล้ว โปรดทราบว่าการแก้ไขรายการที่กำลังทำอยู่ต้องกรอก ID สีใหม่ด้วยตนเอง")


    def save_stone(self):
        """จัดการการบันทึกข้อมูล (เพิ่ม/แก้ไข)"""
        
        stone_id = self.id_entry.get()
        thai_name = self.thai_name_entry.get().strip()
        english_name = self.english_name_entry.get().strip()
        description = self.description_text.get('1.0', tk.END).strip()
        
        if not thai_name or not english_name:
            messagebox.showerror("Error", "กรุณาระบุชื่อไทยและชื่ออังกฤษ")
            return

        # 2. จัดการข้อมูลความสัมพันธ์ (แปลง Comma/Space เป็น Space สำหรับบันทึก)
        relation_data = {}
        for key, entry in self.relation_widgets.items():
            raw_ids = entry.get().strip()
            # แทนที่ Comma ด้วย Space และกรอง Space ที่เกินมา
            normalized_ids = ' '.join(raw_ids.replace(',', ' ').split())
            relation_data[key] = normalized_ids
            
        # 3. สร้าง Object หินใหม่
        new_stone = {
            'id': int(stone_id),
            'thai_name': thai_name,
            'english_name': english_name,
            'other_names': self.other_names_entry.get().strip(),
            'description': description,
            **relation_data
        }

        # 4. อัปเดต List หลัก (self.parent.all_stones)
        if self.mode == 'edit':
            for i, stone in enumerate(self.parent.all_stones):
                if stone.get('id') == new_stone['id']:
                    self.parent.all_stones[i] = new_stone
                    break
            message = f"อัปเดตข้อมูลหิน {thai_name} สำเร็จ"
        else: # Add Mode
            self.parent.all_stones.append(new_stone)
            message = f"เพิ่มหิน {thai_name} สำเร็จ"

        # 5. บันทึกกลับไปที่ JSON
        if save_stones_to_json(self.parent.all_stones):
            messagebox.showinfo("บันทึกสำเร็จ", message)
            
            # 6. อัปเดตหน้าจอหลัก
            self.parent.filtered_stones = self.parent.all_stones.copy()
            self.parent.render_stone_table() 
            self.destroy()
        else:
             messagebox.showerror("บันทึกไม่สำเร็จ", "การบันทึกไฟล์ JSON ล้มเหลว")


class LookupCrudModal(tk.Toplevel):
    """
    Modal Dialog สำหรับเพิ่ม/แก้ไข ข้อมูล Lookup (Chakra, Element, Numerology)
    """
    def __init__(self, parent: 'PyStoneApp', key: str, mode: str, item_data: Dict[str, Any]):
        super().__init__(parent)
        self.parent_app = parent
        self.key = key  # เช่น 'chakra', 'element', 'numerology'
        self.mode = mode
        self.item = item_data if item_data else {}
        
        lookup_name_map = {
            'chakra': 'จักระ', 
            'element': 'ธาตุ', 
            'numerology': 'เลขมงคล'
        }
        self.display_name = lookup_name_map.get(key, 'Lookup Item')
        
        self.title(f"{'แก้ไข' if mode == 'edit' else 'เพิ่ม'} {self.display_name}")
        self.geometry("750x450")
        self.resizable(False, True)
        self.grab_set()
        
        self.create_form()
        self.load_data()

    def create_form(self):
        main_frame = ttk.Frame(self, padding="15")
        main_frame.pack(fill='both', expand=True)
        
        # --- ID & Name ---
        info_frame = ttk.Frame(main_frame)
        info_frame.pack(fill='x', pady=5)
        
        ttk.Label(info_frame, text="ID:").grid(row=0, column=0, sticky='w', padx=5)
        self.id_entry = ttk.Entry(info_frame, width=5)
        self.id_entry.grid(row=0, column=1, sticky='w', padx=5, pady=2)
        self.id_entry.config(state='readonly')
        
        ttk.Label(info_frame, text="ชื่อไทย:", font=('Tahoma', 10, 'bold')).grid(row=0, column=2, sticky='w', padx=15)
        self.name_th_entry = ttk.Entry(info_frame, width=30)
        self.name_th_entry.grid(row=0, column=3, sticky='we', padx=5, pady=2)
        
        if self.key == 'numerology':
             ttk.Label(info_frame, text="ค่าตัวเลข (1-9):", font=('Tahoma', 10, 'bold')).grid(row=1, column=0, sticky='w', padx=5)
             self.number_entry = ttk.Entry(info_frame, width=5)
             self.number_entry.grid(row=1, column=1, sticky='w', padx=5, pady=2)
        
        # หากเป็นจักระ เพิ่มชื่ออังกฤษ/ตำแหน่ง/สี เพื่อให้แก้ไขได้ง่ายขึ้น
        if self.key == 'chakra':
             ttk.Label(info_frame, text="ชื่ออังกฤษ:", font=('Tahoma', 10, 'bold')).grid(row=1, column=2, sticky='w', padx=15)
             self.name_en_entry = ttk.Entry(info_frame, width=30)
             self.name_en_entry.grid(row=1, column=3, sticky='we', padx=5, pady=2)
             
             ttk.Label(info_frame, text="ตำแหน่ง:", font=('Tahoma', 10, 'bold')).grid(row=2, column=0, sticky='w', padx=5)
             self.location_entry = ttk.Entry(info_frame, width=20)
             self.location_entry.grid(row=2, column=1, sticky='w', padx=5, pady=2)
             
             ttk.Label(info_frame, text="สี:", font=('Tahoma', 10, 'bold')).grid(row=2, column=2, sticky='w', padx=15)
             self.color_entry = ttk.Entry(info_frame, width=20)
             self.color_entry.grid(row=2, column=3, sticky='we', padx=5, pady=2)
             
             ttk.Label(info_frame, text="Logo:", font=('Tahoma', 10, 'bold')).grid(row=3, column=0, sticky='w', padx=5)
             self.logo_entry = ttk.Entry(info_frame, width=20)
             self.logo_entry.grid(row=3, column=1, sticky='w', padx=5, pady=2)

        # --- Detail Text Areas ---
        ttk.Label(main_frame, text="รายละเอียดประวัติศาสตร์ (history_th):", font=('Tahoma', 10, 'bold')).pack(anchor='w', pady=5)
        self.history_text = tk.Text(main_frame, wrap="word", height=5, width=80)
        self.history_text.pack(fill='x', pady=2)

        ttk.Label(main_frame, text="รายละเอียดมงคลเชิงลึก (auspice_detail_th):", font=('Tahoma', 10, 'bold')).pack(anchor='w', pady=5)
        self.auspice_text = tk.Text(main_frame, wrap="word", height=7, width=80)
        self.auspice_text.pack(fill='x', pady=2)

        # --- Control Buttons ---
        control_frame = ttk.Frame(self, padding="0 10 0 10")
        control_frame.pack(fill='x')
        
        save_text = "บันทึกข้อมูล" if self.mode == 'add' else "อัปเดตข้อมูล"
        ttk.Button(control_frame, 
                   text=save_text, 
                   command=self.save_item,
                   style='SearchButton.TButton').pack(side='left', padx=15, fill='x', expand=True)

        if self.mode == 'edit':
             ttk.Button(control_frame, 
                        text="ลบรายการนี้", 
                        command=self.delete_item,
                        style='AddButton.TButton').pack(side='left', padx=15, fill='x', expand=True)

        ttk.Button(control_frame, text="ยกเลิก", command=self.destroy).pack(side='right', padx=15, fill='x', expand=True)

    def load_data(self):
        if self.mode == 'edit' and self.item:
            self.id_entry.config(state='normal')
            self.id_entry.insert(0, self.item.get('id', 'N/A'))
            self.id_entry.config(state='readonly')

            self.name_th_entry.insert(0, self.item.get('name_th', ''))
            
            if self.key == 'numerology':
                 self.number_entry.insert(0, self.item.get('number_value', ''))
            
            if self.key == 'chakra':
                 self.name_en_entry.insert(0, self.item.get('name_en', ''))
                 self.location_entry.insert(0, self.item.get('location', ''))
                 self.color_entry.insert(0, self.item.get('color', ''))
                 self.logo_entry.insert(0, self.item.get('logo', ''))
            
            # Load Text Areas
            self.history_text.insert('1.0', self.item.get('history_th', ''))
            self.auspice_text.insert('1.0', self.item.get('auspice_detail_th', ''))
        
        elif self.mode == 'add':
            # Set New ID
            current_list = self.parent_app.ALL_DATA[self.key]
            new_id = generate_new_id(current_list)
            self.id_entry.config(state='normal')
            self.id_entry.insert(0, str(new_id))
            self.id_entry.config(state='readonly')

    def save_item(self):
        new_data = {
            'id': int(self.id_entry.get()),
            'name_th': self.name_th_entry.get().strip(),
            'history_th': self.history_text.get('1.0', tk.END).strip(),
            'auspice_detail_th': self.auspice_text.get('1.0', tk.END).strip()
        }
        
        # จัดการ fields เฉพาะ
        if self.key == 'numerology':
             try:
                 new_data['number_value'] = int(self.number_entry.get())
             except:
                 messagebox.showerror("Error", "ค่าตัวเลขต้องเป็นจำนวนเต็มเท่านั้น")
                 return
        
        if self.key == 'chakra':
             new_data['name_en'] = self.name_en_entry.get().strip()
             new_data['location'] = self.location_entry.get().strip()
             new_data['color'] = self.color_entry.get().strip()
             new_data['logo'] = self.logo_entry.get().strip()
        
        # คัดลอกข้อมูลเก่าที่ไม่เกี่ยวข้องกับ CRUD text fields (เช่น name_en, color, location)
        # เพื่อป้องกันข้อมูลอื่น ๆ หายไปเมื่อทำการ Update
        new_data = {**self.item, **new_data} 
        
        # 1. อัปเดต List หลัก (self.parent_app.ALL_DATA)
        current_list = self.parent_app.ALL_DATA[self.key]
        
        if self.mode == 'edit':
            for i, item in enumerate(current_list):
                if item.get('id') == new_data['id']:
                    current_list[i] = new_data
                    break
            message = f"อัปเดตข้อมูล {self.display_name} ID:{new_data['id']} สำเร็จ"
        else:
            current_list.append(new_data)
            message = f"เพิ่มข้อมูล {self.display_name} ID:{new_data['id']} สำเร็จ"
            
        # 2. บันทึกกลับไปที่ JSON
        if self._save_lookup_to_json(current_list):
            messagebox.showinfo("บันทึกสำเร็จ", message)
            self.parent_app.ALL_DATA = load_all_data() # โหลดข้อมูลหลักใหม่เพื่ออัปเดต Pop-up
            self.destroy()
        else:
             messagebox.showerror("บันทึกไม่สำเร็จ", "การบันทึกไฟล์ JSON ล้มเหลว")

    def delete_item(self):
         if messagebox.askyesno("ยืนยันการลบ", f"คุณต้องการลบ {self.display_name} ID: {self.item['id']} ใช่หรือไม่?"):
            current_list = self.parent_app.ALL_DATA[self.key]
            
            # ลบออกจาก List
            new_list = [item for item in current_list if item.get('id') != self.item['id']]

            # บันทึกกลับไปที่ JSON
            if self._save_lookup_to_json(new_list):
                messagebox.showinfo("ลบข้อมูล", f"ลบ {self.display_name} ID: {self.item['id']} เรียบร้อยแล้ว")
                self.parent_app.ALL_DATA = load_all_data() # โหลดข้อมูลหลักใหม่
                self.destroy()
            else:
                 messagebox.showerror("ลบไม่สำเร็จ", "การบันทึกไฟล์ JSON ล้มเหลว")


    def _save_lookup_to_json(self, data_list: List[Dict[str, Any]]):
        """Helper function สำหรับบันทึกข้อมูล Lookup กลับไปยังไฟล์ JSON"""
        file_path = os.path.join(DATA_FOLDER, f'lookup_{self.key}.json')
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data_list, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            messagebox.showerror("Save Error", f"ไม่สามารถบันทึกไฟล์ {file_path} ได้: {e}")
            return False


class PyStoneApp(tk.Tk):
    # ------------------------------------------------------------------
    # 3. MAIN APPLICATION CLASS
    # ------------------------------------------------------------------
    def __init__(self, all_data):
        self.ALL_DATA = all_data
        
        super().__init__()
        self.title("PyStone: ระบบจัดการและค้นหาหินมงคล")
        self.geometry("1400x900")
        
        # กำหนด Style Global
        self.style = ttk.Style(self)
        self.style.configure('TFrame', background='#f0f0f0')
        self.style.configure('Header.TLabel', font=('Tahoma', 12, 'bold'), foreground='#4CAF50') 
        
        # FIX: ปรับสีปุ่มค้นหาให้เป็น แดง/ขาว
    
        self.style.configure('SearchButton.TButton', 
                             font=('Tahoma', 12, 'bold'), 
                             background="#E0D4D4", 
                             foreground="#D10909", 
                             padding=[5, 2]) 
        self.style.map('SearchButton.TButton', 
                       background=[('active', "#C70B0B")], 
                       foreground=[('active', "#090909")]) # สีขณะคลิก/ชี้

    
        # FIX: Style ปุ่มเพิ่มข้อมูล (ใช้ Style เดียวกับปุ่มค้นหา)
        self.style.configure('AddButton.TButton', 
                             font=('Tahoma', 12, 'bold'), 
                             background="#E3D9D9", 
                             foreground="#D10909", #  ตัวอักษร
                             padding=[5, 2]) 
        self.style.map('AddButton.TButton', 
                       background=[('active', "#C70B0B")], 
                       foreground=[('active',"#090909")]) 


        self.all_stones = self.ALL_DATA['stones']
        self.filtered_stones = self.all_stones.copy()
        
        # Pagination Control
        self.rows_per_page = 20
        self.current_page = 1
        
        # UI Setup
        self.create_widgets()
        self.render_stone_table() 

    def create_widgets(self):
        """สร้าง Layout หลักของแอปพลิเคชัน"""
        
        # --- Main Frame ---
        main_frame = ttk.Frame(self, padding="8")
        main_frame.pack(fill='both', expand=True)
        
        # --- 2. Search and Control Panel ---
        self.search_frame = ttk.LabelFrame(main_frame, text="⚙️ เครื่องมือค้นหาและจัดการ", padding="8")
        self.search_frame.pack(fill='x', pady=5)
        
        # Search Tabs (ใช้ Frame แทน TabControl เพื่อความยืดหยุ่น)
        tab_frame = ttk.Frame(self.search_frame)
        tab_frame.pack(fill='x', pady=5)
        
        self.search_modes = {} 
        self.current_mode = tk.StringVar(value='name')
        
        # *** DEFINE self.search_panel ***
        self.search_panel = ttk.Frame(self.search_frame, borderwidth=1, relief="solid", padding="5")
        self.search_panel.pack(fill='x')
        
        # 2.1 Tab Buttons
        modes = [
            ("ค้นหาตามชื่อหิน", 'name'), 
            ("ค้นตามกลุ่มมงคล", 'group'), 
            ("ค้นตาม วดป.เกิด", 'date'), 
            ("ค้นหาแบบมีเงื่อนไข", 'condition'),
            # FIX: เปลี่ยนกลับมาใช้ show_lookup_detail_popup (Read-Only)
            ("รายละเอียดจักระ", 'Chakra', lambda: self.show_lookup_detail_popup('chakra')),
            ("รายละเอียดธาตุ", 'Element', lambda: self.show_lookup_detail_popup('element')),
            ("รายละเอียดเลขมงคล", 'Numerology', lambda: self.show_lookup_detail_popup('numerology'))
        ]
        
        for item in modes:
            text = item[0]
            mode = item[1]
            command = item[2] if len(item) > 2 else lambda m=mode: self.switch_search_mode(m)
            
            btn = ttk.Button(tab_frame, text=text, command=command)
            btn.pack(side='left', padx=3)
            
            # สร้าง Frame เฉพาะสำหรับโหมดค้นหาเท่านั้น
            if mode not in ('Chakra', 'Element', 'Numerology'):
                self.search_modes[mode] = self.create_search_mode_frame(mode)
            
        # 2.3 Display the initial Frame
        if 'name' in self.search_modes:
            self.search_modes['name'].pack(fill='x')
        
        # --- 2.5 Summary Area for Search (ย้ายมาอยู่ใต้ปุ่มเพิ่มข้อมูล) ---
        self.summary_control_frame = ttk.Frame(main_frame)
        self.summary_control_frame.pack(fill='x', pady=5)
        
        
        # Report Label (Top Left)
        self.report_label = ttk.Label(self.summary_control_frame, text="พบหิน:**0**รายการ", style='Header.TLabel')
        self.report_label.pack(side='left', padx=3)
        
        # 3. Pagination Controls (Top Right)
        self.top_pagination_frame = ttk.Frame(self.summary_control_frame)
        self.top_pagination_frame.pack(side='right', padx=8)
        
        # FIX: ปุ่ม +เพิ่มข้อมูล ถูกย้ายไปอยู่หน้าปุ่ม "ก่อนหน้า" ใน setup_pagination_controls
        self.setup_pagination_controls(self.top_pagination_frame, is_top=True)
        
        
        # 3.5 Summary Labels (อยู่ระหว่าง Report Label และ Pagination)
        self.top_summary_label = ttk.Label(self.summary_control_frame, text="ผลการค้นหา", foreground='blue', justify='left')
        self.top_summary_label.pack(side='left', padx=8, fill='x', expand=True)

        
        # --- 4. Stone Table (Treeview) ---
        
        columns = ('#', 'Name', 'Color', 'Day', 'Chakra', 'Element', 'Numerology', 'Actions')
        self.tree = ttk.Treeview(main_frame, columns=columns, show='headings', height=25) 
        
        # Set Column Headings and Widths (ปรับความกว้าง)
        
        self.tree.heading('#', text='ลำดับ', anchor='center'); self.tree.column('#', width=50, stretch=tk.NO, anchor='center')
        self.tree.heading('Name', text='ชื่อหิน (ไทย/อังกฤษ/อื่น ๆ)', anchor='center'); self.tree.column('Name', width=300, anchor='w') 
        self.tree.heading('Color', text='สีหลัก', anchor='center'); self.tree.column('Color', width=150, anchor='w')
        self.tree.heading('Day', text='วันมงคล', anchor='center'); self.tree.column('Day', width=120, anchor='w')
        self.tree.heading('Chakra', text='จักระ', anchor='center'); self.tree.column('Chakra', width=120, anchor='w')
        self.tree.heading('Element', text='ธาตุ', anchor='center'); self.tree.column('Element', width=120, anchor='w')
        self.tree.heading('Numerology', text='เลขมงคล', anchor='center'); self.tree.column('Numerology', width=60, anchor='w')
        self.tree.heading('Actions', text='จัดการ', anchor='center'); self.tree.column('Actions', width=100, stretch=tk.NO, anchor='center') 
        
        # Apply Custom Tag Styles
        self.tree.tag_configure('unlucky', background='#FFCCCC', foreground='red', font=('Tahoma', 9, 'bold'))
        self.tree.tag_configure('normal', background='#F7F7F7', foreground='black', font=('Tahoma', 9))
        self.tree.tag_configure('odd', background='#EFEFEF', foreground='black', font=('Tahoma', 9))

        self.tree.pack(fill='both', expand=True)
        
        # --- 5. Pagination Controls (Bottom) ---
        self.bottom_pagination_frame = ttk.Frame(main_frame)
        self.bottom_pagination_frame.pack(fill='x', pady=5)
        self.setup_pagination_controls(self.bottom_pagination_frame, is_top=False)
        
        # --- 6. Event Bindings for Actions Column ---
        self.tree.bind('<ButtonRelease-1>', self.handle_action_click)


    def set_search_widgets_state(self, state: str):
        """
        FIX: ฟังก์ชันสำหรับเปิด/ปิดการใช้งานช่องค้นหาทั้งหมดในโหมดปัจจุบัน
        """
        mode = self.current_mode.get()
        frame = self.search_modes.get(mode)
        if frame:
            # 1. จัดการ Entry และ Combobox
            for child in frame.winfo_children():
                if isinstance(child, (ttk.Entry, ttk.Combobox)):
                    child.config(state='readonly' if state == 'disabled' else state)
                
                # 2. จัดการปุ่มค้นหาหลัก (Button)
                elif isinstance(child, ttk.Button) and child.cget('text') in ('ค้นหา', 'ค้นหาหินตาม วดป.', 'ค้นหาด้วยเงื่อนไข'):
                    child.config(state=state)
                
                # 3. จัดการปุ่มเพิ่มข้อมูล (ต้องจัดการแยกในโหมด condition)
                elif isinstance(child, ttk.Button) and child.cget('text') == '+ เพิ่มข้อมูล':
                     child.config(state=state)


    def clear_search_inputs(self):
        """เคลียร์ค่าในช่องค้นหาเมื่อเปลี่ยนโหมด"""
        try:
            if self.current_mode.get() == 'name':
                self.name_search_entry.delete(0, tk.END)
            elif self.current_mode.get() == 'group':
                self.group_select.set('--ทั้งหมด--')
            elif self.current_mode.get() == 'date':
                self.date_search_entry.delete(0, tk.END)
            elif self.current_mode.get() == 'condition':
                self.cond_day_select.set('--ทั้งหมด--')
                self.cond_month_select.set('--ทั้งหมด--')
                self.cond_animal_select.set('--ทั้งหมด--')
                self.cond_sign_select.set('--ทั้งหมด--')
        except Exception:
            pass # ป้องกัน Error หาก widget ยังไม่ถูกสร้าง


    def setup_pagination_controls(self, parent_frame: ttk.Frame, is_top: bool):
        """ตั้งค่าปุ่มและ Label สำหรับ Pagination"""
        
        label_text = 'Top' if is_top else 'Bottom'
        
        # Page Info Label
        setattr(self, f'page_info_label_{label_text}', ttk.Label(parent_frame, text="หน้า 1 ใน 1"))
        getattr(self, f'page_info_label_{label_text}').pack(side='right', padx=8)
        
        # Next Button
        setattr(self, f'next_btn_{label_text}', ttk.Button(parent_frame, text="ถัดไป>", command=lambda: self.change_page(1)))
        getattr(self, f'next_btn_{label_text}').pack(side='right')

        # Previous Button
        setattr(self, f'prev_btn_{label_text}', ttk.Button(parent_frame, text="<ก่อนหน้า", command=lambda: self.change_page(-1)))
        getattr(self, f'prev_btn_{label_text}').pack(side='right')

        # FIX: ปุ่ม +เพิ่มข้อมูล ถูกย้ายไปอยู่หน้าปุ่ม 'ก่อนหน้า'
        if is_top:
            ttk.Button(parent_frame, 
                       text="+ เพิ่มข้อมูล", 
                       command=lambda: self.open_crud_modal('add', None),
                       style='AddButton.TButton').pack(side='right', padx=8)

        

    def create_search_mode_frame(self, mode: str) -> ttk.Frame:
        """สร้าง Frame สำหรับ Search Mode ต่างๆ"""
        
        frame = ttk.Frame(self.search_panel, padding="5")
        
        if mode == 'name':
            ttk.Label(frame, text="ชื่อหิน (ไทย/อังกฤษ):").pack(side='left', padx=5, pady=5)
            self.name_search_entry = ttk.Entry(frame, width=40)
            self.name_search_entry.pack(side='left', padx=5, pady=5)
            # FIX: ใช้ Style ปุ่มค้นหาใหม่
            ttk.Button(frame, text="ค้นหา", command=lambda: self.filter_data(mode), style='SearchButton.TButton').pack(side='left', padx=5)
            
        elif mode == 'group':
            ttk.Label(frame, text="กลุ่มมงคล:").pack(side='left', padx=5, pady=5)
            # สร้าง Map แยกไว้สำหรับ Lookup ใน filter_data
            self.group_select_map = {g['name']: g['id'] for g in self.ALL_DATA['groups']}
            self.group_select = ttk.Combobox(frame, values=['--ทั้งหมด--'] + [g['name'] for g in self.ALL_DATA['groups']], width=30)
            self.group_select.set('--ทั้งหมด--')
            self.group_select.pack(side='left', padx=5, pady=5)
            # FIX: ใช้ Style ปุ่มค้นหาใหม่
            ttk.Button(frame, text="ค้นหา", command=lambda: self.filter_data(mode), style='SearchButton.TButton').pack(side='left', padx=5)
            
        elif mode == 'date':
            ttk.Label(frame, text="วัน/เดือน/พ.ศ.(DD/MM/YYYY พ.ศ.):").pack(side='left', padx=5, pady=5)
            self.date_search_entry = ttk.Entry(frame, width=15)
            self.date_search_entry.pack(side='left', padx=5, pady=5)
            # FIX: ใช้ Style ปุ่มค้นหาใหม่
            ttk.Button(frame, text="ค้นหาหินตาม วดป.", command=lambda: self.filter_data(mode), style='SearchButton.TButton').pack(side='left', padx=8)
            # NOTE: Label สรุปถูกย้ายไปที่ self.top_summary_label
            
        elif mode == 'condition':
            # Dropdowns สำหรับค้นหาแบบมีเงื่อนไข (AND Logic)
            ttk.Label(frame, text="เงื่อนไข (AND):").pack(side='left', padx=5, pady=5)

            # FIX: ใช้ custom_label เพื่อแสดงชื่อช่องที่ถูกต้อง (วัน:, เดือน:, นักษัตร:, ราศี:)
            self.cond_day_select = self.create_combobox(frame, self.ALL_DATA['days'], 'name', 'day_id', custom_label="วัน:")
            self.cond_month_select = self.create_combobox(frame, self.ALL_DATA['months'], 'name', 'month_id', custom_label="เดือน:")
            self.cond_animal_select = self.create_combobox(frame, self.ALL_DATA['animals'], 'thai_name', 'animal_id', custom_label="นักษัตร:")
            self.cond_sign_select = self.create_combobox(frame, self.ALL_DATA['signs'], 'name', 'sign_id', custom_label="ราศี:")

            # FIX: ใช้ Style ปุ่มค้นหาใหม่
            ttk.Button(frame, text="ค้นหาด้วยเงื่อนไข", command=lambda: self.filter_data(mode), style='SearchButton.TButton').pack(side='left', padx=5)
            
            # NOTE: ปุ่ม +เพิ่มข้อมูล ถูกย้ายไปที่ setup_pagination_controls
            
        return frame
    
    def create_combobox(self, parent_frame, data_list, display_key, attr_name, custom_label: str = None):
        """Helper to create Comboboxes for search conditions (FIX: ใช้ custom_label)"""
        
        mapping = {item[display_key]: item['id'] for item in data_list}
        mapping['--ทั้งหมด--'] = 0 
        
        # FIX: ใช้ custom_label ที่ถูกต้อง
        label_text = custom_label if custom_label else f"{display_key.capitalize()}:"
        ttk.Label(parent_frame, text=label_text).pack(side='left', padx=5)
        
        cb = ttk.Combobox(parent_frame, 
                          values=['--ทั้งหมด--'] + [item[display_key] for item in data_list], 
                          width=15, state='readonly') 
        cb.set('--ทั้งหมด--')
        cb.pack(side='left', padx=5)
        
        # เก็บ map และ Combobox object ไว้ใน instance variable
        setattr(self, f'{attr_name}_map', mapping) # self.day_id_map (Map)
        setattr(self, f'{attr_name}_cb', cb)       # self.day_id_cb (Combobox object)
        
        # FIX: ผูก Event เพื่ออัปเดต Cond Summary เมื่อมีการเปลี่ยนค่าใน Dropdown วัน (ไม่เรียก filter_data)
        if attr_name == 'day_id':
             cb.bind("<<ComboboxSelected>>", lambda e: self.update_cond_summary_label())


        return cb


    def switch_search_mode(self, mode: str):
        """ซ่อน Frame เก่าและแสดง Frame ใหม่เมื่อเปลี่ยน Tab ค้นหา"""
        
        # 1. เปิดการใช้งานและเคลียร์ข้อมูลเก่า (FIXED)
        self.set_search_widgets_state('normal')
        self.clear_search_inputs()
        self.top_summary_label.config(text="ผลการค้นหา", foreground='blue')

        # 2. แสดง Frame ใหม่
        for frame in self.search_modes.values():
            frame.pack_forget()
        self.search_modes[mode].pack(fill='x')
        self.current_mode.set(mode)
        
        # 3. หากสลับไปโหมด condition ให้อัปเดตสรุปสีทันที (เพื่อแสดงค่าเริ่มต้น)
        if mode == 'condition':
            self.update_cond_summary_label()
        
    
    def filter_data(self, mode: str):
        """ฟังก์ชันหลักในการกรองข้อมูลตามโหมดที่เลือก"""
        
        self.filtered_stones = self.all_stones.copy()
        current_day_id = 0 
        search_params = {}
        
        try:
            if mode == 'name':
                search_term = self.name_search_entry.get().strip().lower()
                if search_term:
                    self.filtered_stones = [s for s in self.filtered_stones if search_term in s['thai_name'].lower() or search_term in s['english_name'].lower() or search_term in s['other_names'].lower()]
                
                if not search_term:
                    self.filtered_stones = self.all_stones.copy()
            
            elif mode == 'group':
                group_name = self.group_select.get()
                group_id = self.group_select_map.get(group_name, 0)
                if group_id:
                    search_params['group_id'] = str(group_id)
                else: 
                    self.filtered_stones = self.all_stones.copy()
            
            elif mode == 'date':
                date_th = self.date_search_entry.get().strip()
                if not date_th:
                    messagebox.showwarning("Warning", "กรุณาระบุ วัน/เดือน/พ.ศ.")
                    return
                
                auspice_result = calculate_auspice_ids(date_th, self.ALL_DATA)
                if 'error' in auspice_result:
                    self.top_summary_label.config(text=f"❌ {auspice_result['error']}", foreground='red')
                    messagebox.showerror("Error", auspice_result['error'])
                    return

                search_params = {
                    'day_id': str(auspice_result['day_id']),
                    'month_id': str(auspice_result['month_id']),
                    'animal_id': str(auspice_result['animal_id']),
                    'sign_id': str(auspice_result['sign_id']),
                }
                current_day_id = auspice_result['day_id']
                # self.update_date_summary(auspice_result) # จะเรียกหลังการกรอง
            
            elif mode == 'condition':
                # อัปเดต Summary (ถูกเรียกผ่าน bind ใน Combobox อยู่แล้ว)
                
                day_id = getattr(self, 'day_id_map', {}).get(self.cond_day_select.get(), 0)
                if day_id: search_params['day_id'] = str(day_id)

                month_id = getattr(self, 'month_id_map', {}).get(self.cond_month_select.get(), 0)
                if month_id: search_params['month_id'] = str(month_id)
                
                animal_id = getattr(self, 'animal_id_map', {}).get(self.cond_animal_select.get(), 0)
                if animal_id: search_params['animal_id'] = str(animal_id)
                
                sign_id = getattr(self, 'sign_id_map', {}).get(self.cond_sign_select.get(), 0)
                if sign_id: search_params['sign_id'] = str(sign_id)
                
                current_day_id = day_id 
                
                if not search_params and all(cb.get() == '--ทั้งหมด--' for cb in [self.cond_day_select, self.cond_month_select, self.cond_animal_select, self.cond_sign_select]):
                    messagebox.showwarning("Warning", "กรุณาเลือกเงื่อนไขอย่างน้อยหนึ่งข้อ")
                    return
            
            # 1. เพิ่มเงื่อนไขสีมงคลก่อนส่งไปกรอง
            if current_day_id:
                lucky_color_ids = get_lucky_color_ids(current_day_id, self.ALL_DATA)
                if lucky_color_ids:
                    search_params['lucky_color_ids'] = lucky_color_ids

            
            # 2. Apply AND Search for ID parameters
            if search_params:
                self.filtered_stones = self.apply_auspice_filter(self.filtered_stones, search_params)

            # 3. Check for Unlucky Color (เฉพาะถ้ามีการระบุ Day ID)
            unlucky_count = 0
            if current_day_id:
                self.check_unlucky_colors_for_results(current_day_id)
                unlucky_count = sum(1 for stone in self.filtered_stones if stone.get('is_unlucky'))
            else:
                for stone in self.filtered_stones:
                    stone['is_unlucky'] = False
                    stone['unlucky_note'] = ""

            # 4. อัปเดต Summary Bar ด้วย Unlucky Count
            if mode == 'date':
                # ส่งผลลัพธ์การคำนวณและจำนวนหินอัปมงคลไปแสดงผล
                self.update_date_summary(auspice_result, unlucky_count)
            elif mode == 'condition' and current_day_id:
                self.update_cond_summary_label(unlucky_count)
            elif mode != 'date' and mode != 'condition':
                 self.top_summary_label.config(text="ข้อมูลสรุปการค้นหา", foreground='blue')

            # 5. FIX: ปิดการใช้งานช่องค้นหาเมื่อการค้นหาเสร็จสมบูรณ์
            self.set_search_widgets_state('disabled')


            self.current_page = 1
            self.render_stone_table()

        except Exception as e:
            messagebox.showerror("Error", f"เกิดข้อผิดพลาดในการค้นหา: {e}")
            self.filtered_stones = self.all_stones.copy()
            self.current_page = 1
            self.render_stone_table()


    def apply_auspice_filter(self, stones: List[Dict[str, Union[str, List[str]]]], params: Dict[str, Union[str, List[str]]]) -> List[Dict[str, Any]]:
        """
        ใช้ AND logic เพื่อกรองหินตาม ID ต่างๆ (Day, Month, Animal, Sign, Group, และ Lucky Color)
        """
        
        filtered = []
        # Mapping parameter key to stone data key
        param_to_stone_key = {
            'group_id': 'group_ids',
            'day_id': 'good_days',
            'month_id': 'good_months',
            'animal_id': 'good_zodiac_animals',
            'sign_id': 'good_zodiac_signs'
        }
        
        required_lucky_ids = set(params.get('lucky_color_ids', []))

        for stone in stones:
            is_match = True
            
            # 1. CHECK LUCKY COLOR CONDITION (OR Logic - ต้องมีสีมงคลอย่างน้อย 1 สี)
            if required_lucky_ids:
                stone_color_ids = set([str(id) for id in split_ids(stone.get('color_ids', ''))])
                
                # ถ้าไม่มีสีมงคลใดๆ เลยในหินนี้ -> NOT A MATCH
                if not (required_lucky_ids.intersection(stone_color_ids)):
                    is_match = False
            
            if not is_match:
                continue

            # 2. CHECK GENERAL AND CONDITIONS (วัน, เดือน, นักษัตร, ราศี)
            for param_key, param_val in params.items():
                if param_key == 'lucky_color_ids': 
                    continue # ข้ามสีมงคล เพราะถูกตรวจสอบแล้ว
                
                stone_key = param_to_stone_key.get(param_key)
                
                if not stone_key or not param_val or param_val == '0': continue
                
                # Check IDs against stone's relation IDs
                stone_ids = [str(id) for id in split_ids(stone.get(stone_key, ''))]
                
                # Special handling for Wednesday (Day ID 4:กลางวัน, 5:กลางคืน)
                if param_key == 'day_id' and param_val == '4': 
                    # ถ้าค้นด้วย ID 4 (พุธกลางวัน) ต้องรวมหินที่เหมาะกับ ID 4 หรือ ID 5
                    if '4' not in stone_ids and '5' not in stone_ids:
                        is_match = False
                        break
                elif param_val not in stone_ids:
                    is_match = False
                    break
            
            if is_match:
                filtered.append(stone)
                
        return filtered


    def check_unlucky_colors_for_results(self, day_id: int):
        """เพิ่ม Flag สีอัปมงคลให้กับรายการหินที่ถูกกรองแล้ว"""
        
        for stone in self.filtered_stones:
            stone['is_unlucky'] = False
            stone['unlucky_note'] = ""
            
            # ตรวจสอบสีอัปมงคล
            result = check_unlucky_color(stone['color_ids'], day_id, self.ALL_DATA)
            
            if result['is_unlucky']:
                stone['is_unlucky'] = True
                stone['unlucky_note'] = f"❌ มีสีอัปมงคล: {result['unlucky_colors_found']}"
            

    def update_date_summary(self, auspice_result: Dict[str, Union[int, str]], unlucky_count: int = 0):
        """อัปเดต Label แสดงผลสรุป วดป.เกิด (ย้ายไป self.top_summary_label)"""
        
        d_id = auspice_result['day_id']
        m_id = auspice_result['month_id']
        a_id = auspice_result['animal_id']
        s_id = auspice_result['sign_id']
        
        day_name = lookup_name(self.ALL_DATA['days'], d_id, 'name')
        
        # ตรรกะการแสดงผลสำหรับวันพุธ (กลางวัน/กลางคืน)
        day_info_html = ""
        if d_id == 4:
            day_info_day = next((d for d in self.ALL_DATA['days'] if d['id'] == 4), None)
            day_info_night = next((d for d in self.ALL_DATA['days'] if d['id'] == 5), None)
            
            if day_info_day and day_info_night:
                day_info_html = (
                    f"📅 วันพุธ | "
                    f"กลางวัน: มงคล:{day_info_day['lucky_color']} | อัปมงคล:{day_info_day['unlucky_color']} "
                    f"กลางคืน: มงคล:{day_info_night['lucky_color']} | อัปมงคล:{day_info_night['unlucky_color']}"
                )
        else:
            day_info = next((d for d in self.ALL_DATA['days'] if d['id'] == d_id), None)
            if day_info:
                 day_info_html = (
                    f"📅 วัน{day_info['name']} | "
                    f"มงคล: {day_info['lucky_color']} | อัปมงคล: {day_info['unlucky_color']}"
                )

        month_name = lookup_name(self.ALL_DATA['months'], m_id, 'name')
        animal_name = lookup_name(self.ALL_DATA['animals'], a_id, 'thai_name')
        sign_name = lookup_name(self.ALL_DATA['signs'], s_id, 'name')

        # FIX: รวม Unlucky Count ในวงเล็บ
        unlucky_note = f" (❌ {unlucky_count} มีหินสีอัปมงคล)" if unlucky_count > 0 else ""

        summary = (
            f"{day_info_html} | "
            f"📆 เดือน{month_name} | ปีนักษัตร: {animal_name} | ราศี: {sign_name}"
            f"{unlucky_note}"
        )
        
        self.top_summary_label.config(text=summary, foreground='blue', justify='left')


    def update_cond_summary_label(self, unlucky_count: int = 0):
        """อัปเดต Label สรุปสีมงคล/อัปมงคลเมื่อเลือกวันในโหมด Condition"""
        
        day_name = self.cond_day_select.get()
        day_id = getattr(self, 'day_id_map', {}).get(day_name, 0)
        
        if day_id == 0:
            self.top_summary_label.config(text="*เลือกวันเพื่อดูข้อมูลสี", foreground='darkgreen')
            return

        # ตรรกะการแสดงผลสำหรับวันพุธ (กลางวัน/กลางคืน)
        day_info_html = ""
        if day_id == 4 or day_id == 5:
            day_info_day = next((d for d in self.ALL_DATA['days'] if d['id'] == 4), None)
            day_info_night = next((d for d in self.ALL_DATA['days'] if d['id'] == 5), None)
            
            if day_info_day and day_info_night:
                day_info_html = (
                    f"📅 วันพุธ | "
                    f"กลางวัน: มงคล:{day_info_day['lucky_color']} | อัปมงคล:{day_info_day['unlucky_color']} "
                    f"กลางคืน: มงคล:{day_info_night['lucky_color']} | อัปมงคล:{day_info_night['unlucky_color']}"
                )
        else:
            day_info = next((d for d in self.ALL_DATA['days'] if d['id'] == day_id), None)
            if day_info:
                 day_info_html = (
                    f"📅 วัน{day_info['name']} | "
                    f"มงคล: {day_info['lucky_color']} | อัปมงคล: {day_info['unlucky_color']}"
                )
        
        # FIX: รวม Unlucky Count ในวงเล็บ
        unlucky_note = f" (❌ {unlucky_count} มีหินสีอัปมงคล)" if unlucky_count > 0 else ""
        
        self.top_summary_label.config(text=f"{day_info_html}{unlucky_note}", foreground='darkgreen', justify='left')
        
    
    # ... (filter_data, apply_auspice_filter, check_unlucky_colors_for_results เหมือนเดิม) ...

    # =======================================================
    # 4. TABLE RENDER AND PAGINATION
    # =======================================================

    def render_stone_table(self):
        """ล้างตารางและแสดงข้อมูลหินสำหรับหน้าปัจจุบัน (ปรับปรุงคอลัมน์)"""
        
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        total_rows = len(self.filtered_stones)
        total_pages = math.ceil(total_rows / self.rows_per_page) if total_rows > 0 else 1
        
        self.report_label.config(text=f"พบหิน:**{total_rows}** รายการ", style='Header.TLabel') # เน้นหัวข้อ

        # Get data for the current page
        start_index = (self.current_page - 1) * self.rows_per_page
        end_index = start_index + self.rows_per_page
        page_stones = self.filtered_stones[start_index:end_index]

        # Populate the table
        for i, stone in enumerate(page_stones):
            idx = start_index + i + 1
            
            # --- Data Lookup ---
            
            # FIX: ต้องเรียกใช้ format_lookup_list ที่ถูกย้ายไปด้านนอกแล้ว
            color_names = format_lookup_list(stone.get('color_ids', ''), self.ALL_DATA['colors'], 'name')
            day_names = format_lookup_list(stone.get('good_days', ''), self.ALL_DATA['days'], 'name')
            
            # NEW COLUMNS DATA
            chakra_names = format_lookup_list(stone.get('chakra_ids', ''), self.ALL_DATA.get('chakra', []), 'name_th')
            # **** FIX: ใช้คีย์ 'element' (ไม่มี s) ****
            element_names = format_lookup_list(stone.get('element_ids', ''), self.ALL_DATA.get('element', []), 'name_th')
            numerology_values = format_lookup_list(stone.get('numerology_ids', ''), self.ALL_DATA.get('numerology', []), 'number_value')
            
            # จัดรูปแบบชื่อหิน
            name_display = f"{stone['thai_name']} ({stone['english_name']})"
            if stone.get('other_names'):
                name_display += f" | {stone['other_names'][:30]}..." if len(stone['other_names']) > 30 else f" | {stone['other_names']}"
            
            # Column Numerology + Unlucky Note
            numerology_display = numerology_values
            
            # Col 8: Actions - FIX: แสดงเป็นปุ่มเดียวตามที่ขอ
            actions_display = "[ จัดการ ]"
            
            # --- Row Data and Tagging ---
            tag = 'unlucky' if stone.get('is_unlucky') else ('odd' if idx % 2 != 0 else 'normal')
            
            self.tree.insert('', 'end', 
                             values=(idx, name_display, color_names, day_names, 
                                     chakra_names, element_names, numerology_display, actions_display), 
                             tags=(tag,),
                             iid=stone['id']) 
            
        self.update_pagination_controls(total_pages, total_rows)


    def update_pagination_controls(self, total_pages: int, total_rows: int):
        """อัปเดตสถานะปุ่มและ Label การแบ่งหน้า"""
        
        page_text = f"หน้า {self.current_page} ใน {total_pages}" if total_rows > 0 else "หน้า 1 ใน 1"
        
        # Top
        self.page_info_label_Top.config(text=page_text)
        self.prev_btn_Top.config(state='disabled' if self.current_page <= 1 else 'normal')
        self.next_btn_Top.config(state='disabled' if self.current_page >= total_pages or total_rows == 0 else 'normal')

        # Bottom
        self.page_info_label_Bottom.config(text=page_text)
        self.prev_btn_Bottom.config(state='disabled' if self.current_page <= 1 else 'normal')
        self.next_btn_Bottom.config(state='disabled' if self.current_page >= total_pages or total_rows == 0 else 'normal')


    def change_page(self, direction: int):
        """เปลี่ยนหน้าปัจจุบัน"""
        total_pages = math.ceil(len(self.filtered_stones) / self.rows_per_page) if len(self.filtered_stones) > 0 else 1
        new_page = self.current_page + direction

        if 1 <= new_page <= total_pages:
            self.current_page = new_page
            self.render_stone_table()


    # =======================================================
    # 5. ACTION HANDLER (CRUD and External Search)
    # =======================================================

    def handle_action_click(self, event):
        """จัดการการคลิกในคอลัมน์ Actions (ใช้ simpledialog เพื่อเลือก action)"""
        
        item_id = self.tree.identify_row(event.y)
        col = self.tree.identify_column(event.x)
        
        if not item_id or col != '#8': # #8 คือคอลัมน์ Actions
            return

        stone_id = int(item_id)
        stone = next((s for s in self.all_stones if s['id'] == stone_id), None)
        if not stone: return

        # FIX: แทนที่ simpledialog ด้วยการเรียก Pop-up ปุ่มจริง
        self.show_action_popup(stone, event)


    def show_action_popup(self, stone, event):
        """
        แสดง Pop-up ที่มีปุ่ม Actions จริงให้เลือก (แทน simpledialog)
        """
        popup = tk.Toplevel(self)
        popup.title(f"จัดการ: {stone['thai_name']}")
        
        # ใช้ตำแหน่งคงที่เพื่อไม่ให้หลุดขอบ
        popup.geometry("300x300") 
        popup.transient(self) 
        popup.grab_set()      
        
        ttk.Label(popup, text=f"เลือก Actions สำหรับ {stone['thai_name']}", font=('Tahoma', 10, 'bold')).pack(pady=10)

        # Actions Buttons
        button_frame = ttk.Frame(popup)
        button_frame.pack(pady=5)

        ttk.Button(button_frame, text="1. รายละเอียด", command=lambda: [popup.destroy(), self.show_detail_popup(stone)]).pack(fill='x', padx=20, pady=2)
        ttk.Button(button_frame, text="2. แก้ไข", command=lambda: [popup.destroy(), self.open_crud_modal('edit', stone)]).pack(fill='x', padx=20, pady=2)
        ttk.Button(button_frame, text="3. ลบ", command=lambda: [popup.destroy(), self.delete_stone(stone)]).pack(fill='x', padx=20, pady=2)
        
        ttk.Separator(popup, orient='horizontal').pack(fill='x', padx=15, pady=5)
        
        # Search Buttons (เน้นสร้อยข้อมือ)
        ttk.Button(button_frame, text="Google", command=lambda: [self.search_external(stone, 'Google'), popup.destroy()]).pack(fill='x', padx=20, pady=2)
        ttk.Button(button_frame, text="Etsy", command=lambda: [self.search_external(stone, 'Etsy'), popup.destroy()]).pack(fill='x', padx=20, pady=2)

        ttk.Button(popup, text="ยกเลิก", command=popup.destroy).pack(pady=5)

    def search_external(self, stone: Dict[str, Any], platform: str):
        """ค้นหารูปภาพภายนอกโดยเปิด Tab ใหม่ในเบราว์เซอร์ (เน้นสร้อยข้อมือ)"""
        # FIX: เน้นคำค้นหา
        query = f"{stone['english_name']} auspicious stone bracelet jewelry" 
        if platform == 'Google':
            url = f"https://www.google.com/search?q={query}&tbm=isch"
        elif platform == 'Etsy':
            url = f"https://www.etsy.com/search?q={query}"
        
        webbrowser.open_new_tab(url)


    # =======================================================
    # 6. MODALS and CRUD PLACEHOLDERS 
    # =======================================================

    def open_crud_modal(self, mode: str, stone: Union[Dict[str, Any], None]):
        """เปิดหน้าต่างสำหรับเพิ่ม/แก้ไขข้อมูลหิน (FIXED)"""
        
        # FIX: เปิดการใช้งานช่องค้นหาทั้งหมดเมื่อกลับมาหน้าหลัก
        self.set_search_widgets_state('normal')

        if mode == 'add':
             stone_data = None
        else:
             stone_data = stone

        StoneCrudModal(self, mode, stone_data)

    def show_detail_popup(self, stone: Dict[str, Any]):
        """แสดงรายละเอียดหินแบบ Pop-up/Modal พร้อมปุ่ม Export"""
        
        detail_window = tk.Toplevel(self)
        detail_window.title(f"รายละเอียด: {stone['thai_name']}")
        detail_window.geometry("600x500")
        detail_window.resizable(True, True)

        # Main Frame
        main_frame = ttk.Frame(detail_window, padding="15")
        main_frame.pack(fill='both', expand=True)

        # Text Widget for Display
        text_widget = tk.Text(main_frame, wrap='word', font=('Tahoma', 10), padx=10, pady=10)
        text_widget.pack(fill='both', expand=True, side='left')

        # Scrollbar
        scrollbar = ttk.Scrollbar(main_frame, orient='vertical', command=text_widget.yview)
        scrollbar.pack(side='right', fill='y')
        text_widget.configure(yscrollcommand=scrollbar.set)

        # Format Detail Text
        detail_text = self.format_stone_detail(stone)
        text_widget.insert('1.0', detail_text)
        text_widget.config(state='disabled')  # Read-only

        # --- Control Buttons with Export ---
        control_frame = ttk.Frame(detail_window, padding="0 10 0 10")
        control_frame.pack(fill='x')
        
        filename_base = f"{stone['thai_name']}_detail"

        # Export Buttons
        ttk.Button(control_frame, 
                   text="Export (.txt)", 
                   command=lambda: export_to_file(detail_text, filename_base, 'text'),
                   style='SearchButton.TButton').pack(side='left', padx=5)
        
        ttk.Button(control_frame, 
                   text="Export (.pdf)", 
                   command=lambda: export_to_file(detail_text, filename_base, 'pdf'),
                   style='SearchButton.TButton').pack(side='left', padx=5)
        
        ttk.Button(control_frame, text="ปิด", command=detail_window.destroy).pack(side='right', padx=5)


    def format_stone_detail(self, stone: Dict[str, Any]) -> str:
        """จัดรูปแบบข้อความสำหรับแสดงรายละเอียดหิน"""
        
        def format_lookup_list_local(ids_str, lookup_data, display_key):
            ids = split_ids(ids_str)
            names = [lookup_name(lookup_data, id, display_key) for id in ids]
            return ', '.join(names) if names else '-'

        # Main Details
        lines = [
            f"ชื่อไทย: {stone['thai_name']}",
            f"ชื่ออังกฤษ: {stone['english_name']}",
            f"ชื่ออื่น ๆ: {stone.get('other_names', '-')}",
            f"คำอธิบาย: {stone.get('description', '-')[:200]}...",
            "",
            "--- ข้อมูลมงคล ---",
            f"กลุ่ม: {format_lookup_list_local(stone.get('group_ids', ''), self.ALL_DATA['groups'], 'name')}",
            f"สี: {format_lookup_list_local(stone.get('color_ids', ''), self.ALL_DATA['colors'], 'name')}",
            f"วันมงคล: {format_lookup_list_local(stone.get('good_days', ''), self.ALL_DATA['days'], 'name')}",
            f"เดือนมงคล: {format_lookup_list_local(stone.get('good_months', ''), self.ALL_DATA['months'], 'name')}",
            f"ปีนักษัตรมงคล: {format_lookup_list_local(stone.get('good_zodiac_animals', ''), self.ALL_DATA['animals'], 'thai_name')}",
            f"ราศีมงคล: {format_lookup_list_local(stone.get('good_zodiac_signs', ''), self.ALL_DATA['signs'], 'name')}",
            f"จักระ: {format_lookup_list_local(stone.get('chakra_ids', ''), self.ALL_DATA.get('chakra', []), 'name_th')}",
            # **** FIX: ใช้คีย์ 'element' (ไม่มี s) ****
            f"ธาตุ: {format_lookup_list_local(stone.get('element_ids', ''), self.ALL_DATA.get('element', []), 'name_th')}", 
            f"เลขศาสตร์: {format_lookup_list_local(stone.get('numerology_ids', ''), self.ALL_DATA.get('numerology', []), 'number_value')}",
            "",
            "--- ข้อมูลเพิ่มเติม ---",
            f"คำอธิบายเต็ม: {stone.get('description', '-')}",
        ]

        return '\n'.join(lines)


    def delete_stone(self, stone: Dict[str, Any]):
        """ยืนยันการลบข้อมูลหิน (Placeholder)"""
        if messagebox.askyesno("ยืนยันการลบ", f"คุณต้องการลบหิน '{stone['thai_name']}' ใช่หรือไม่?"):
            # 1. ลบจาก List หลัก
            self.all_stones.remove(stone)
            
            # 2. บันทึกกลับไปที่ JSON
            if save_stones_to_json(self.all_stones):
                messagebox.showinfo("ลบข้อมูล", f"ลบหิน {stone['thai_name']} เรียบร้อยแล้ว")
                
                # 3. อัปเดตหน้าจอหลัก
                self.filtered_stones = self.all_stones.copy()
                self.render_stone_table() 
            else:
                 messagebox.showerror("ลบไม่สำเร็จ", "การบันทึกไฟล์ JSON ล้มเหลวหลังการลบ")

    def open_lookup_crud_modal(self, key: str):
        """
        แสดง Pop-up ตาราง Lookup และปุ่ม CRUD สำหรับจักระ/ธาตุ/เลขมงคล
        """
        detail_window = tk.Toplevel(self)
        lookup_name_map = {
            'chakra': 'จักระ', 
            'element': 'ธาตุ', 
            'numerology': 'เลขมงคล'
        }
        display_name = lookup_name_map.get(key, 'Lookup Item')
        detail_window.title(f"จัดการข้อมูล: {display_name}")
        detail_window.geometry("700x500")
        detail_window.resizable(True, True)
        detail_window.transient(self)
        detail_window.grab_set()

        main_frame = ttk.Frame(detail_window, padding="10")
        main_frame.pack(fill='both', expand=True)

        lookup_data = self.ALL_DATA.get(key, [])

        # --- Treeview Setup ---
        columns = ('ID', 'Name', 'Detail')
        tree = ttk.Treeview(main_frame, columns=columns, show='headings', selectmode='browse')
        
        tree.heading('ID', text='ID'); tree.column('ID', width=50, stretch=tk.NO, anchor='center')
        tree.heading('Name', text='ชื่อไทย'); tree.column('Name', width=150, anchor='w')
        tree.heading('Detail', text='รายละเอียดมงคล (Auspiece Detail)'); tree.column('Detail', width=500, anchor='w')
        
        # Populate Data
        for item in lookup_data:
            name = item.get('name_th', item.get('english_name', '-'))
            # สำหรับเลขศาสตร์ ให้แสดงค่าตัวเลข
            if key == 'numerology':
                 name = f"เลข {item.get('number_value', '-')}: {name}"
            
            detail_snippet = item.get('auspice_detail_th', 'N/A')
            
            tree.insert('', 'end', 
                        values=(item['id'], name, detail_snippet[:100] + '...'), 
                        iid=item['id'])
            
        tree.pack(fill='both', expand=True, padx=5, pady=5)
        
        # --- Control Buttons ---
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill='x', pady=5)
        
        def open_edit_modal():
            selected_item_id = tree.focus()
            if not selected_item_id:
                messagebox.showwarning("เลือกรายการ", "กรุณาเลือกรายการที่ต้องการแก้ไขก่อน")
                return
            
            item_id = int(selected_item_id)
            selected_data = next((item for item in lookup_data if item['id'] == item_id), None)
            
            if selected_data:
                 detail_window.destroy() # ปิดตารางก่อนเปิด modal
                 LookupCrudModal(self, key, 'edit', selected_data)
        
        def open_add_modal():
            detail_window.destroy() # ปิดตารางก่อนเปิด modal
            LookupCrudModal(self, key, 'add', None)
        
        # Double Click Action (เพื่อเข้าสู่หน้าแก้ไขอย่างรวดเร็ว)
        tree.bind('<Double-1>', lambda event: open_edit_modal())
            
        ttk.Button(control_frame, 
                   text=f"➕ เพิ่ม {display_name} ใหม่", 
                   command=open_add_modal,
                   style='SearchButton.TButton').pack(side='left', padx=5)

        ttk.Button(control_frame, 
                   text=f"✏️ แก้ไขรายการที่เลือก", 
                   command=open_edit_modal,
                   style='SearchButton.TButton').pack(side='left', padx=5)

        ttk.Button(control_frame, text="ปิด", command=detail_window.destroy).pack(side='right', padx=5)


    def show_lookup_detail_popup(self, key: str):
        """
        แสดง Pop-up รายละเอียดเชิงประวัติศาสตร์และความมงคลแบบอ่านอย่างเดียว
        พร้อมปุ่ม "จัดการข้อมูล" (CRUD Admin)
        """
        detail_window = tk.Toplevel(self)
        lookup_name_map = {
            'chakra': 'จักระ', 
            'element': 'ธาตุ', 
            'numerology': 'เลขมงคล'
        }
        display_name = lookup_name_map.get(key, 'Lookup Item')
        
        detail_window.title(f"รายละเอียดมงคล: {display_name}")
        detail_window.geometry("850x700") # ขยายกรอบให้ใหญ่ขึ้น
        detail_window.resizable(True, True)
        detail_window.transient(self)
        detail_window.grab_set()

        main_frame = ttk.Frame(detail_window, padding="15")
        main_frame.pack(fill='both', expand=True)

        # ใช้ tk.Text สำหรับการจัดรูปแบบขั้นสูง
        text_widget = tk.Text(main_frame, wrap='word', font=('Tahoma', 11), padx=15, pady=15, relief="groove", borderwidth=2, bg="#F9F9F9")
        text_widget.pack(fill='both', expand=True, side='left')

        scrollbar = ttk.Scrollbar(main_frame, orient='vertical', command=text_widget.yview)
        scrollbar.pack(side='right', fill='y')
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        # 1. ตั้งค่า Tags สำหรับ Styling
        self._setup_text_tags(text_widget)
        
        lookup_data = self.ALL_DATA.get(key, [])
        raw_content = self._format_detail_view(key, lookup_data) # ดึงเนื้อหาที่มี Marker

        # 2. ใส่เนื้อหาและประยุกต์ใช้ Tags
        text_widget.insert('1.0', raw_content)
        self._apply_text_formatting(text_widget) # ไฮไลต์ตาม Marker ที่กำหนด
        
        text_widget.config(state='disabled')
        
        # --- Export Buttons & Control ---
        control_frame = ttk.Frame(detail_window, padding="0 10 0 10")
        control_frame.pack(fill='x')
        
        filename_base = f"{key}_details"
        
        # Export Buttons
        ttk.Button(control_frame, 
                   text="Export (.txt)", 
                   command=lambda: export_to_file(raw_content, filename_base, 'text'),
                   style='SearchButton.TButton').pack(side='left', padx=5)
        
        ttk.Button(control_frame, 
                   text="Export (.pdf)", 
                   command=lambda: export_to_file(raw_content, filename_base, 'pdf'),
                   style='SearchButton.TButton').pack(side='left', padx=5)

        # ปุ่ม Admin (เข้าสู่โหมด CRUD)
        ttk.Button(control_frame, 
                   text=f"⚙️ จัดการ/แก้ไข ข้อมูล {display_name}", 
                   command=lambda: [detail_window.destroy(), self.open_lookup_crud_modal(key)],
                   style='AddButton.TButton').pack(side='left', padx=15)
        
        ttk.Button(control_frame, text="ปิด", command=detail_window.destroy).pack(side='right', padx=15)


    def _setup_text_tags(self, text_widget: tk.Text):
        """กำหนด Style Tags สำหรับ Tkinter Text Widget"""
        
        # Header (ใหญ่สุด)
        text_widget.tag_configure('header', font=('Tahoma', 16, 'bold'), foreground='#2E86C1', justify='center')
        
        # SubHeader (ชื่อหัวข้อหลัก)
        text_widget.tag_configure('subheader', font=('Tahoma', 12, 'bold'), foreground='#8E44AD', spacing3=8)

        # Title (ชื่อรายการแต่ละตัว)
        text_widget.tag_configure('title', font=('Tahoma', 11, 'bold'), foreground='#D35400', spacing3=5)
        
        # Key Detail (ชื่อฟิลด์สำคัญ เช่น 'ประวัติ', 'มงคล')
        text_widget.tag_configure('key_detail', font=('Tahoma', 11, 'bold'), foreground='#28B463')
        
        # Bold (สำหรับเน้นข้อความใน Detail)
        text_widget.tag_configure('bold', font=('Tahoma', 11, 'bold'))


    def _apply_text_formatting(self, text_widget: tk.Text):
        """ใช้การค้นหาข้อความ (Marker) เพื่อประยุกต์ใช้ Tags"""
        
        text_content = text_widget.get("1.0", tk.END)
        
        # 1. Apply Header (บรรทัดแรก)
        text_widget.tag_add('header', "1.0", "1.end")

        # 2. Apply SubHeaders (### 1. ประวัติ... / ### 2. รายละเอียด...)
        start_index = "2.0" # เริ่มตั้งแต่บรรทัดที่ 2
        while True:
            # ค้นหาหัวข้อที่เริ่มต้นด้วย '###'
            idx = text_widget.search("###", start_index, stopindex=tk.END)
            if not idx: break
            
            line_end = text_widget.search('\n', idx, stopindex=tk.END)
            if not line_end: line_end = tk.END
            
            text_widget.tag_add('subheader', idx, f"{line_end}-1c")
            start_index = line_end # เริ่มค้นหาจากบรรทัดถัดไป

        # 3. Apply Titles (--- ชื่อรายการ ---)
        start_index = "1.0"
        while True:
            # ค้นหาหัวข้อที่เริ่มต้นด้วย '---'
            idx = text_widget.search("---", start_index, stopindex=tk.END)
            if not idx: break
            
            line_end = text_widget.search('\n', idx, stopindex=tk.END)
            if not line_end: line_end = tk.END
            
            # ตรวจสอบว่าบรรทัดนั้นมีคำว่า "---" อยู่
            if text_widget.get(idx, line_end).strip().startswith("---"):
                text_widget.tag_add('title', idx, f"{line_end}-1c")
            
            start_index = line_end # เริ่มค้นหาจากบรรทัดถัดไป
            
        # 4. Apply Key Details (เช่น **1. ประวัติ:**)
        start_index = "1.0"
        while True:
            # ค้นหาหัวข้อที่เริ่มต้นด้วย '**1. ประวัติ:**' หรือ '**2. รายละเอียด:**'
            idx = text_widget.search("**1. ประวัติ", start_index, stopindex=tk.END)
            if not idx: idx = text_widget.search("**2. รายละเอียด", start_index, stopindex=tk.END)
            if not idx: break

            line_end = text_widget.search('\n', idx, stopindex=tk.END)
            if not line_end: line_end = tk.END
            
            # เน้นแค่ส่วนหัวข้อ
            text_widget.tag_add('key_detail', idx, f"{line_end}-1c")
            start_index = line_end

    def _get_next_element_name(self, current_name: str) -> str:
        """Helper function สำหรับแสดงวัฏจักรส่งเสริม (ใช้ชื่อธาตุในการคำนวณ)"""
        
        # ลำดับการส่งเสริม (相生 - Shēng) ตามหลักปรัชญาจีน: ไม้ -> ไฟ -> ดิน -> ทอง/โลหะ -> น้ำ -> ไม้
        relationship = {
            "ไม้": "ไฟ",
            "ไฟ": "ดิน", 
            "ดิน": "ทอง/โลหะ",
            "ทอง/โลหะ": "น้ำ",
            "น้ำ": "ไม้"
        }
        
        # ค้นหาธาตุที่ถูกสร้างโดยธาตุปัจจุบัน
        return relationship.get(current_name, 'N/A')

    
    def _format_detail_view(self, key: str, lookup_data: List[Dict[str, Any]]) -> str:
        """
        Helper function สำหรับจัดรูปแบบข้อมูลทั้งหมด (ประวัติ + รายละเอียดมงคล) 
        ตามโครงสร้างเฉพาะของแต่ละ Lookup (จักระ, ธาตุ, เลขมงคล)
        """
        detail = ""
        
        # --- 1. Header ---
        header_map = {'chakra': '🧘‍♂️ 7 จักระ (Chakra)', 'element': '🌟 5 ธาตุ (Wǔxíng)', 'numerology': '🔢 เลขศาสตร์ (Numerology)'}
        display_name = header_map.get(key, 'รายละเอียด')
        detail += f"### {display_name}\n\n"
        
        if not lookup_data:
             return detail + "❌ ไม่พบข้อมูลในไฟล์ JSON"

        # --- 2. จัดรูปแบบเฉพาะสำหรับแต่ละ Key ---
        
        if key == 'numerology':
            detail += "### 1. ประวัติและความเป็นมา\n"
            detail += "เลขศาสตร์มีรากฐานจากหลายอารยธรรม (เช่น พีทาโกรัส) เชื่อว่าตัวเลขแต่ละตัวมี 'ความสั่นสะเทือนทางพลังงาน' ที่ส่งผลต่อชะตาชีวิตและบุคลิกภาพของมนุษย์\n\n"
            detail += "### 2. รายละเอียดมงคลเลข 1-9\n"
            detail += "----------------------------------------------\n"
            
            sorted_data = sorted([d for d in lookup_data if d.get('number_value') in range(1, 10)], key=lambda x: x.get('number_value', 0))
            
            for item in sorted_data:
                number = item.get('number_value')
                auspice_detail = item.get('auspice_detail_th', 'N/A')
                
                detail += f"--- [{number}] เลข {number} ---\n"
                detail += f" - มงคล: {auspice_detail}\n\n"
        
        else: # สำหรับ Chakra และ Element (ที่มีรายละเอียดประวัติแยกรายตัว)
            
            # กรองและจัดเรียงข้อมูล
            sorted_data = sorted(lookup_data, key=lambda x: x.get('id', 0))

            for item in sorted_data:
                id = item.get('id')
                name_th = item.get('name_th', '-')
                
                history_th = item.get('history_th', 'N/A')
                auspice_detail = item.get('auspice_detail_th', 'N/A')
                
                # --- หัวข้อหลัก ---
                detail += f"----------------------------------------------\n"
                detail += f"--- {name_th.upper()} (ID: {id}) ---\n"
                
                # --- ประวัติ (เฉพาะแต่ละรายการ) ---
                detail += "**1. ประวัติและความเป็นมา:**\n"
                detail += f"{history_th}\n\n"
                
                # --- รายละเอียดมงคล ---
                detail += "**2. รายละเอียดเชิงมงคล:**\n"
                detail += f" - ความเชื่อหลัก: {auspice_detail}\n"
                
                if key == 'chakra':
                    # แสดงรายละเอียดเฉพาะจักระ
                    detail += f" - ตำแหน่ง: {item.get('location', '-')}\n"
                    detail += f" - ธาตุ: {item.get('name_th', '-').split('ธาตุ: ')[-1].strip() if 'ธาตุ:' in item.get('name_th', '') else item.get('name_th', '-')}\n"
                    detail += f" - สัญลักษณ์/โลโก้: {item.get('logo', '-')}\n"
                    
                if key == 'element':
                    # แสดงรายละเอียดเฉพาะธาตุ
                    detail += f" - คำจำกัดความ: {item.get('description', '-')}\n" 
                    detail += f" - วัฏจักรส่งเสริม: {name_th} สร้าง {self._get_next_element_name(name_th)}\n"
                    
                detail += "\n"
            
        return detail

# =======================================================
# 7. MAIN EXECUTION
# =======================================================

if __name__ == "__main__":
    all_data = load_all_data()
    if all_data:
        app = PyStoneApp(all_data)
        app.mainloop()