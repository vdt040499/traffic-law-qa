#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprehensive script to add additional penalties structure to all relevant articles
"""

import json
import os
import re
from datetime import datetime

def get_additional_penalties_data():
    """Define additional penalties for each article"""
    return {
        "dieu_5": {
            # Điều 5 - Xe ô tô
            "additional_penalties": [
                "a) \"Thực hiện hành vi quy định tại điểm e khoản 4 Điều này bị tịch thu thiết bị phát tín hiệu ưu tiên lắp đặt sử dụng trái quy định\"",
                "b) \"Thực hiện hành vi quy định tại điểm đ khoản 2; điểm h, điểm i khoản 3; khoản 4; điểm a, điểm b, điểm d, điểm đ, điểm g, điểm h, điểm i khoản 5 Điều này bị tước quyền sử dụng Giấy phép lái xe từ 01 tháng đến 03 tháng\"",
                "c) \"Thực hiện hành vi quy định tại điểm c khoản 5; điểm a, điểm b khoản 6; khoản 7 Điều này bị tước quyền sử dụng Giấy phép lái xe từ 02 tháng đến 04 tháng. Thực hiện hành vi quy định tại một trong các điểm, khoản sau của Điều này mà gây tai nạn giao thông thì bị tước quyền sử dụng Giấy phép lái xe từ 02 tháng đến 04 tháng: điểm a, điểm d, điểm đ, điểm e, điểm g khoản 1; điểm b, điểm d, điểm g khoản 2; điểm b, điểm g, điểm h, điểm m, điểm n, điểm r, điểm s khoản 3; điểm a, điểm c, điểm e, điểm g, điểm h khoản 4; điểm a, điểm b, điểm e, điểm g, điểm h khoản 5 Điều này\"",
                "d) \"Thực hiện hành vi quy định tại khoản 9 Điều này hoặc tái phạm hành vi quy định tại điểm b khoản 7 Điều này, bị tước quyền sử dụng Giấy phép lái xe từ 03 tháng đến 05 tháng\"",
                "đ) \"Thực hiện hành vi quy định tại điểm a, điểm b khoản 8 Điều này bị tước quyền sử dụng Giấy phép lái xe từ 05 tháng đến 07 tháng\"",
                "e) \"Thực hiện hành vi quy định tại điểm c khoản 6 Điều này bị tước quyền sử dụng Giấy phép lái xe từ 10 tháng đến 12 tháng\"",
                "g) \"Thực hiện hành vi quy định tại điểm c khoản 8 Điều này bị tước quyền sử dụng Giấy phép lái xe từ 16 tháng đến 18 tháng\"",
                "h) \"Thực hiện hành vi quy định tại khoản 10 Điều này bị tước quyền sử dụng Giấy phép lái xe từ 22 tháng đến 24 tháng\""
            ]
        },
        "dieu_6": {
            # Điều 6 - Xe mô tô, xe gắn máy
            "additional_penalties": [
                "a) \"Thực hiện hành vi quy định tại điểm g khoản 2 Điều này bị tịch thu thiết bị phát tín hiệu ưu tiên lắp đặt, sử dụng trái quy định\"",
                "b) \"Thực hiện hành vi quy định tại điểm b, điểm e, điểm i khoản 3; điểm đ, điểm e, điểm g, điểm h khoản 4; khoản 5 Điều này bị tước quyền sử dụng Giấy phép lái xe từ 01 tháng đến 03 tháng\"",
                "c) \"Thực hiện hành vi quy định tại điểm a khoản 6; điểm a, điểm khoản 7; điểm a, điểm b, điểm c, điểm d khoản 8 Điều này bị tước quyền sử dụng Giấy phép lái xe từ 02 tháng đến 04 tháng\"",
                "d) \"Thực hiện hành vi quy định tại điểm b khoản 6; điểm đ khoản 8; khoản 9 Điều này bị tước quyền sử dụng Giấy phép lái xe từ 03 tháng đến 05 tháng\"",
                "đ) \"Thực hiện hành vi quy định tại điểm c khoản 6 Điều này bị tước quyền sử dụng Giấy phép lái xe từ 10 tháng đến 12 tháng\"",
                "e) \"Thực hiện hành vi quy định tại điểm c khoản 7 Điều này bị tước quyền sử dụng Giấy phép lái xe từ 16 tháng đến 18 tháng\"",
                "g) \"Thực hiện hành vi quy định tại điểm e, điểm g, điểm h, điểm i khoản 8 Điều này bị tước quyền sử dụng Giấy phép lái xe từ 22 tháng đến 24 tháng\""
            ]
        },
        "dieu_7": {
            # Điều 7 - Xe máy chuyên dùng
            "additional_penalties": [
                "a) \"Thực hiện hành vi quy định tại điểm b, điểm c, điểm g khoản 3; điểm a, điểm c, điểm d, điểm e khoản 4; khoản 5 Điều này bị tước quyền sử dụng Giấy phép lái xe, chứng chỉ bồi dưỡng kiến thức pháp luật về giao thông đường bộ từ 01 tháng đến 03 tháng\"",
                "b) \"Thực hiện hành vi quy định tại điểm a, điểm b khoản 6; điểm a khoản 7 Điều này bị tước quyền sử dụng Giấy phép lái xe, chứng chỉ bồi dưỡng kiến thức pháp luật về giao thông đường bộ từ 02 tháng đến 04 tháng\"",
                "c) \"Thực hiện hành vi quy định tại khoản 8 Điều này thì bị tước quyền sử dụng Giấy phép lái xe, chứng chỉ bồi dưỡng kiến thức pháp luật về giao thông đường bộ từ 05 tháng đến 07 tháng\"",
                "d) \"Thực hiện hành vi quy định tại điểm c khoản 6 Điều này thì bị tước quyền sử dụng Giấy phép lái xe, chứng chỉ bồi dưỡng kiến thức pháp luật về giao thông đường bộ từ 10 tháng đến 12 tháng\"",
                "đ) \"Thực hiện hành vi quy định tại điểm b khoản 7 Điều này thì bị tước quyền sử dụng Giấy phép lái xe, chứng chỉ bồi dưỡng kiến thức pháp luật về giao thông đường bộ từ 16 tháng đến 18 tháng\"",
                "e) \"Thực hiện hành vi quy định tại khoản 9 bị tước quyền sử dụng Giấy phép lái xe, chứng chỉ bồi dưỡng kiến thức pháp luật về giao thông đường bộ từ 22 tháng đến 24 tháng\""
            ]
        },
        "dieu_11": {
            # Điều 11 - Vi phạm khác về giao thông đường bộ
            "additional_penalties": [
                "a) \"Thực hiện hành vi quy định tại khoản 4 Điều này buộc phải tháo dỡ các vật che khuất biển báo hiệu đường bộ, đèn tín hiệu giao thông\"",
                "b) \"Thực hiện hành vi quy định tại điểm a khoản 10 Điều này buộc phải thu dọn đỉnh, vật sắc nhọn, dây hoặc các vật cản khác và khôi phục lại tình trạng ban đầu đã bị thay đổi do vi phạm hành chính gây ra\""
            ]
        },
        "dieu_12": {
            # Điều 12 - Vi phạm về trật tự, an toàn giao thông trên đường bộ
            "additional_penalties": [
                "a) \"Thực hiện hành vi quy định tại điểm b khoản 1 Điều này buộc phải thu dọn thóc, lúa, rơm, rạ, nông, lâm, hải sản, thiết bị trên đường bộ\"",
                "b) \"Thực hiện hành vi quy định tại điểm a, điểm b khoản 2 Điều này buộc phải di dời cây trồng không đúng quy định và khôi phục lại tình trạng ban đầu đã bị thay đổi do vi phạm hành chính gây ra\"",
                "c) \"Thực hiện hành vi quy định tại điểm c, điểm d khoản 2 Điều này buộc phải thu dọn vật tư, vật liệu, hàng hóa và khôi phục lại tình trạng ban đầu đã bị thay đổi do vi phạm hành chính gây ra\"",
                "d) \"Thực hiện hành vi quy định tại khoản 3; khoản 4; điểm b, điểm c, điểm d khoản 5; điểm a, điểm b, điểm c, điểm d, điểm e, điểm g, điểm h, điểm i khoản 6; khoản 7; điểm a khoản 8 Điều này buộc phải thu dọn rác, chất phế thải, phương tiện, vật tư, vật liệu, hàng hóa, máy móc, thiết bị, biển hiệu, biển quảng cáo, các loại vật dụng khác và khôi phục lại tình trạng ban đầu đã bị thay đổi do vi phạm hành chính gây ra\"",
                "đ) \"Thực hiện hành vi quy định tại điểm a khoản 5, điểm đ khoản 6, điểm b khoản 8, khoản 9 Điều này buộc phải tháo dỡ công trình xây dựng trái phép và khôi phục lại tình trạng ban đầu đã bị thay đổi do vi phạm hành chính gây ra\""
            ]
        },
        "dieu_13": {
            # Điều 13 - Vi phạm về bảo đảm trật tự, an toàn giao thông
            "additional_penalties": [
                "a) \"Thực hiện hành vi quy định tại điểm a, điểm b khoản 3; khoản 4; điểm a, điểm e khoản 5 Điều này bị tước quyền sử dụng Giấy phép lái xe từ 01 tháng đến 03 tháng\"",
                "b) \"Thực hiện hành vi quy định tại điểm a, điểm b khoản 2; khoản 3; điểm a khoản 4; khoản 5 Điều này buộc phải thực hiện ngay các biện pháp bảo đảm an toàn giao thông theo quy định\"",
                "c) \"Thực hiện hành vi quy định tại điểm d, điểm đ khoản 5 Điều này bị tịch thu Giấy chứng nhận, tem kiểm định an toàn kỹ thuật và bảo vệ môi trường, Giấy đăng ký xe, biển số không đúng quy định hoặc bị tẩy xóa; bị tước quyền sử dụng Giấy phép lái xe từ 01 tháng đến 03 tháng\"",
                "d) \"Thực hiện hành vi quy định tại điểm b, điểm c khoản 5 Điều này bị tịch thu phương tiện và bị tước quyền sử dụng Giấy phép lái xe từ 01 tháng đến 03 tháng\"",
                "đ) \"Thực hiện hành vi quy định tại điểm a khoản 4, điểm đ khoản 5 Điều này trong trường hợp không có Giấy đăng ký xe hoặc sử dụng Giấy đăng ký xe không do cơ quan có thẩm quyền cấp, không đúng số khung, số máy của xe hoặc bị tẩy xóa mà không chứng minh được nguồn gốc xuất xứ của phương tiện thì bị tịch thu phương tiện\""
            ]
        }
    }

def add_all_additional_penalties():
    """Add additional penalties to all relevant articles"""
    
    json_file = "data/raw/legal_documents/nghi_dinh_100_2019.json"
    backup_file = "data/raw/legal_documents/nghi_dinh_100_2019_backup_all_penalties.json"
    
    # Load existing JSON
    if not os.path.exists(json_file):
        print(f"❌ JSON file not found: {json_file}")
        return False
    
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Create backup
    with open(backup_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"✅ Created backup: {backup_file}")
    
    # Get additional penalties data
    penalties_data = get_additional_penalties_data()
    
    added_count = 0
    updated_articles = []
    
    # Process each article
    for article_key, penalties_info in penalties_data.items():
        if article_key in data.get("articles", {}):
            article = data["articles"][article_key]
            
            # Add to the last section or create a dedicated penalties section
            if "sections" in article:
                # Find if there's already additional_penalties or add to last section
                found_existing = False
                
                for section in article["sections"]:
                    if "additional_penalties" in section:
                        # Update existing
                        section["additional_penalties"] = penalties_info["additional_penalties"]
                        found_existing = True
                        break
                
                if not found_existing:
                    # Create new section for additional penalties
                    penalties_section = {
                        "section": "Hình thức phạt bổ sung",
                        "additional_penalties": penalties_info["additional_penalties"]
                    }
                    article["sections"].append(penalties_section)
                
                added_count += len(penalties_info["additional_penalties"])
                updated_articles.append(article_key)
                print(f"✅ Added {len(penalties_info['additional_penalties'])} additional penalties to {article_key}")
    
    # Update metadata
    if "document_info" in data:
        data["document_info"]["last_updated"] = datetime.now().strftime("%Y-%m-%d")
        data["document_info"]["update_source"] = f"Added comprehensive additional penalties to {len(updated_articles)} articles"
    
    # Save updated JSON
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Updated file: {json_file}")
    print(f"📊 Total additional penalties added: {added_count}")
    print(f"📄 Articles updated: {', '.join(updated_articles)}")
    
    return True

def show_comprehensive_structure():
    """Show comprehensive structure of additional penalties"""
    json_file = "data/raw/legal_documents/nghi_dinh_100_2019.json"
    
    if not os.path.exists(json_file):
        print(f"❌ JSON file not found: {json_file}")
        return
    
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print("\n📋 Comprehensive Additional Penalties Structure:")
    print("=" * 70)
    
    # Count and show all articles with additional penalties
    articles_with_penalties = []
    total_penalties = 0
    
    for article_key, article_data in data.get("articles", {}).items():
        if "sections" in article_data:
            for section in article_data["sections"]:
                if "additional_penalties" in section:
                    penalties_count = len(section["additional_penalties"])
                    articles_with_penalties.append({
                        "article": article_key,
                        "title": article_data.get("title", "N/A"),
                        "section": section.get("section", "N/A"),
                        "penalties_count": penalties_count
                    })
                    total_penalties += penalties_count
    
    print(f"📊 Total articles with additional penalties: {len(articles_with_penalties)}")
    print(f"📊 Total additional penalties: {total_penalties}")
    print()
    
    for item in articles_with_penalties:
        print(f"📄 {item['article'].upper()}: {item['title']}")
        print(f"   📊 {item['section']}: {item['penalties_count']} penalties")
        print()
    
    # Show sample from Điều 5
    if "dieu_5" in data.get("articles", {}):
        article_5 = data["articles"]["dieu_5"]
        
        for section in article_5.get("sections", []):
            if "additional_penalties" in section:
                print("📋 Sample - Điều 5 Additional Penalties:")
                print("=" * 50)
                print(f"📄 Article: {article_5.get('title', 'N/A')}")
                print(f"📊 Section: {section.get('section', 'N/A')}")
                
                if "additional_penalties" in section:
                    print(f"\n⚖️ Additional Penalties ({len(section['additional_penalties'])}):")
                    for i, penalty in enumerate(section["additional_penalties"][:3], 1):
                        # Truncate long penalties for display
                        display_penalty = penalty[:100] + "..." if len(penalty) > 100 else penalty
                        print(f"   {i}. {display_penalty}")
                    
                    if len(section["additional_penalties"]) > 3:
                        print(f"   ... và {len(section['additional_penalties']) - 3} penalties khác")
                break

if __name__ == "__main__":
    print("🚀 Adding Comprehensive Additional Penalties Structure")
    print("=" * 70)
    
    success = add_all_additional_penalties()
    
    if success:
        show_comprehensive_structure()
        print("\n✅ Successfully added comprehensive additional penalties structure!")
        print("\n📋 Summary:")
        print("   - Added additional penalties to multiple articles")
        print("   - Each article now has structured penalty information")
        print("   - Letter indicators (a, b, c, đ, e, g, h) are preserved")
        print("   - JSON structure maintains backward compatibility")
    else:
        print("\n❌ Failed to add additional penalties!")