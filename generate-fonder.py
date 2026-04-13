import os
import json
import re
import unicodedata
from pathlib import Path

# Cấu hình đường dẫn
DATA_DIR = Path(r"C:\Users\Admin\Desktop\ViVQA-Food\data")
INPUT_JSON = DATA_DIR / "vietnamese_food_vqa_knowledge.json" 
OUTPUT_DIR = DATA_DIR / "images" 

def remove_vietnamese_accents(text):
    """
    Hàm xóa dấu tiếng Việt và chuyển về ký tự thường
    """
    if not text:
        return ""
    # Chuẩn hóa về dạng Unicode tổ hợp
    text = unicodedata.normalize('NFD', text)
    # Loại bỏ các ký tự dấu
    text = "".join(c for c in text if unicodedata.category(c) != 'Mn')
    # Thay chữ đ/Đ
    text = text.replace('đ', 'd').replace('Đ', 'D')
    return text

def create_food_folders():
    if not INPUT_JSON.exists():
        print(f"Lỗi: Không tìm thấy file tại {INPUT_JSON}")
        return

    with open(INPUT_JSON, 'r', encoding='utf-8') as f:
        try:
            food_list = json.load(f)
        except json.JSONDecodeError:
            print("Lỗi: File JSON không đúng định dạng.")
            return

    if not OUTPUT_DIR.exists():
        os.makedirs(OUTPUT_DIR)
        print(f"Đã tạo thư mục gốc: {OUTPUT_DIR}")

    count_success = 0
    count_exist = 0

    for item in food_list:
        ten_mon = item.get("ten_mon")
        
        if ten_mon:
            # 1. Xử lý tên thư mục (không dấu, gạch ngang)
            clean_name = remove_vietnamese_accents(ten_mon)
            clean_name = clean_name.lower()
            clean_name = re.sub(r'[^a-z0-9\s]', '', clean_name)
            clean_name = re.sub(r'\s+', '-', clean_name).strip('-')
            
            folder_path = OUTPUT_DIR / clean_name
            
            try:
                # Tạo thư mục nếu chưa tồn tại
                if not folder_path.exists():
                    os.makedirs(folder_path)
                    print(f"--- Đã tạo thư mục: {clean_name}")
                    count_success += 1
                else:
                    print(f"--- Thư mục đã tồn tại: {clean_name}")
                    count_exist += 1
                
                # 2. Tạo file text lưu tên tiếng Việt bên trong thư mục
                # Tên file có thể đặt là 'original_name.txt' hoặc 'name.txt'
                file_info_path = folder_path / "vietnamese_name.txt"
                with open(file_info_path, 'w', encoding='utf-8') as f_info:
                    f_info.write(ten_mon)
                
            except Exception as e:
                print(f"!!! Lỗi khi xử lý {clean_name}: {e}")

    print("-" * 30)
    print(f"Hoàn tất! Tạo/Cập nhật: {count_success + count_exist} thư mục.")
    print(f"Mỗi thư mục đã có file 'vietnamese_name.txt' chứa tên gốc.")

if __name__ == "__main__":
    create_food_folders()