import json
import csv
from pathlib import Path

# Cấu hình đường dẫn
DATA_DIR = Path(r"C:\Users\Admin\Desktop\ViVQA-Food\data")
INPUT_JSON = DATA_DIR / "cleaned.json" 
OUTPUT_CSV = DATA_DIR / "vietnam_food.csv"

def json_to_csv(json_file, csv_file):
    # Đọc file JSON gốc
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # --- Sắp xếp dữ liệu theo nhóm ---
    # Sử dụng hàm sort với key là giá trị của trường 'nhom'
    data.sort(key=lambda x: x.get('nhom', ''))
        
    # Lấy tiêu đề cột từ các keys của món ăn đầu tiên
    if not data:
        print("Dữ liệu trống.")
        return
    headers = list(data[0].keys())

    # Mở file CSV để ghi (dùng utf-8-sig để không lỗi font Excel)
    with open(csv_file, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=headers, extrasaction='ignore')
        writer.writeheader()
        
        for item in data:
            row_data = {}
            for key, value in item.items():
                # Trường hợp 1: Value là một danh sách (list)
                if isinstance(value, list):
                    temp_list = []
                    for element in value:
                        if isinstance(element, (dict, list)):
                            temp_list.append(json.dumps(element, ensure_ascii=False))
                        else:
                            temp_list.append(str(element).strip())
                    row_data[key] = ", ".join(temp_list)
                
                # Trường hợp 2: Value là một dictionary
                elif isinstance(value, dict):
                    row_data[key] = json.dumps(value, ensure_ascii=False)
                
                # Trường hợp 3: Value là chuỗi hoặc số bình thường
                else:
                    row_data[key] = value
                    
            writer.writerow(row_data)

    print(f"Đã sắp xếp theo nhóm và xuất file thành công ra: {csv_file}")

# Thực thi hàm
if __name__ == "__main__":
    json_to_csv(INPUT_JSON, OUTPUT_CSV)