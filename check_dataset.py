import json
import os
from pathlib import Path

# Cấu hình đường dẫn
DATA_DIR = Path(r"C:\Users\Admin\Desktop\ViVQA-Food\data")
JSON_FILE = DATA_DIR / "vietnamese_food_vqa_knowledge_updated.json"
IMAGE_ROOT = DATA_DIR / "images"
MISSING_ROOT = DATA_DIR / "images_missing"
# File lưu danh sách để crawl
CRAWL_LIST_FILE = DATA_DIR / "missing_list.txt"

def verify_and_prepare_crawl():
    if not JSON_FILE.exists():
        print(f"Lỗi: Không tìm thấy file JSON tại {JSON_FILE}")
        return

    if not MISSING_ROOT.exists():
        os.makedirs(MISSING_ROOT)

    with open(JSON_FILE, 'r', encoding='utf-8') as f:
        food_list = json.load(f)

    total_dishes = len(food_list)
    missing_names = [] # Lưu tên tiếng Việt để crawl
    success_count = 0

    for item in food_list:
        ten_mon = item.get("ten_mon", "Không rõ tên")
        folder_name = item.get("image_folder")
        if not folder_name: continue

        original_path = IMAGE_ROOT / folder_name
        missing_path = MISSING_ROOT / folder_name

        # Kiểm tra xem món này đã có ảnh ở đâu chưa
        has_images = False
        for path in [original_path, missing_path]:
            if path.exists() and any(path.glob("*.[jp][pn]*g")):
                has_images = True
                break
        
        if has_images:
            success_count += 1
        else:
            # Nếu chưa có ảnh, tạo folder trong missing (nếu chưa có)
            if not missing_path.exists():
                os.makedirs(missing_path)
            # Thêm tên vào danh sách cần crawl
            missing_names.append(ten_mon)

    # Xuất danh sách ra file .txt
    with open(CRAWL_LIST_FILE, 'w', encoding='utf-8') as f:
        for name in missing_names:
            f.write(f"{name}\n")

    # Báo cáo
    print("=" * 60)
    print(f"{'HOÀN TẤT CHUẨN BỊ DỮ LIỆU CRAWL':^60}")
    print("=" * 60)
    print(f"- Tổng số món:             {total_dishes:>3}")
    print(f"- Đã có ảnh:               {success_count:>3}")
    print(f"- Cần crawl thêm:          {len(missing_names):>3}")
    print(f"- File danh sách đã tạo:   {CRAWL_LIST_FILE.name}")
    print("-" * 60)
    print(f"LƯU Ý: Hãy dùng file '{CRAWL_LIST_FILE.name}' để nạp vào tool crawl.")
    print("=" * 60)

if __name__ == "__main__":
    verify_and_prepare_crawl()