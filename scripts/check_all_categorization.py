#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script kiểm tra toàn diện phân loại category cho TẤT CẢ các điều trong violations_168.json
"""

import json
import re
from collections import Counter, defaultdict

def analyze_all_categorization():
    """Kiểm tra phân loại toàn bộ các vi phạm"""
    
    violations_path = r"c:\Users\Mr Hieu\Documents\vietnamese-traffic-law-qa\data\processed\violations_168.json"
    raw_path = r"c:\Users\Mr Hieu\Documents\vietnamese-traffic-law-qa\data\raw\legal_documents\nghi_dinh_168_2024.json"
    
    print("🔍 KIỂM TRA TOÀN DIỆN PHÂN LOẠI TẤT CẢ CÁC ĐIỀU")
    print("=" * 70)
    
    # Load processed violations
    with open(violations_path, 'r', encoding='utf-8') as f:
        processed_data = json.load(f)
    
    violations = processed_data.get('violations', [])
    
    # Load raw data để kiểm tra title gốc
    with open(raw_path, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)
    
    key_articles = raw_data.get('key_articles', {})
    
    print(f"📊 Tổng số violations: {len(violations)}")
    print(f"📋 Số articles trong raw: {len(key_articles)}")
    print()
    
    # Phân tích theo article
    article_analysis = defaultdict(lambda: {
        'title': '',
        'violations_count': 0,
        'categories': Counter(),
        'violations': []
    })
    
    # Group violations by article
    for violation in violations:
        source_article = violation.get('source_article', 'unknown')
        category = violation.get('category', 'unknown')
        
        article_analysis[source_article]['violations_count'] += 1
        article_analysis[source_article]['categories'][category] += 1
        article_analysis[source_article]['violations'].append(violation)
        
        # Get title from raw data
        if source_article in key_articles:
            article_analysis[source_article]['title'] = key_articles[source_article].get('title', '')
    
    # Định nghĩa mapping expected categories dựa trên keywords trong title
    vehicle_keywords = {
        'xe ô tô': ['Xe ô tô'],
        'xe mô tô': ['Xe mô tô, xe máy'],
        'xe gắn máy': ['Xe mô tô, xe máy'],
        'mô tô': ['Xe mô tô, xe máy'],
        'xe máy chuyên dùng': ['Xe máy chuyên dùng'],
        'xe thô sơ': ['Xe thô sơ'],
        'xe đạp': ['Xe đạp'],
        'người đi bộ': ['Người đi bộ'],
        'vật nuôi': ['Vật nuôi'],
        'đào tạo': ['Đào tạo lái xe'],
        'sát hạch': ['Đào tạo lái xe'],
        'kinh doanh vận tải': ['Kinh doanh vận tải'],
        'vận tải': ['Kinh doanh vận tải'],
        'đăng kiểm': ['Vi phạm khác', 'Xe máy chuyên dùng', 'Xe ô tô']
    }
    
    def get_expected_categories(title):
        """Lấy categories dự kiến dựa trên title"""
        title_lower = title.lower()
        expected = []
        
        for keyword, categories in vehicle_keywords.items():
            if keyword in title_lower:
                expected.extend(categories)
        
        return list(set(expected)) if expected else ['Vi phạm khác']
    
    # Phân tích từng article
    print("📋 PHÂN TÍCH TỪNG ĐIỀU:")
    print("=" * 70)
    
    total_correct = 0
    total_wrong = 0
    articles_with_issues = []
    
    for article_key in sorted(article_analysis.keys()):
        if article_key == 'unknown':
            continue
            
        analysis = article_analysis[article_key]
        title = analysis['title']
        violations_count = analysis['violations_count']
        categories = analysis['categories']
        
        expected_categories = get_expected_categories(title)
        
        print(f"\n🔸 {article_key.upper().replace('_', ' ')}")
        print(f"   Title: {title[:100]}{'...' if len(title) > 100 else ''}")
        print(f"   Violations: {violations_count}")
        print(f"   Expected categories: {', '.join(expected_categories)}")
        print(f"   Actual categories: {dict(categories)}")
        
        # Kiểm tra xem có category nào không phù hợp
        wrong_categories = []
        correct_categories = []
        
        for category, count in categories.items():
            if category in expected_categories or category == 'Vi phạm khác':
                correct_categories.append((category, count))
                total_correct += count
            else:
                wrong_categories.append((category, count))
                total_wrong += count
        
        if wrong_categories:
            print(f"   ❌ Categories có thể sai: {dict(wrong_categories)}")
            articles_with_issues.append({
                'article': article_key,
                'title': title,
                'wrong_categories': wrong_categories,
                'expected': expected_categories,
                'violations': analysis['violations']
            })
        else:
            print(f"   ✅ Tất cả categories đều phù hợp")
    
    # Chi tiết các vi phạm có thể bị phân loại sai
    if articles_with_issues:
        print(f"\n❌ CHI TIẾT CÁC VI PHẠM CÓ THỂ BỊ PHÂN LOẠI SAI:")
        print("=" * 70)
        
        for issue in articles_with_issues:
            print(f"\n📄 {issue['article'].upper().replace('_', ' ')}")
            print(f"   Title: {issue['title']}")
            print(f"   Expected: {', '.join(issue['expected'])}")
            
            # Lấy một vài vi phạm mẫu từ wrong categories
            for wrong_cat, count in issue['wrong_categories']:
                print(f"\n   ❌ Category '{wrong_cat}' ({count} violations):")
                
                sample_violations = [v for v in issue['violations'] if v.get('category') == wrong_cat][:3]
                for violation in sample_violations:
                    print(f"      - ID {violation.get('id')}: {violation.get('description', '')[:80]}...")
    
    # Thống kê tổng kết
    print(f"\n📊 THỐNG KÊ TỔNG KẾT:")
    print("=" * 50)
    print(f"✅ Vi phạm phân loại đúng: {total_correct}")
    print(f"❌ Vi phạm có thể sai: {total_wrong}")
    print(f"📋 Articles có vấn đề: {len(articles_with_issues)}")
    
    if total_correct + total_wrong > 0:
        accuracy = (total_correct / (total_correct + total_wrong)) * 100
        print(f"🎯 Độ chính xác: {accuracy:.1f}%")
    
    # Category distribution
    all_categories = Counter(v.get('category') for v in violations)
    print(f"\n📈 PHÂN BỐ CATEGORIES:")
    for category, count in sorted(all_categories.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / len(violations)) * 100
        print(f"   {category}: {count} ({percentage:.1f}%)")
    
    return {
        'total_violations': len(violations),
        'correct_classifications': total_correct,
        'wrong_classifications': total_wrong,
        'articles_with_issues': len(articles_with_issues),
        'accuracy': (total_correct / (total_correct + total_wrong)) * 100 if total_correct + total_wrong > 0 else 0
    }

def generate_fix_recommendations():
    """Tạo đề xuất sửa lỗi"""
    
    print(f"\n🛠️ ĐỀ XUẤT SỬA LỖI:")
    print("=" * 40)
    
    recommendations = [
        "1. Cải tiến hàm determine_category() để handle các edge cases:",
        "   - Kiểm tra từ khóa cụ thể trước, tổng quát sau",
        "   - Thêm logic cho các loại xe đặc biệt",
        "   - Xử lý trường hợp multi-vehicle articles",
        "",
        "2. Tạo mapping table cho article -> expected categories",
        "",
        "3. Implement fuzzy matching cho categories tương tự",
        "",
        "4. Thêm validation rules dựa trên article title",
        "",
        "5. Tạo unit tests để prevent regression"
    ]
    
    for rec in recommendations:
        print(rec)

if __name__ == "__main__":
    print("🚗 KIỂM TRA TOÀN DIỆN PHÂN LOẠI VIOLATIONS_168.JSON")
    print("=" * 70)
    
    results = analyze_all_categorization()
    
    print(f"\n🎯 KẾT LUẬN CHUNG:")
    print(f"✅ Tổng violations: {results['total_violations']}")
    print(f"✅ Phân loại đúng: {results['correct_classifications']}")
    print(f"❌ Cần kiểm tra: {results['wrong_classifications']}")
    print(f"📋 Articles có vấn đề: {results['articles_with_issues']}")
    print(f"🎯 Độ chính xác: {results['accuracy']:.1f}%")
    
    if results['wrong_classifications'] > 0:
        generate_fix_recommendations()
    else:
        print("\n🎉 TẤT CẢ PHÂN LOẠI ĐỀU CHÍNH XÁC!")