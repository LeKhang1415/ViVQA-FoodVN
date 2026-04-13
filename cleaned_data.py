import json
from pathlib import Path

# Đường dẫn file của bạn
DATA_DIR = Path(r"C:\Users\Admin\Desktop\ViVQA-Food\data")
INPUT_JSON = DATA_DIR / "vietnamese_food_vqa_knowledge.json" 
OUTPUT_JSON = DATA_DIR / "cleaned_knowledge.json"

def clean_json_data():
    # 1. Đọc dữ liệu từ file JSON
    with open(INPUT_JSON, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 2. Danh sách các trường (keys) bạn muốn xóa
    keys_to_remove = ["cau_hoi_vqa", "phuong_phap_che_bien", "dac_diem_thi_giac"]

    count = 0
    # 3. Lặp qua từng món ăn và xóa các trường
    for item in data:
        for key in keys_to_remove:
            # Dùng pop(key, None) để xóa. 
            # Tham số None giúp code không bị lỗi (crash) nếu lỡ có món nào đó không có trường này.
            if key in item:
                item.pop(key, None)
        count += 1

    # 4. Ghi lại dữ liệu đã dọn dẹp ra file mới
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    print(f"Hoàn tất! Đã dọn dẹp {count} món ăn và lưu vào {OUTPUT_JSON}")

if __name__ == "__main__":
    clean_json_data()