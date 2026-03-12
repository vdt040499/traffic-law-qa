#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script để thêm cấu trúc điểm a, b, c, d và hình phạt bổ sung vào tất cả các điều 
trong file nghi_dinh_168_2024.json tương tự như file nghi_dinh_100_2019.json
"""

import json
import re
from pathlib import Path

def load_json_file(file_path):
    """Đọc file JSON"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json_file(file_path, data):
    """Lưu file JSON với định dạng đẹp"""
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def add_letter_points_to_violations(violations):
    """Thêm điểm a, b, c, d... vào danh sách vi phạm"""
    letters = ['a', 'b', 'c', 'd', 'đ', 'e', 'g', 'h', 'i', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'x', 'y', 'z']
    
    updated_violations = []
    for i, violation in enumerate(violations):
        if i < len(letters):
            letter = letters[i]
            # Nếu vi phạm chưa có điểm, thêm vào
            if not re.match(r'^[a-z][\)\)]', violation):
                updated_violation = f"{letter}) {violation}"
            else:
                updated_violation = violation
            updated_violations.append(updated_violation)
        else:
            updated_violations.append(violation)
    
    return updated_violations

def create_additional_penalties_for_dieu(dieu_key):
    """Tạo phần hình phạt bổ sung theo từng điều"""
    
    penalties_mapping = {
        "dieu_6": [
            "a) Thực hiện hành vi quy định tại điểm e khoản 5 Điều này bị tịch thu thiết bị phát tín hiệu ưu tiên lắp đặt, sử dụng trái quy định",
            "b) Thực hiện hành vi quy định tại điểm h, điểm i khoản 3; điểm a, điểm b, điểm c, điểm d, điểm đ, điểm g khoản 4; điểm a, điểm b, điểm c, điểm d, điểm đ, điểm e, điểm g, điểm i, điểm k, điểm n, điểm o khoản 5 Điều này bị trừ điểm giấy phép lái xe 02 điểm",
            "c) Thực hiện hành vi quy định tại điểm h khoản 5; khoản 6; điểm b khoản 7; điểm b, điểm c, điểm d khoản 9 Điều này bị trừ điểm giấy phép lái xe 04 điểm",
            "d) Thực hiện hành vi quy định tại điểm p khoản 5; điểm a, điểm c khoản 7; khoản 8 Điều này bị trừ điểm giấy phép lái xe 06 điểm",
            "đ) Thực hiện hành vi quy định tại điểm a khoản 9, khoản 10, điểm đ khoản 11 Điều này bị trừ điểm giấy phép lái xe 10 điểm",
            "e) Thực hiện hành vi quy định tại điểm a, điểm b, điểm c, điểm d khoản 11; khoản 13; khoản 14 Điều này bị tước quyền sử dụng giấy phép lái xe từ 22 tháng đến 24 tháng",
            "g) Thực hiện hành vi quy định tại khoản 12 Điều này bị tước quyền sử dụng giấy phép lái xe từ 10 tháng đến 12 tháng"
        ],
        "dieu_7": [
            "a) Thực hiện hành vi quy định tại điểm g khoản 4 Điều này bị tịch thu thiết bị phát tín hiệu ưu tiên lắp đặt, sử dụng trại quy định",
            "b) Thực hiện hành vi quy định tại điểm a, điểm b, điểm c, điểm đ, điểm i khoản 3; điểm a, điểm b, điểm c, điểm d, điểm đ, điểm g khoản 4; điểm a, điểm b, điểm c, điểm d, điểm đ khoản 5 Điều này bị trừ điểm giấy phép lái xe 02 điểm",
            "c) Thực hiện hành vi quy định tại điểm h khoản 3; điểm h khoản 4; điểm h khoản 5; khoản 6 Điều này bị trừ điểm giấy phép lái xe 04 điểm",
            "d) Thực hiện hành vi quy định tại khoản 7; khoản 8 Điều này bị trừ điểm giấy phép lái xe 06 điểm",
            "đ) Thực hiện hành vi quy định tại khoản 9 Điều này bị trừ điểm giây phép lái xe 10 điểm"
        ],
        "dieu_8": [
            "a) Thực hiện hành vi quy định tại điểm a, điểm b, điểm c khoản 2; điểm b, điểm c khoản 3 Điều này bị trừ điểm giấy phép lái xe 02 điểm",
            "b) Thực hiện hành vi quy định tại điểm a khoản 3; khoản 4 Điều này bị trừ điểm giấy phép lái xe 04 điểm",
            "c) Thực hiện hành vi quy định tại khoản 5 Điều này bị trừ điểm giấy phép lái xe 06 điểm"
        ]
    }
    
    return penalties_mapping.get(dieu_key, [])

def process_dieu(dieu_data, dieu_key):
    """Xử lý một điều để thêm cấu trúc mới"""
    # Cập nhật từng khoản với điểm a, b, c, d...
    updated_sections = []
    
    for section in dieu_data["sections"]:
        if "violations" in section:
            section["violations"] = add_letter_points_to_violations(section["violations"])
        updated_sections.append(section)
    
    # Thêm phần hình phạt bổ sung nếu có
    additional_penalties = create_additional_penalties_for_dieu(dieu_key)
    if additional_penalties:
        additional_penalties_section = {
            "section": "Hình thức phạt bổ sung", 
            "additional_penalties": additional_penalties
        }
        updated_sections.append(additional_penalties_section)
    
    dieu_data["sections"] = updated_sections
    return dieu_data

def main():
    """Hàm chính"""
    # Đường dẫn file
    file_path = Path("c:/Users/Mr Hieu/Documents/vietnamese-traffic-law-qa/data/raw/legal_documents/nghi_dinh_168_2024.json")
    
    print(f"Đang xử lý file: {file_path}")
    
    # Đọc file JSON
    data = load_json_file(file_path)
    
    # Danh sách các điều cần xử lý
    dieu_keys = ["dieu_7", "dieu_8", "dieu_9", "dieu_10", "dieu_11", "dieu_12", "dieu_13", "dieu_14", "dieu_15"]
    
    for dieu_key in dieu_keys:
        if dieu_key in data.get("key_articles", {}):
            print(f"Đang cập nhật cấu trúc {dieu_key.replace('_', ' ').title()}...")
            data["key_articles"][dieu_key] = process_dieu(data["key_articles"][dieu_key], dieu_key)
            print(f"✓ Đã cập nhật {dieu_key.replace('_', ' ').title()}")
    
    # Lưu file
    save_json_file(file_path, data)
    print(f"✓ Đã lưu file: {file_path}")
    print("Hoàn thành cập nhật cấu trúc cho tất cả các điều!")

if __name__ == "__main__":
    main()