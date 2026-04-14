import os
import re
import unicodedata
import time
import random
from pathlib import Path
from icrawler.builtin import BingImageCrawler  # Chuyển sang dùng Bing

# ==========================================
# CẤU HÌNH ĐƯỜNG DẪN
# ==========================================
DATA_DIR = Path(r"C:\Users\Admin\Desktop\ViVQA-Food\data")
MISSING_ROOT = DATA_DIR / "images_missing"
CRAWL_LIST_FILE = DATA_DIR / "missing_list.txt"

def remove_vietnamese_accents(text):
    if not text: return ""
    text = unicodedata.normalize('NFD', text)
    text = "".join(c for c in text if unicodedata.category(c) != 'Mn')
    text = text.replace('đ', 'd').replace('Đ', 'D')
    return text

def get_folder_name(ten_mon):
    """Tạo tên folder chuẩn khớp với cấu hình dự án"""
    clean_name = re.sub(r'\(.*?\)', '', ten_mon).strip()
    clean_name = remove_vietnamese_accents(clean_name).lower()
    clean_name = re.sub(r'[^a-z0-9\s]', '', clean_name)
    return re.sub(r'\s+', '_', clean_name).strip('_')

def start_crawling(max_images_per_dish=40):
    # 1. Kiểm tra file danh sách
    if not CRAWL_LIST_FILE.exists():
        print(f"Lỗi: Không tìm thấy file '{CRAWL_LIST_FILE.name}'.")
        return

    # 2. Đọc danh sách các món cần cào
    with open(CRAWL_LIST_FILE, "r", encoding="utf-8") as f:
        food_list = [line.strip() for line in f if line.strip()]

    if not food_list:
        print("🎉 Chúc mừng! Danh sách cào ảnh hiện đang trống.")
        return

    print(f"--- Bắt đầu cào ảnh (Sử dụng Bing) cho {len(food_list)} món ăn ---")
    
    # 3. Vòng lặp cào ảnh
    for i, food_name in enumerate(food_list, 1):
        folder_name = get_folder_name(food_name)
        save_path = MISSING_ROOT / folder_name
        os.makedirs(save_path, exist_ok=True)

        print(f"[{i}/{len(food_list)}] Đang cào: {food_name}")
        
        try:
            # Sử dụng BingImageCrawler để tránh lỗi chặn từ Google
            bing_crawler = BingImageCrawler(
                storage={'root_dir': str(save_path)},
                log_level=50 
            )
            
            # Thực hiện cào ảnh
            bing_crawler.crawl(
                keyword=f"món {food_name} việt nam", 
                max_num=max_images_per_dish,
                min_size=(200, 200),
                overwrite=False 
            )
            
            # NGHỈ NGẪU NHIÊN: Rất quan trọng để tránh bị phát hiện là bot
            # Nghỉ từ 2 đến 5 giây sau mỗi món ăn
            delay = random.uniform(2, 5)
            time.sleep(delay)
            
            print(f"   => Xong món {i}. Nghỉ {delay:.1f}s...")

        except Exception as e:
            print(f"   !!! Lỗi tại món {food_name}: {e}")
            # Nếu gặp lỗi thread, nghỉ lâu hơn một chút trước khi sang món tiếp theo
            time.sleep(10)

    print("\n" + "="*50)
    print("HOÀN TẤT!")
    print("="*50)

if __name__ == "__main__":
    start_crawling()