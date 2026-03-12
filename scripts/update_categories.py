"""
Script để cập nhật category cho các violations dựa trên description
"""
import json
import re
from typing import Dict, List, Optional

# Định nghĩa các từ khóa cho từng category
CATEGORY_KEYWORDS = {
    "Vi phạm tín hiệu giao thông": [
        "biển báo", "vạch kẻ đường", "tín hiệu", "đèn giao thông", "đèn đỏ", "đèn vàng", 
        "hiệu lệnh", "chỉ dẫn", "biển báo hiệu", "tín hiệu đèn", "đèn tín hiệu"
    ],
    "Xe ô tô": [
        "xe ô tô", "ô tô", "xe hơi", "xe con", "xe sedan", "xe SUV", "xe 4 chỗ", "xe 5 chỗ", 
        "xe 7 chỗ", "xe 9 chỗ", "xe pickup", "xe bán tải nhỹ"
    ],
    "Rơ moóc, sơ mi rơ moóc": [
        "rơ moóc", "sơ mi rơ moóc", "rơmoóc", "sơmi rơmoóc", "xe đầu kéo", "container rơ moóc"
    ],
    "Xe mô tô, xe máy": [
        "xe mô tô", "mô tô", "xe máy", "xe gắn máy", "xe hai bánh", "xe scooter", 
        "xe máy điện", "xe moto", "motor", "motorcycle"
    ],
    "Người đi bộ": [
        "người đi bộ", "đi bộ", "bộ hành", "người qua đường", "vỉa hè", "lề đường"
    ],
    "Xe thô sơ": [
        "xe thô sơ", "xe bò", "xe ngựa", "xe kéo tay", "xe đạp thồ", "xe xích lô"
    ],
    "Xe đạp": [
        "xe đạp", "đạp xe", "xe đạp điện", "bicycle"
    ],
    "Kinh doanh vận tải": [
        "kinh doanh vận tải", "vận tải", "kinh doanh", "doanh nghiệp vận tải", 
        "hoạt động vận tải", "giấy phép kinh doanh", "vận chuyển hàng hóa", "vận chuyển hành khách"
    ],
    "Quản lý nhà nước": [
        "quản lý nhà nước", "cán bộ", "công chức", "viên chức", "thanh tra", 
        "kiểm tra", "giám sát", "cấp phép", "đăng ký", "đăng kiểm"
    ],
    "Vi phạm giấy tờ": [
        "giấy phép lái xe", "bằng lái xe", "giấy tờ", "giấy phép", "giấy chứng nhận", 
        "chứng nhận", "đăng ký xe", "cavet", "bảo hiểm", "giấy phép kinh doanh",
        "chứng chỉ", "giấy chứng minh", "không có giấy phép", "quên bằng lái"
    ],
    "Xe tải, container": [
        "xe tải", "xe container", "container", "xe chở hàng", "xe tải nặng", 
        "xe tải nhẹ", "xe ben", "xe đông lạnh", "xe chuyên dùng"
    ],
    "Vi phạm dừng đỗ xe": [
        "dừng xe", "đỗ xe", "đỗ", "dừng", "đậu xe", "đỗ sai quy định", 
        "dừng sai", "nơi cấm dừng", "nơi cấm đỗ", "đỗ trên vỉa hè"
    ],
    "Tàu thủy, thuyền": [
        "tàu thủy", "thuyền", "tàu", "phương tiện thủy", "đường thủy", 
        "sông", "biển", "cảng", "bến thủy"
    ],
    "Taxi, xe du lịch": [
        "taxi", "xe taxi", "xe du lịch", "xe hợp đồng", "xe dịch vụ", 
        "grab", "uber", "xe công nghệ"
    ],
    "Xe khách, xe buýt": [
        "xe khách", "xe buýt", "xe bus", "xe giường nằm", "xe limousine", 
        "vận tải hành khách", "xe chở khách"
    ],
    "Vi phạm tốc độ": [
        "tốc độ", "quá tốc độ", "chạy quá tốc độ", "vượt tốc độ", "tốc độ tối đa", 
        "giới hạn tốc độ", "chạy nhanh", "chạy chậm"
    ],
    "Đào tạo lái xe": [
        "đào tạo lái xe", "học lái xe", "trường dạy lái", "giáo viên dạy lái", 
        "sát hạch lái xe", "cấp bằng lái", "học viên", "giảng viên"
    ],
    "Tàu hỏa, đường sắt": [
        "tàu hỏa", "tàu lửa", "đường sắt", "đường ray", "giao lộ đường sắt", 
        "ga tàu", "đường ngang", "rào chắn"
    ],
    "Vi phạm chở người/hàng": [
        "chở người", "chở hàng", "quá tải", "chở quá số người", "chở quá tải trọng", 
        "hàng hóa", "chất cấm", "chở trẻ em", "không đội mũ bảo hiểm"
    ],
    "Vi phạm về rượu bia": [
        "rượu", "bia", "chất kích thích", "ma túy", "đồ uống có cồn", 
        "nồng độ cồn", "say xỉn", "sử dụng rượu bia", "test nồng độ cồn"
    ]
}

def classify_violation(description: str) -> str:
    """Phân loại violation dựa trên description"""
    description_lower = description.lower()
    
    # Tính điểm cho mỗi category
    category_scores = {}
    
    for category, keywords in CATEGORY_KEYWORDS.items():
        score = 0
        for keyword in keywords:
            # Đếm số lần xuất hiện của từ khóa
            count = description_lower.count(keyword.lower())
            if count > 0:
                # Từ khóa càng dài, điểm càng cao
                score += count * len(keyword.split())
        
        if score > 0:
            category_scores[category] = score
    
    # Nếu không tìm thấy category phù hợp, trả về "Vi phạm khác"
    if not category_scores:
        return "Vi phạm khác"
    
    # Trả về category có điểm cao nhất
    return max(category_scores, key=category_scores.get)

def update_categories_in_violations():
    """Cập nhật categories cho tất cả violations"""
    # Đọc file violations_100.json
    with open(r"c:\Users\Mr Hieu\Documents\vietnamese-traffic-law-qa\data\processed\violations_100.json", 
              "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # Cập nhật category cho từng violation
    updated_count = 0
    for violation in data["violations"]:
        old_category = violation.get("category", "")
        new_category = classify_violation(violation["description"])
        
        if old_category != new_category:
            violation["category"] = new_category
            updated_count += 1
            print(f"ID {violation['id']}: '{old_category}' -> '{new_category}'")
    
    # Cập nhật metadata
    data["metadata"]["processed_date"] = "2025-11-24T21:00:00.000000"
    data["metadata"]["processing_pipeline"] = "raw->processed (direct) + category_update"
    
    # Tính toán lại số lượng categories
    unique_categories = set()
    for violation in data["violations"]:
        unique_categories.add(violation["category"])
    
    data["metadata"]["validation_summary"]["categories"] = len(unique_categories)
    
    print(f"\nĐã cập nhật {updated_count} violations")
    print(f"Tổng số categories: {len(unique_categories)}")
    print("Categories hiện tại:", sorted(unique_categories))
    
    # Ghi lại file
    with open(r"c:\Users\Mr Hieu\Documents\vietnamese-traffic-law-qa\data\processed\violations_100.json", 
              "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print("\nĐã lưu file violations_100.json thành công!")

if __name__ == "__main__":
    update_categories_in_violations()