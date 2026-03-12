#!/usr/bin/env python3
"""
Script để cập nhật lại ID của violations để liên tục từ 1 trở đi
"""

import json
from datetime import datetime
import os

def main():
    # Đường dẫn file
    violations_file = r"c:\Users\Mr Hieu\Documents\vietnamese-traffic-law-qa\data\processed\violations_100.json"
    backup_file = violations_file + ".backup_before_reindex"
    
    # Backup file gốc
    if os.path.exists(violations_file):
        with open(violations_file, 'r', encoding='utf-8') as f:
            original_data = json.load(f)
        
        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(original_data, f, ensure_ascii=False, indent=2)
        print(f"✓ Đã backup file gốc: {backup_file}")
    else:
        print(f"❌ Không tìm thấy file: {violations_file}")
        return
    
    # Cập nhật ID
    violations = original_data["violations"]
    old_ids = [v["id"] for v in violations]
    
    print(f"Cập nhật ID cho {len(violations)} violations...")
    print(f"ID ban đầu: {old_ids[:10]}{'...' if len(old_ids) > 10 else ''}")
    
    # Đánh số lại từ 1
    for i, violation in enumerate(violations, 1):
        old_id = violation["id"]
        violation["id"] = i
        if i <= 10:  # In ra 10 ID đầu tiên để kiểm tra
            print(f"  {old_id} -> {i}")
    
    # Cập nhật metadata
    updated_data = original_data.copy()
    updated_data["violations"] = violations
    updated_data["metadata"]["processed_date"] = datetime.now().isoformat()
    updated_data["metadata"]["processing_pipeline"] += " -> id_reindexed"
    
    # Thêm thông tin về việc đánh số lại ID
    if "id_reindex" not in updated_data["metadata"]:
        updated_data["metadata"]["id_reindex"] = {}
    
    updated_data["metadata"]["id_reindex"] = {
        "applied_date": datetime.now().isoformat(),
        "description": "Đánh số lại ID của violations liên tục từ 1",
        "old_id_range": f"{min(old_ids)}-{max(old_ids)}",
        "new_id_range": f"1-{len(violations)}",
        "total_violations": len(violations)
    }
    
    # Lưu file đã cập nhật
    with open(violations_file, 'w', encoding='utf-8') as f:
        json.dump(updated_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✓ Đã cập nhật lại ID của violations")
    print(f"  - Tổng số violations: {len(violations)}")
    print(f"  - ID cũ: {min(old_ids)} - {max(old_ids)}")
    print(f"  - ID mới: 1 - {len(violations)}")
    print(f"  - File backup: {backup_file}")

if __name__ == "__main__":
    main()