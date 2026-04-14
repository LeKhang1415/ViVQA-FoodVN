import json
import time
from pathlib import Path
from groq import Groq
from tqdm import tqdm

# =================================================================
# 1. CẤU HÌNH ĐƯỜNG DẪN (LOCAL ONLY)
# =================================================================
DATA_DIR = Path(r"C:\Users\Admin\Desktop\ViVQA-Food\data")
INPUT_FILE = DATA_DIR / "food_knowledge_ready.json"
OUTPUT_FILE = DATA_DIR / "vivqa_food_dataset_final.json"

# Cấu hình API Groq
GROQ_API_KEY = ""
client = Groq(api_key=GROQ_API_KEY)

# =================================================================
# 2. HÀM TẠO VQA VỚI ĐA DẠNG CÂU HỎI VÀ CÂU TRẢ LỜI
# =================================================================
def generate_vqa_for_dish(dish_data):
    """
    Sử dụng LLM làm 'constrained generator' để tạo dataset với 5 biến thể câu hỏi 
    và 5 biến thể câu trả lời cho mỗi danh mục[cite: 189].
    """
    ten_mon = dish_data.get('ten_mon', 'món ăn')
    
    prompt = f"""
    Bạn là chuyên gia ngôn ngữ và ẩm thực Việt Nam, đang xây dựng tập dữ liệu Visual Question Answering (VQA) để huấn luyện AI.
    Dữ liệu nền tảng của món ăn: {json.dumps(dish_data, ensure_ascii=False)}

    NHIỆM VỤ:
    Tạo 5 nhóm thông tin. Với mỗi nhóm, hãy cung cấp ĐÚNG 05 cách đặt câu hỏi khác nhau (questions) và ĐÚNG 05 cách trả lời khác nhau (answers).

    CÁC NHÓM BẮT BUỘC (Phải dựa trên dữ liệu nền tảng):
    1. Nhận diện: Các câu hỏi để AI nhận biết tên món ăn khi nhìn vào ảnh (VD: Đây là món gì?, Ảnh chụp món nào?).
    2. Thành phần: Hỏi về nguyên liệu chính, topping hoặc màu sắc đặc trưng có thể quan sát.
    3. Vùng miền: Hỏi về quê hương, xuất xứ hoặc nơi món ăn này phổ biến.
    4. Cách nấu: Hỏi về quy trình hoặc bước chế biến cốt lõi nhất.
    5. Dinh dưỡng: Hỏi về mức độ calo (Thấp/Trung bình/Cao) của món ăn.

    RÀNG BUỘC KỸ THUẬT NGHIÊM NGẶT:
    - Độ dài: Câu hỏi và câu trả lời phải RẤT NGẮN GỌN (từ 1 đến tối đa 20 từ).
    - Tính đồng nghĩa: 5 câu hỏi trong 1 nhóm phải mang cùng một ý. 5 câu trả lời phải mang cùng một đáp án thực tế.
    - Tính chân thực: Tuyệt đối không sinh ra thông tin giả mạo (hallucination), chỉ dùng dữ liệu được cung cấp.

    ĐỊNH DẠNG ĐẦU RA (Chỉ trả về JSON duy nhất, không có văn bản giải thích):
    {{
        "ten_mon": "{ten_mon}",
        "image_folder": "{dish_data.get('image_folder')}",
        "vqa_pairs": [
            {{
                "nhom": "Nhận diện",
                "questions": ["...", "...", "...", "...", "..."],
                "answers": ["...", "...", "...", "...", "..."]
            }},
            {{ "nhom": "Thành phần", "questions": ["..."], "answers": ["..."] }},
            {{ "nhom": "Vùng miền", "questions": ["..."], "answers": ["..."] }},
            {{ "nhom": "Cách nấu", "questions": ["..."], "answers": ["..."] }},
            {{ "nhom": "Dinh dưỡng", "questions": ["..."], "answers": ["..."] }}
        ]
    }}
    """

    try:
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            temperature=0.5,
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        print(f"\n[!] Lỗi món {ten_mon}: {e}")
        return None

# =================================================================
# 3. LUỒNG CHẠY CHÍNH
# =================================================================
def main():
    if not INPUT_FILE.exists():
        print(f"Lỗi: Không tìm thấy file {INPUT_FILE}")
        return

    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        food_list = json.load(f)

    final_dataset = []
    print(f"Đang tạo dataset VQA đa biến thể (5 câu hỏi & 5 câu trả lời/nhóm) cho {len(food_list)} món...")

    for dish in tqdm(food_list, desc="Generating ViVQA-Food"):
        vqa_result = generate_vqa_for_dish(dish)
        
        if vqa_result:
            # Kiểm tra tính đầy đủ của dữ liệu
            if len(vqa_result.get("vqa_pairs", [])) == 5:
                final_dataset.append(vqa_result)
                
                with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
                    json.dump(final_dataset, f, ensure_ascii=False, indent=4)
            else:
                print(f"\n[!] Bỏ qua {dish.get('ten_mon')} do không đủ số nhóm yêu cầu.")
        
        # Nghỉ để tránh Rate Limit của Groq 
        time.sleep(1.2)

    print(f"\n--- HOÀN TẤT ---")
    print(f"Dataset đã được cập nhật thành công tại: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()