import json
from pathlib import Path

# ==========================================
# CẤU HÌNH ĐƯỜNG DẪN
# ==========================================
DATA_DIR = Path(r"C:\Users\Admin\Desktop\ViVQA-Food\data")
INPUT_FILE = DATA_DIR / "food_knowledge_ready.json"
OUTPUT_FILE = DATA_DIR / "vivqa_food_dataset_final.json"

# Cấu hình đường dẫn tới thư mục chứa ảnh
# Lưu ý: Nếu thư mục 'images' nằm trong thư mục 'data', hãy dùng: IMAGE_DIR = DATA_DIR / "images"
# Nếu thư mục 'images' nằm ngang hàng với 'data', hãy dùng đường dẫn bên dưới:
IMAGE_DIR = Path(r"C:\Users\Admin\Desktop\ViVQA-Food\data\images") 


def main():
    # Kiểm tra xem file JSON đầu vào có tồn tại không
    if not INPUT_FILE.exists():
        print(f"Lỗi: Không tìm thấy file gốc tại {INPUT_FILE}")
        return

    # Đọc dữ liệu JSON
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    new_data = []

    print(f"Đang xử lý dữ liệu từ {INPUT_FILE}...")

    for item in data:
        # Lấy tên thư mục ảnh từ JSON
        folder_name = item.get("image_folder")
        if not folder_name:
            continue
            
        folder_path = IMAGE_DIR / folder_name

        # Kiểm tra xem thư mục ảnh có tồn tại không
        if folder_path.exists():
            # Lấy danh sách tất cả các ảnh hợp lệ trong thư mục
            for img_file in folder_path.iterdir():
                if img_file.is_file() and img_file.suffix.lower() in ['.jpg', '.png', '.jpeg', '.webp']:
                    # Tạo một bản sao của item và thêm đường dẫn ảnh
                    new_item = item.copy()
                    
                    # Lưu đường dẫn ảnh vào dict (ép kiểu về string)
                    # Chỉ lấy chữ "images/" + "tên_thư_mục" + "tên_file_ảnh"
                    new_item["image_path"] = f"images/{folder_name}/{img_file.name}"
                    new_data.append(new_item)
        else:
            print(f"[!] Bỏ qua - Không tìm thấy thư mục ảnh: {folder_path}")

    # Tạo thư mục đầu ra nếu chưa có (phòng trường hợp thư mục data bị xóa mất)
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    # Lưu dữ liệu mới ra file JSON
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(new_data, f, ensure_ascii=False, indent=4)

    print(f"\n--- HOÀN TẤT ---")
    print(f"Đã tạo ra {len(new_data)} mẫu dữ liệu.")
    print(f"File mới được lưu thành công tại: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()