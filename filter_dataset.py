import pandas as pd

# Đường dẫn file (Sửa lại đường dẫn nếu file của bạn nằm trong thư mục data/)
INPUT_CSV = 'data/foodvqa_visual_dataset_filtered.csv'
OUTPUT_CSV = 'data/foodvqa_visual_dataset_filtered1.csv'

def is_valid_row(row):
    """
    Hàm kiểm tra từng dòng trong file CSV.
    Trả về True nếu giữ lại, False nếu xóa bỏ.
    """
    # Chuyển dữ liệu về chữ thường để dễ so sánh
    q = str(row['Question']).lower()
    a = str(row['Answer']).lower()
    nhom = str(row['Question_Group']).lower()

    # ==========================================
    # QUY TẮC MỚI: BỎ HOÀN TOÀN NHÓM "TRẠNG THÁI"
    # ==========================================
    if "trạng thái" in nhom:
        return False

    # QUY TẮC 1: Bắt lỗi râu ông nọ cắm cằm bà kia (Hỏi liệt kê nhưng trả lời tính từ)
    if "những gì" in q and ("đầy" in a or "nhiều" in a or "ít" in a):
        return False
        
    # QUY TẮC 2: Bắt lỗi sai nhóm "Số lượng/Hình dáng"
    if "số lượng" in nhom or "hình dáng" in nhom:
        if "những gì" in q or "có những thành phần" in q:
            return False
            
    # QUY TẮC 3: Bắt lỗi câu trả lời bị dính tạp âm (quá 10 từ)
    if len(str(row['Answer']).split()) > 10:
        return False

    # ==========================================
    # QUY TẮC 4: XÓA ĐÁP ÁN "KHÔNG RÕ"
    # ==========================================
    if "không rõ" in a:
        return False

    return True

def main():
    print(f"Đang đọc file {INPUT_CSV}...")
    try:
        df = pd.read_csv(INPUT_CSV)
    except FileNotFoundError:
        print(f"Lỗi: Không tìm thấy file {INPUT_CSV}")
        return

    original_count = len(df)

    # Áp dụng hàm lọc qua từng dòng (axis=1)
    df_filtered = df[df.apply(is_valid_row, axis=1)]
    
    removed_count = original_count - len(df_filtered)

    # Lưu lại file CSV mới (dùng utf-8-sig để Excel không lỗi font)
    df_filtered.to_csv(OUTPUT_CSV, index=False, encoding='utf-8-sig')

    print("\n--- KẾT QUẢ LỌC ---")
    print(f"Tổng số câu hỏi ban đầu: {original_count}")
    print(f"Số câu hỏi đã xóa      : {removed_count}")
    print(f"Số câu hỏi giữ lại     : {len(df_filtered)}")
    print(f"\nDữ liệu sạch đã được lưu tại: {OUTPUT_CSV}")

if __name__ == "__main__":
    main()