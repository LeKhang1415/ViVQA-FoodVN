import json
import time
from pathlib import Path
from tqdm import tqdm
from groq import Groq

# ==========================================
# 1. CẤU HÌNH ĐƯỜNG DẪN & API
# ==========================================
# 🚨 Nhớ điền API KEY của bạn vào đây:
API_KEY = ''
client = Groq(api_key=API_KEY)

PROJECT_ROOT = Path(r"C:\Users\Admin\Desktop\ViVQA-Food")
DATA_DIR = PROJECT_ROOT / "data"

INPUT_JSON = DATA_DIR / "vivqa_food_dataset_final.json"
OUTPUT_JSON = DATA_DIR / "foodvqa_knowledge_dataset.json"

MODEL_ID = "llama-3.1-8b-instant"

# ==========================================
# 2. HÀM SINH CÂU HỎI TỪ KIẾN THỨC
# ==========================================
def generate_knowledge_qa(dish_data, max_retries=5):
    ten_mon = dish_data.get('ten_mon', '')
    context = f"""
    - Tên món: {ten_mon}
    - Nguồn gốc/Vùng miền: {dish_data.get('vung_mien', '')}
    - Nguyên liệu chính: {', '.join(dish_data.get('thanh_phan_chinh', []))}
    - Các bước nấu: {', '.join(dish_data.get('cac_buoc_nau', []))}
    - Cách ăn: {dish_data.get('cach_an', '')}
    """

    # Mình bỏ luôn yêu cầu in image_path ở LLM cho nó rảnh nợ
    prompt = f"""
    Bạn là chuyên gia về ẩm thực Việt Nam và tạo dữ liệu VQA.
    Dưới đây là thông tin chi tiết về món '{ten_mon}':
    {context}

    NHIỆM VỤ: Tạo ĐÚNG 04 cặp câu hỏi và câu trả lời dựa trên thông tin trên.

    YÊU CẦU:
    1. Nguyên liệu: Hỏi về thành phần (1-10 từ).
    2. Nguồn gốc: Hỏi về vùng miền (1-10 từ).
    3. Cách nấu: Hỏi về một bước nấu (tối đa 25 từ).
    4. Trải nghiệm: Hỏi về cách thưởng thức (tối đa 25 từ).

    ĐA DẠNG HÓA: Dùng nhiều cách hỏi khác nhau (Hãy kể, Có phải, Bạn biết không...)

    TRẢ VỀ JSON THEO CẤU TRÚC SAU:
    {{
        "food_name": "{ten_mon}",
        "vqa_pairs": [
            {{ "nhom": "Nguyên liệu", "question": "...", "answer": "..." }},
            {{ "nhom": "Nguồn gốc", "question": "...", "answer": "..." }},
            {{ "nhom": "Cách nấu", "question": "...", "answer": "..." }},
            {{ "nhom": "Cách ăn", "question": "...", "answer": "..." }}
        ]
    }}
    """

    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=MODEL_ID,
                temperature=0.4, 
                response_format={"type": "json_object"}
            )
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            error_msg = str(e).lower()
            if "503" in error_msg or "429" in error_msg or "rate limit" in error_msg:
                wait_time = 3 * (attempt + 1)
                time.sleep(wait_time)
            else:
                return None
    return None

# ==========================================
# 3. LUỒNG CHẠY CHÍNH
# ==========================================
def main():
    if not INPUT_JSON.exists():
        print(f"Lỗi: Không tìm thấy tệp {INPUT_JSON}")
        return

    with open(INPUT_JSON, 'r', encoding='utf-8') as f:
        data = json.load(f)

    final_dataset = []
    processed_paths = set()
    
    if OUTPUT_JSON.exists():
        try:
            with open(OUTPUT_JSON, 'r', encoding='utf-8') as f:
                final_dataset = json.load(f)
                # Đọc image_path một cách chuẩn xác
                processed_paths = {item.get('image_path') for item in final_dataset if item.get('image_path')}
        except json.JSONDecodeError:
            print("\n[!] Lỗi đọc file cũ, sẽ chạy lại từ đầu!")
            final_dataset = []
            processed_paths = set()

    # Lọc danh sách ĐÚNG để thanh tiến trình đếm chuẩn
    items_to_process = [
        item for item in data 
        if item.get('image_path') and item.get('image_path') not in processed_paths
    ]

    print(f"Tổng số bản ghi gốc: {len(data)}")
    print(f"Đã làm thành công: {len(processed_paths)}")
    print(f"Số lượng còn lại cần xử lý: {len(items_to_process)}")

    if len(items_to_process) == 0:
        print("\nTất cả dữ liệu đã được xử lý xong!")
        return

    for item in tqdm(items_to_process, desc="Generating Knowledge QA"):
        img_path = item.get('image_path')
        result = generate_knowledge_qa(item)
        
        if result and "vqa_pairs" in result:
            # 🔥 ĐÂY LÀ DÒNG CODE CỨU CÁNH: Ép Python gán thẳng đường dẫn ảnh vào!
            result["image_path"] = img_path
            
            final_dataset.append(result)
            
            with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
                json.dump(final_dataset, f, ensure_ascii=False, indent=4)
        
        time.sleep(2)

    print(f"\n--- HOÀN TẤT! ---")
    print(f"Dữ liệu đã được lưu tại: {OUTPUT_JSON}")

if __name__ == "__main__":
    main()