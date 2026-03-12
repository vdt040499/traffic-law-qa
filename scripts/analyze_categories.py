"""
Script thống kê categories sau khi cập nhật
"""
import json
from collections import Counter

def analyze_categories():
    """Phân tích và thống kê categories"""
    # Đọc file violations_100.json
    with open(r"c:\Users\Mr Hieu\Documents\vietnamese-traffic-law-qa\data\processed\violations_100.json", 
              "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # Đếm số lượng violations theo category
    category_counts = Counter()
    for violation in data["violations"]:
        category_counts[violation["category"]] += 1
    
    print("=== THỐNG KÊ CATEGORIES SAU KHI CẬP NHẬT ===")
    print(f"Tổng số violations: {len(data['violations'])}")
    print(f"Tổng số categories: {len(category_counts)}")
    print()
    
    print("PHÂN BỐ THEO CATEGORY:")
    print("-" * 50)
    
    # Sắp xếp theo số lượng giảm dần
    for category, count in category_counts.most_common():
        percentage = (count / len(data['violations'])) * 100
        print(f"{category:<30} | {count:>4} | {percentage:>5.1f}%")
    
    print("-" * 50)
    print(f"{'TỔNG':<30} | {len(data['violations']):>4} | 100.0%")

if __name__ == "__main__":
    analyze_categories()