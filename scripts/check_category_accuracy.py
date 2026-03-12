"""
Script kiểm tra tính chính xác của categories trong violations_100.json 
dựa trên file nguồn nghi_dinh_100_2019.json
"""
import json
import re
from collections import defaultdict

# Mapping từ articles sang expected categories dựa trên nội dung
ARTICLE_CATEGORY_MAPPING = {
    "Điều 5": "Xe ô tô",  # Xử phạt người điều khiển xe ô tô
    "Điều 6": "Xe mô tô, xe máy",  # Xử phạt người điều khiển xe mô tô, xe gắn máy
    "Điều 7": "Xe đạp",  # Xử phạt người điều khiển xe đạp, xe đạp máy
    "Điều 8": "Xe thô sơ",  # Xử phạt người điều khiển xe thô sơ
    "Điều 9": "Người đi bộ",  # Xử phạt người đi bộ
    "Điều 10": "Vi phạm tín hiệu giao thông",  # Vi phạm quy định về tín hiệu đường bộ
    "Điều 11": "Vi phạm dừng đỗ xe",  # Vi phạm quy định về dừng, đỗ xe
    "Điều 12": "Vi phạm tốc độ",  # Vi phạm quy định về tốc độ
    "Điều 13": "Kinh doanh vận tải",  # Vi phạm trong hoạt động kinh doanh vận tải
    "Điều 14": "Vi phạm giấy tờ",  # Vi phạm về giấy tờ, chứng từ
    "Điều 15": "Đào tạo lái xe",  # Vi phạm trong đào tạo lái xe
    "Điều 16": "Quản lý nhà nước",  # Vi phạm của cơ quan quản lý
    "Điều 17": "Vi phạm chở người/hàng",  # Vi phạm về chở người và hàng hóa
    "Điều 18": "Vi phạm về rượu bia",  # Vi phạm về rượu bia, chất kích thích
    "Điều 19": "Tàu hỏa, đường sắt",  # Vi phạm giao thông đường sắt - Tàu hỏa
    "Điều 20": "Tàu hỏa, đường sắt",  # Vi phạm giao thông đường sắt - Cán bộ nhân viên
    "Điều 21": "Tàu hỏa, đường sắt",  # Vi phạm giao thông đường sắt - Tổ chức, cá nhân khác
}

def load_source_document():
    """Đọc file nguồn nghi_dinh_100_2019.json"""
    with open(r"c:\Users\Mr Hieu\Documents\vietnamese-traffic-law-qa\data\raw\legal_documents\nghi_dinh_100_2019.json", 
              "r", encoding="utf-8") as f:
        return json.load(f)

def load_violations():
    """Đọc file violations_100.json"""
    with open(r"c:\Users\Mr Hieu\Documents\vietnamese-traffic-law-qa\data\processed\violations_100.json", 
              "r", encoding="utf-8") as f:
        return json.load(f)

def extract_article_from_legal_basis(legal_basis):
    """Trích xuất article từ legal_basis"""
    if isinstance(legal_basis, dict):
        return legal_basis.get("article", "")
    return ""

def check_category_accuracy():
    """Kiểm tra tính chính xác của categories"""
    source_doc = load_source_document()
    violations_data = load_violations()
    
    print("=== KIỂM TRA TÍNH CHÍNH XÁC CỦA CATEGORIES ===\n")
    
    # Phân tích theo article
    article_analysis = defaultdict(lambda: {
        'violations': [],
        'categories': set(),
        'expected_category': '',
        'correct_count': 0,
        'total_count': 0
    })
    
    # Duyệt qua tất cả violations
    for violation in violations_data["violations"]:
        article = extract_article_from_legal_basis(violation.get("legal_basis", {}))
        if article:
            current_category = violation.get("category", "")
            expected_category = ARTICLE_CATEGORY_MAPPING.get(article, "Vi phạm khác")
            
            article_analysis[article]['violations'].append({
                'id': violation['id'],
                'description': violation['description'][:100] + "...",
                'current_category': current_category,
                'expected_category': expected_category,
                'is_correct': current_category == expected_category
            })
            
            article_analysis[article]['categories'].add(current_category)
            article_analysis[article]['expected_category'] = expected_category
            article_analysis[article]['total_count'] += 1
            
            if current_category == expected_category:
                article_analysis[article]['correct_count'] += 1
    
    # In kết quả phân tích
    total_violations = 0
    total_correct = 0
    
    for article in sorted(article_analysis.keys()):
        data = article_analysis[article]
        accuracy = (data['correct_count'] / data['total_count']) * 100 if data['total_count'] > 0 else 0
        
        print(f"📋 {article}")
        print(f"   Expected Category: {data['expected_category']}")
        print(f"   Current Categories: {', '.join(data['categories'])}")
        print(f"   Accuracy: {data['correct_count']}/{data['total_count']} ({accuracy:.1f}%)")
        
        # Hiển thị một số violations không đúng category
        incorrect_violations = [v for v in data['violations'] if not v['is_correct']]
        if incorrect_violations:
            print(f"   ❌ Incorrect categorizations (showing first 3):")
            for v in incorrect_violations[:3]:
                print(f"      ID {v['id']}: '{v['current_category']}' should be '{v['expected_category']}'")
                print(f"      Description: {v['description']}")
        
        print()
        
        total_violations += data['total_count']
        total_correct += data['correct_count']
    
    # Tổng kết
    overall_accuracy = (total_correct / total_violations) * 100 if total_violations > 0 else 0
    print("=" * 60)
    print(f"📊 TỔNG KẾT:")
    print(f"   Total violations: {total_violations}")
    print(f"   Correctly categorized: {total_correct}")
    print(f"   Overall accuracy: {overall_accuracy:.1f}%")
    print("=" * 60)
    
    return article_analysis

def generate_corrections():
    """Tạo danh sách các correction cần thiết"""
    violations_data = load_violations()
    
    corrections = []
    for violation in violations_data["violations"]:
        article = extract_article_from_legal_basis(violation.get("legal_basis", {}))
        if article:
            current_category = violation.get("category", "")
            expected_category = ARTICLE_CATEGORY_MAPPING.get(article, "Vi phạm khác")
            
            if current_category != expected_category:
                corrections.append({
                    'id': violation['id'],
                    'article': article,
                    'current_category': current_category,
                    'expected_category': expected_category,
                    'description': violation['description'][:150] + "..."
                })
    
    print(f"\n🔧 CẦN SỬA {len(corrections)} VIOLATIONS:")
    print("-" * 80)
    
    for correction in corrections[:20]:  # Hiển thị 20 đầu tiên
        print(f"ID {correction['id']} ({correction['article']}): "
              f"'{correction['current_category']}' → '{correction['expected_category']}'")
    
    if len(corrections) > 20:
        print(f"... và {len(corrections) - 20} violations khác")
    
    return corrections

if __name__ == "__main__":
    article_analysis = check_category_accuracy()
    corrections = generate_corrections()