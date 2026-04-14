import json
from pathlib import Path

# Cấu hình đường dẫn
DATA_DIR = Path(r"C:\Users\Admin\Desktop\ViVQA-Food\data")
JSON_FILE = DATA_DIR / "vietnamese_food_vqa_knowledge_updated.json"
IMAGE_ROOT = DATA_DIR / "images"

def verify_food_images():
    if not JSON_FILE.exists():
        print(f"Lỗi: Không tìm thấy file JSON tại {JSON_FILE}")
        return

    with open(JSON_FILE, 'r', encoding='utf-8') as f:
        food_list = json.load(f)

    total_dishes = len(food_list)
    print(f"--- Đang kiểm tra {total_dishes} món ăn ---\n")

    missing_folders = []
    empty_folders = []
    success_count = 0

    for item in food_list:
        ten_mon = item.get("ten_mon", "Không rõ tên")
        folder_name = item.get("image_folder")

        if not folder_name:
            print(f"[!] Món '{ten_mon}' thiếu thông tin image_folder trong JSON.")
            continue

        folder_path = IMAGE_ROOT / folder_name

        # 1. Kiểm tra thư mục có tồn tại không
        if not folder_path.exists():
            missing_folders.append(f"{ten_mon} (Thư mục thiếu: {folder_name})")
        else:
            # 2. Nếu tồn tại, kiểm tra xem có ảnh không
            images = list(folder_path.glob("*.[jp][pn]*g"))
            if len(images) == 0:
                empty_folders.append(f"{ten_mon} (Thư mục: {folder_name})")
            else:
                success_count += 1

    # Tính toán thống kê
    num_missing = len(missing_folders)
    num_empty = len(empty_folders)
    total_incomplete = num_missing + num_empty
    completion_rate = (success_count / total_dishes) * 100 if total_dishes > 0 else 0

    # Xuất báo cáo kết quả chi tiết
    print("=" * 60)
    print(f"{'BÁO CÁO TÌNH TRẠNG DỮ LIỆU':^60}")
    print("=" * 60)
    print(f"- Tổng số món cần có:      {total_dishes:>3}")
    print(f"- Đã hoàn thành (có ảnh):  {success_count:>3}")
    print(f"- Tổng số món còn thiếu:   {total_incomplete:>3} (CHIẾM {(total_incomplete/total_dishes)*100:.1f}%)")
    print("-" * 60)
    print(f"  + Thiếu thư mục hoàn toàn: {num_missing:>3}")
    print(f"  + Thư mục trống (0 ảnh):   {num_empty:>3}")
    print("-" * 60)
    print(f"Tỷ lệ hoàn thành bộ dữ liệu: {completion_rate:.2f}%")
    print("=" * 60)

    if missing_folders:
        print(f"\n[DANH SÁCH {num_missing} MÓN THIẾU THƯ MỤC]:")
        for i, msg in enumerate(missing_folders, 1):
            print(f"  {i}. {msg}")

    if empty_folders:
        print(f"\n[DANH SÁCH {num_empty} THƯ MỤC CHƯA CÓ ẢNH]:")
        for i, msg in enumerate(empty_folders, 1):
            print(f"  {i}. {msg}")

    if total_incomplete == 0:
        print("\n🎉 Tuyệt vời! Tất cả các món đều đã có thư mục và ảnh.")

if __name__ == "__main__":
    verify_food_images()