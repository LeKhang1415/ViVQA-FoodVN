import json
import pandas as pd
import re

# Đường dẫn file JSON đầu vào và CSV đầu ra 
INPUT_JSON = 'data/foodvqa_knowledge_dataset.json'
OUTPUT_CSV = 'data/foodvqa_knowledge_dataset.csv'

def remove_text_in_parentheses(text):
    """
    Hàm dùng biểu thức chính quy (regex) để tìm và xóa toàn bộ ngoặc đơn ()
    kèm theo nội dung bên trong nó, đồng thời xóa luôn khoảng trắng thừa.
    """
    if not isinstance(text, str):
        return text
    # Xóa nội dung trong ngoặc tròn ( )
    cleaned_text = re.sub(r'\s*\([^)]*\)', '', text)
    return cleaned_text.strip()

def clean_quotes(text):
    """
    Hàm lột bỏ dấu ngoặc kép (" ") hoặc dấu nháy đơn (' ') bọc ngoài cùng câu.
    """
    if not isinstance(text, str):
        return text
    # Lột bỏ khoảng trắng, sau đó lột dấu ngoặc kép, dấu nháy đơn ở 2 đầu
    return text.strip(' "\'')

def main():
    print("Đang đọc file JSON...")
    try:
        with open(INPUT_JSON, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Lỗi: Không tìm thấy tệp {INPUT_JSON}")
        return

    csv_data = []

    # Lặp qua từng món ăn
    for item in data:
        img_path = item.get("image_path", "")
        
        # Xóa chữ trong ngoặc của tên món
        food_name = remove_text_in_parentheses(item.get("food_name", ""))
        food_name = clean_quotes(food_name)
        
        # Lặp qua các cặp câu hỏi
        for pair in item.get("vqa_pairs", []):
            # 1. Xóa nội dung trong ngoặc đơn ( )
            question = remove_text_in_parentheses(pair.get("question", ""))
            answer = remove_text_in_parentheses(pair.get("answer", ""))
            
            # 2. Xóa dấu ngoặc kép " " bọc bên ngoài
            question = clean_quotes(question)
            answer = clean_quotes(answer)
            
            # 3. Lọc bỏ dữ liệu rỗng
            if question == "" or answer == "":
                continue
                
            csv_data.append({
                "Image_Path": img_path,
                "Food_Name": food_name,
                "Question_Group": pair.get("nhom", ""),
                "Question": question,
                "Answer": answer
            })

    # Chuyển đổi thành dạng bảng bằng Pandas
    df = pd.DataFrame(csv_data)
    
    # Lưu ra file CSV
    df.to_csv(OUTPUT_CSV, index=False, encoding='utf-8-sig')
    
    print("\n--- HOÀN TẤT ---")
    print(f"Số câu hỏi giữ lại và làm sạch thành công: {len(df)}")
    print(f"File CSV sạch 100% đã được lưu tại: {OUTPUT_CSV}")

if __name__ == "__main__":
    main()