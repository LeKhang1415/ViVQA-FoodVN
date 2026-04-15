import os
import csv
import json
import time
from pathlib import Path
from tqdm import tqdm
from groq import Groq

# ==========================================
# 1. CẤU HÌNH ĐƯỜNG DẪN & API
# ==========================================
# 🚨 Điền API KEY của GROQ vào đây:
API_KEY = '' 
client = Groq(api_key=API_KEY)

PROJECT_ROOT = Path(r"C:\Users\Admin\Desktop\ViVQA-Food")
DATA_DIR = PROJECT_ROOT / "data"

INPUT_CSV = DATA_DIR / "foodvqa_img_description.csv"
OUTPUT_JSON = DATA_DIR / "foodvqa_visual_dataset.json"

# Mô hình xử lý văn bản cực nhanh của Groq
MODEL_ID = "llama-3.1-8b-instant"

# ==========================================
# 2. HÀM SINH CÂU HỎI TỪ MÔ TẢ
# ==========================================
def generate_visual_qa(image_path, food_name, description, max_retries=5):
    prompt = f"""
    Bạn là chuyên gia tạo dữ liệu VQA.
    Dưới đây là mô tả chi tiết của bức ảnh chụp món '{food_name}':
    "{description}"

    NHIỆM VỤ:
    Tạo ra các cặp câu hỏi và câu trả lời tập trung 100% vào các chi tiết thị giác trong mô tả. 
    Tuyệt đối KHÔNG hỏi về nguyên liệu, cách nấu, xuất xứ hay lượng calo.

    YÊU CẦU KIỂM TRA CHÉO (CROSS-CHECK):
    Hãy đọc kỹ mô tả và xét 3 yếu tố sau. NẾU VÀ CHỈ NẾU mô tả có nhắc đến yếu tố đó thì mới được phép tạo câu hỏi.
    1. Màu sắc/Trạng thái: (Ví dụ: xanh, đỏ, chín, sống...)
    2. Số lượng/Hình dáng: (Ví dụ: hai, ba, tròn, dẹt...)
    3. Vị trí/Hành động: (Ví dụ: bên trái, ở giữa, gắp, rót...)

    RÀNG BUỘC KỸ THUẬT NGHIÊM NGẶT:
    - Nếu mô tả KHÔNG CHỨA thông tin về một nhóm nào đó, tuyệt đối KHÔNG ĐƯỢC tạo câu hỏi cho nhóm đó (bỏ qua nhóm đó hoàn toàn).
    - Trả lời cực kỳ ngắn gọn (1-5 từ).
    - Chỉ dùng thông tin có sẵn trong mô tả, tuyệt đối không bịa thêm thông tin.

    TRẢ VỀ JSON THEO ĐÚNG CẤU TRÚC SAU (Số lượng phần tử trong vqa_pairs có thể từ 1 đến 3 tùy vào nội dung mô tả):
    {{
        "image_path": "{image_path}",
        "food_name": "{food_name}",
        "vqa_pairs": [
            {{
                "nhom": "Màu sắc",
                "question": "...",
                "answer": "..."
            }},
            {{
                "nhom": "Vị trí / Hành động",
                "question": "...",
                "answer": "..."
            }}
        ]
    }}
    """

    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=MODEL_ID,
                temperature=0.1, # Nhiệt độ cực thấp để chống bịa đặt (hallucination)
                response_format={"type": "json_object"}
            )
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            error_msg = str(e).lower()
            # Bắt lỗi quá tải hoặc hết lượt
            if "503" in error_msg or "unavailable" in error_msg or "429" in error_msg or "rate limit" in error_msg:
                wait_time = 3 * (attempt + 1)
                print(f"\n[!] Máy chủ bận. Đang thử lại lần {attempt + 1}/{max_retries} sau {wait_time}s...")
                time.sleep(wait_time)
            else:
                print(f"\n[!] Lỗi không thể khắc phục ở ảnh {image_path}: {e}")
                return None
                
    print(f"\n[-] Bỏ qua ảnh {image_path} sau {max_retries} lần thử thất bại.")
    return None

# ==========================================
# 3. LUỒNG CHẠY CHÍNH
# ==========================================
def main():
    if not INPUT_CSV.exists():
        print(f"Lỗi: Không tìm thấy tệp {INPUT_CSV}")
        return

    # Đọc danh sách mô tả từ CSV
    descriptions = []
    with open(INPUT_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Bỏ qua những ảnh chưa lấy được mô tả (NaN)
            if row['Image_Description'] != 'NaN' and row['Image_Description'].strip() != '':
                descriptions.append(row)

    # Đọc dữ liệu đã xử lý để Resume (Tránh chạy lại từ đầu nếu tắt máy)
    final_dataset = []
    processed_paths = set()
    
    if OUTPUT_JSON.exists():
        with open(OUTPUT_JSON, 'r', encoding='utf-8') as f:
            try:
                final_dataset = json.load(f)
                processed_paths = {item['image_path'] for item in final_dataset}
            except json.JSONDecodeError:
                final_dataset = []

    print(f"Tổng số ảnh có mô tả hợp lệ: {len(descriptions)}")
    print(f"Đã xử lý trước đó: {len(processed_paths)} ảnh")

    # Bắt đầu vòng lặp tạo câu hỏi
    for item in tqdm(descriptions, desc="Generating Visual QA"):
        img_path = item['Image_Path']
        
        if img_path in processed_paths:
            continue

        result = generate_visual_qa(img_path, item['Food_Name'], item['Image_Description'])
        
        if result and "vqa_pairs" in result:
            final_dataset.append(result)
            
            # Ghi vào file ngay lập tức để bảo toàn dữ liệu
            with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
                json.dump(final_dataset, f, ensure_ascii=False, indent=4)
        
        # Tạm nghỉ 2 giây để khớp với Rate Limit 30 RPM của bản free Llama 3.3 70B
        time.sleep(2)

    print(f"\n--- HOÀN TẤT! ---")
    print(f"Dữ liệu Visual QA đã được lưu an toàn tại: {OUTPUT_JSON}")

if __name__ == "__main__":
    main()