import os
import json
import csv
import time
import base64
from pathlib import Path
from tqdm import tqdm

# Import thư viện Groq
from groq import Groq

# ==========================================
# 1. CẤU HÌNH ĐƯỜNG DẪN & API
# ==========================================
# 🚨 Điền API KEY của GROQ vào đây:
API_KEY = ''

PROJECT_ROOT = Path(r"C:\Users\Admin\Desktop\ViVQA-Food")
DATA_DIR = PROJECT_ROOT / "data"

INPUT_JSON = DATA_DIR / "vivqa_food_dataset_final.json"
OUTPUT_CSV = DATA_DIR / "foodvqa_img_description.csv"

# Khởi tạo Client Groq
client = Groq(api_key=API_KEY)

# Sử dụng model Vision miễn phí tốt nhất của Groq hiện tại
MODEL_ID = "meta-llama/llama-4-scout-17b-16e-instruct"

# ==========================================
# 2. HÀM TẠO PROMPT VÀ XỬ LÝ ẢNH
# ==========================================
def create_prompt(food_name='', additional_info=''):
    prompt = (
        f"Bức ảnh này chụp món ăn: {food_name}.\n"
        f"Thông tin tham khảo thêm về món ăn: {additional_info}\n\n"
        "NHIỆM VỤ:\n"
        "Hãy quan sát ảnh và mô tả thật chi tiết màu sắc, hình dáng, cũng như vị trí tương đối của các thành phần món ăn có xuất hiện trong ảnh.\n\n"
        "RÀNG BUỘC NGHIÊM NGẶT:\n"
        "- Chỉ in ra ĐÚNG kết quả mô tả cuối cùng, tuyệt đối không in ra tiêu đề, lời chào hay phần giải thích thêm.\n"
        "- Phải viết bằng Tiếng Việt.\n"
        "- Trình bày cực kỳ ngắn gọn, tối đa 25 từ.\n"
        "- Không được xuống dòng (viết thành 1 đoạn văn duy nhất)!\n"
    )
    return prompt

def encode_image(image_path):
    """Mã hóa ảnh sang định dạng Base64 để gửi cho Groq"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

# ==========================================
# 3. LUỒNG CHẠY CHÍNH
# ==========================================
def main():
    if not INPUT_JSON.exists():
        print(f"Lỗi: Không tìm thấy file dữ liệu {INPUT_JSON}")
        return

    # Đọc dữ liệu JSON
    with open(INPUT_JSON, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Đọc các ảnh đã được xử lý (để Resume nếu code bị ngắt giữa chừng)
    processed_images = set()
    if OUTPUT_CSV.exists():
        with open(OUTPUT_CSV, 'r', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            next(reader, None)  # Bỏ qua dòng tiêu đề
            for row in reader:
                if row:
                    processed_images.add(row[0])
    else:
        # Nếu chưa có file CSV, tạo mới và ghi dòng Header
        with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Image_Path', 'Food_Name', 'Image_Description'])

    print(f"Đã xử lý trước đó: {len(processed_images)} ảnh.")
    print(f"Bắt đầu tạo mô tả bằng Groq ({MODEL_ID})...")

    for item in tqdm(data, desc="Captioning Images"):
        image_path_str = item.get("image_path")
        food_name = item.get("ten_mon", "")
        summary = item.get("mo_ta", "")

        if not image_path_str or image_path_str in processed_images:
            continue

        full_img_path = DATA_DIR / image_path_str

        if not full_img_path.exists():
            print(f"\n[!] Bỏ qua - Không tìm thấy file ảnh thực tế tại: {full_img_path}")
            continue

        # 1. Mã hóa ảnh và lấy mime_type
        try:
            base64_image = encode_image(full_img_path)
            
            ext = full_img_path.suffix.lower()
            mime_type = 'image/jpeg'
            if ext == '.png':
                mime_type = 'image/png'
            elif ext == '.webp':
                mime_type = 'image/webp'
        except Exception as file_e:
            print(f"\n[!] Lỗi đọc file ảnh {full_img_path}: {file_e}")
            continue

        prompt_text = create_prompt(food_name=food_name, additional_info=summary)

        # ==========================================
        # CƠ CHẾ RETRY (XỬ LÝ LỖI 503 / 429)
        # ==========================================
        max_retries = 5
        success = False

        for attempt in range(max_retries):
            try:
                # 2. Gọi API Groq với cấu trúc Vision (Text + Image URL dạng Base64)
                response = client.chat.completions.create(
                    model=MODEL_ID,
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": prompt_text
                                },
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:{mime_type};base64,{base64_image}"
                                    }
                                }
                            ]
                        }
                    ],
                    temperature=0.4, # Giữ ở mức thấp để mô tả bám sát ảnh thực tế
                    max_tokens=100
                )

                # 3. Lưu kết quả
                description = response.choices[0].message.content.strip()
                description = description.replace('\n', ' ').replace('\r', '')

                with open(OUTPUT_CSV, 'a', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow([image_path_str, food_name, description])

                processed_images.add(image_path_str)
                success = True
                
                # Nghỉ 2.5 giây để khớp với Rate Limit 30 RPM của Groq (60s / 30 = 2s)
                time.sleep(2.5)
                break 

            except Exception as e:
                error_msg = str(e).lower()
                
                # Bắt các lỗi quen thuộc: Rate limit (429) hoặc Server lag (503)
                if "503" in error_msg or "unavailable" in error_msg or "429" in error_msg or "rate limit" in error_msg:
                    wait_time = 5 * (attempt + 1)
                    print(f"\n[!] Server bận. Đang thử lại lần {attempt + 1}/{max_retries} cho ảnh {image_path_str} sau {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    print(f"\n[!] Lỗi không thể khắc phục ở ảnh {image_path_str}: {e}")
                    break
        
        if not success:
            print(f"\n[-] Đã thử {max_retries} lần nhưng vẫn thất bại. Bỏ qua ảnh {image_path_str}.")

    print("\n--- HOÀN TẤT BƯỚC 3 ---")
    print(f"Toàn bộ mô tả ảnh đã được lưu an toàn tại: {OUTPUT_CSV}")

if __name__ == "__main__":
    main()