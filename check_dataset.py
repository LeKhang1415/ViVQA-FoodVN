import json
import os
from pathlib import Path

# Cấu hình đường dẫn
DATA_DIR = Path(r"C:\Users\Admin\Desktop\ViVQA-Food\data")
JSON_FILE = DATA_DIR / "vietnamese_food_vqa_knowledge_updated.json"
IMAGE_ROOT = DATA_DIR / "images"
MISSING_ROOT = DATA_DIR / "images_missing"
CRAWL_LIST_FILE = DATA_DIR / "missing_list.txt"
READY_FOR_VQA_FILE = DATA_DIR / "food_knowledge_ready.json"

def is_valid_image_folder(folder_path):
    """Kiểm tra xem thư mục có chứa ít nhất 1 file ảnh hợp lệ hay không."""
    if not folder_path.exists() or not folder_path.is_dir():
        return False
    
    # Danh sách các đuôi file ảnh phổ biến
    extensions = ("*.jpg", "*.jpeg", "*.png", "*.webp", "*.JPG", "*.PNG")
    
    for ext in extensions:
        for img_file in folder_path.glob(ext):
            # Kiểm tra file có thực sự tồn tại và có dung lượng > 0
            if img_file.is_file() and img_file.stat().st_size > 0:
                return True
    return False

def verify_and_prepare_crawl():
    if not JSON_FILE.exists():
        print(f"Lỗi: Không tìm thấy file JSON tại {JSON_FILE}")
        return

    # Luôn đảm bảo folder missing tồn tại để crawl về sau
    if not MISSING_ROOT.exists():
        os.makedirs(MISSING_ROOT)

    with open(JSON_FILE, 'r', encoding='utf-8') as f:
        food_list = json.load(f)

    total_dishes = len(food_list)
    missing_names = [] 
    ready_food_items = []
    success_count = 0

    for item in food_list:
        ten_mon = item.get("ten_mon", "Không rõ tên")
        folder_name = item.get("image_folder")
        if not folder_name:
            continue

        # CHỈ KIỂM TRA TRONG THƯ MỤC IMAGES GỐC
        original_path = IMAGE_ROOT / folder_name
        
        # Nếu tìm thấy ảnh hợp lệ trong folder chính
        if is_valid_image_folder(original_path):
            success_count += 1
            ready_food_items.append(item)
        else:
            # Nếu không có (hoặc folder rỗng), đưa vào danh sách cần crawl
            missing_names.append(ten_mon)
            
            # Tạo sẵn folder trong missing_root để tool crawl tải về đúng chỗ
            missing_path = MISSING_ROOT / folder_name
            if not missing_path.exists():
                os.makedirs(missing_path)

    # 1. Xuất danh sách món thiếu ra file .txt
    with open(CRAWL_LIST_FILE, 'w', encoding='utf-8') as f:
        for name in missing_names:
            f.write(f"{name}\n")

    # 2. Xuất JSON chỉ chứa món ĐÃ CÓ ẢNH trong folder 'images'
    with open(READY_FOR_VQA_FILE, 'w', encoding='utf-8') as f:
        json.dump(ready_food_items, f, ensure_ascii=False, indent=4)

    # Báo cáo
    print("=" * 60)
    print(f"{'KIỂM TRA ẢNH TRONG THƯ MỤC GỐC':^60}")
    print("=" * 60)
    print(f"- Tổng số món:             {total_dishes:>3}")
    print(f"- Đã có ảnh tại 'images':  {success_count:>3}")
    print(f"- Chưa có ảnh:             {len(missing_names):>3}")
    print("-" * 60)
    print(f"File JSON sẵn sàng: {READY_FOR_VQA_FILE.name}")
    print("=" * 60)

if __name__ == "__main__":
    verify_and_prepare_crawl()