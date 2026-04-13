import json
import time
from pathlib import Path
from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

# 1. CẤU HÌNH ĐƯỜNG DẪN
DATA_DIR = Path(r"C:\Users\Admin\Desktop\ViVQA-Food\data")
INPUT_JSON = DATA_DIR / "food.json" 
OUTPUT_JSON = DATA_DIR / "vietnamese_food_vqa_knowledge.json"

# 2. KHỞI TẠO CLIENT GROQ
client = Groq(api_key = os.getenv("GROQ_API_KEY"))

def get_food_knowledge(food_name, category):
    prompt = f"""
    Hãy đóng vai chuyên gia văn hóa ẩm thực Việt Nam. 
    Cung cấp thông tin chi tiết phục vụ cho bài toán Visual Question Answering (VQA) cho món '{food_name}' (thuộc nhóm {category}).

    YÊU CẦU BẮT BUỘC: Trả về nội dung bằng ĐÚNG định dạng JSON dưới đây:
    {{
        "ten_mon": "{food_name}",
        "nhom": "{category}",
        "mo_ta": "Mô tả hương vị đặc trưng.",
        "vung_mien": "Nơi phổ biến nhất.",
        "thanh_phan_chinh": ["nguyên liệu 1", "nguyên liệu 2"],
        "phuong_phap_che_bien": "Hấp/Rán/Luộc/Nướng/Kho/Xào...",
        "cac_buoc_nau": ["Bước 1...", "Bước 2...", "Bước 3..."],
        "cach_an": "Ăn nóng hay nguội, dùng kèm với nước chấm hay rau gì?",
        "dac_diem_thi_giac": "Mô tả hình dáng, màu sắc, cách bày trí để AI nhận diện qua ảnh.",
        "calo_uoc_tinh": "Thấp/Trung bình/Cao",
        "cau_hoi_vqa": {{
            "nhan_dang": "Đây là món gì?",
            "cach_lam": "Món ăn này được nấu bằng phương pháp nào?",
            "chi_tiet": "Đặc điểm nhận dạng đặc trưng nhất của món này trên ảnh là gì?"
        }}
    }}
    """
    try:
        response = client.chat.completions.create(
            # THAY ĐỔI Ở ĐÂY: Dùng model đời mới llama-3.1
            model="llama-3.1-8b-instant", 
            messages=[
                {"role": "system", "content": "Bạn là chuyên gia ẩm thực Việt Nam. Chỉ trả về JSON."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.6
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        print(f"  -> Lỗi khi xử lý {food_name}: {e}")
        return None

def main():
    if not INPUT_JSON.exists():
        print(f"Lỗi: Không tìm thấy file {INPUT_JSON}")
        return

    with open(INPUT_JSON, "r", encoding="utf-8") as f:
        wiki_data = json.load(f)

    final_results = []
    
    # Kiểm tra xem file output đã có dữ liệu chưa để chạy tiếp (resume) nếu cần
    if OUTPUT_JSON.exists():
        with open(OUTPUT_JSON, "r", encoding="utf-8") as f_existing:
            try:
                final_results = json.load(f_existing)
                print(f"Đã tải {len(final_results)} món đã xử lý trước đó.")
            except:
                final_results = []

    # Lấy danh sách tên món đã xử lý để bỏ qua
    processed_dishes = {item["ten_mon"] for item in final_results}

    groups = wiki_data.get("danh_sach_mon_an_viet_nam", [])
    
    try:
        for group in groups:
            category = group["nhom"]
            dishes = group["danh_sach"]
            
            for dish in dishes:
                if dish in processed_dishes:
                    continue # Bỏ qua món đã làm rồi
                
                print(f"Đang xử lý: {dish}...")
                result = get_food_knowledge(dish, category)
                
                if result:
                    final_results.append(result)
                    with open(OUTPUT_JSON, "w", encoding="utf-8") as f_out:
                        json.dump(final_results, f_out, ensure_ascii=False, indent=4)
                
                time.sleep(1.5) # Nghỉ để tránh Rate Limit
    except KeyboardInterrupt:
        print("\nĐã dừng chương trình bằng phím bấm. Dữ liệu đã được lưu.")

    print(f"\n✅ HOÀN THÀNH! Tổng cộng {len(final_results)} món.")

if __name__ == "__main__":
    main()