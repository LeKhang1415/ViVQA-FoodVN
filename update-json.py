import json
import re
import unicodedata
from pathlib import Path

# Cấu hình đường dẫn
DATA_DIR = Path(r"C:\Users\Admin\Desktop\ViVQA-Food\data")
INPUT_JSON = DATA_DIR / "vietnamese_food_vqa_knowledge.json"
OUTPUT_JSON = DATA_DIR / "vietnamese_food_vqa_knowledge_updated.json"

def remove_vietnamese_accents(text):
    if not text:
        return ""
    text = unicodedata.normalize('NFD', text)
    text = "".join(c for c in text if unicodedata.category(c) != 'Mn')
    text = text.replace('đ', 'd').replace('Đ', 'D')
    return text

def generate_folder_name(ten_mon):
    # Sử dụng đúng logic đã dùng để tạo thư mục
    # 1. Loại bỏ nội dung trong ngoặc đơn
    clean_name = re.sub(r'\(.*?\)', '', ten_mon).strip()
    # 2. Xóa dấu
    clean_name = remove_vietnamese_accents(clean_name)
    # 3. Chữ thường
    clean_name = clean_name.lower()
    # 4. Loại bỏ ký tự đặc biệt
    clean_name = re.sub(r'[^a-z0-9\s]', '', clean_name)
    # 5. Thay khoảng trắng bằng gạch dưới
    clean_name = re.sub(r'\s+', '_', clean_name).strip('_')
    return clean_name

def update_json_with_folder_names():
    if not INPUT_JSON.exists():
        print(f"Lỗi: Không tìm thấy file tại {INPUT_JSON}")
        return

    # 1. Đọc dữ liệu JSON hiện tại
    with open(INPUT_JSON, 'r', encoding='utf-8') as f:
        food_list = json.load(f)

    # 2. Duyệt qua từng món ăn để thêm trường image_folder
    for item in food_list:
        ten_mon = item.get("ten_mon")
        if ten_mon:
            folder_name = generate_folder_name(ten_mon)
            # Thêm trường mới vào object
            item["image_folder"] = folder_name

    # 3. Ghi lại dữ liệu đã cập nhật vào file mới
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(food_list, f, ensure_ascii=False, indent=4)

    print(f"Hoàn tất! Đã tạo file mới với trường 'image_folder' tại: {OUTPUT_JSON}")

if __name__ == "__main__":
    update_json_with_folder_names()