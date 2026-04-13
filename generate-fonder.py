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
    if not text:
        return ""
    text = unicodedata.normalize('NFD', text)
    text = "".join(c for c in text if unicodedata.category(c) != 'Mn')
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
            # --- PHẦN XỬ LÝ MỚI TẠI ĐÂY ---
            
            # 1. Loại bỏ nội dung trong ngoặc đơn (bao gồm cả cặp ngoặc)
            # Ví dụ: "Bánh trung thu (Bánh nướng & Bánh dẻo)" -> "Bánh trung thu "
            clean_name = re.sub(r'\(.*?\)', '', ten_mon).strip()
            
            # 2. Xóa dấu tiếng Việt
            clean_name = remove_vietnamese_accents(clean_name)
            
            # 3. Chuyển về chữ thường
            clean_name = clean_name.lower()
            
            # 4. Loại bỏ các ký tự đặc biệt, chỉ giữ lại chữ cái và số
            clean_name = re.sub(r'[^a-z0-9\s]', '', clean_name)
            
            # 5. Thay thế khoảng trắng bằng dấu gạch dưới (_) thay vì gạch ngang (-)
            # Ví dụ: "banh trung thu" -> "banh_trung_thu"
            clean_name = re.sub(r'\s+', '_', clean_name).strip('_')
            
            # ------------------------------

            folder_path = OUTPUT_DIR / clean_name
            
            try:
                if not folder_path.exists():
                    os.makedirs(folder_path)
                    print(f"--- Đã tạo thư mục: {clean_name}")
                    count_success += 1
                else:
                    print(f"--- Thư mục đã tồn tại: {clean_name}")
                    count_exist += 1
                
                # Lưu tên gốc vào file txt bên trong để đối chiếu sau này
                file_info_path = folder_path / "vietnamese_name.txt"
                with open(file_info_path, 'w', encoding='utf-8') as f_info:
                    f_info.write(ten_mon)
                
            except Exception as e:
                print(f"!!! Lỗi khi xử lý {clean_name}: {e}")

    print("-" * 30)
    print(f"Hoàn tất! Tạo/Cập nhật: {count_success + count_exist} thư mục.")

if __name__ == "__main__":
    create_food_folders()