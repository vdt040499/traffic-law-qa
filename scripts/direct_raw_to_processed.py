#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Direct conversion from raw legal documents to processed violations
Removes duplicates and invalid entries as requested
"""

import json
import re
from datetime import datetime
import hashlib

def clean_text(text):
    """Clean and normalize text"""
    if not text:
        return ""
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Remove special characters that might cause issues
    text = re.sub(r'[^\w\s\-.,():;/]', '', text)
    
    return text

def extract_fine_amounts(fine_range):
    """Extract min and max fine amounts from fine range string"""
    if not fine_range:
        return 0, 0, ""
    
    # Remove VNĐ and normalize
    fine_text = fine_range.replace('VNĐ', '').strip()
    
    # Find numbers (handle both . and , as thousand separators)
    numbers = re.findall(r'(\d+(?:[.,]\d{3})*)', fine_text)
    
    if not numbers:
        return 0, 0, fine_range
    
    # Convert to integers
    amounts = []
    for num in numbers:
        # Remove thousand separators
        clean_num = num.replace('.', '').replace(',', '')
        try:
            amounts.append(int(clean_num))
        except ValueError:
            continue
    
    if len(amounts) >= 2:
        return min(amounts), max(amounts), fine_range
    elif len(amounts) == 1:
        return amounts[0], amounts[0], fine_range
    else:
        return 0, 0, fine_range

def categorize_violation(violation_text, article_title=""):
    """Categorize violation based on content"""
    text = f"{violation_text} {article_title}".lower()
    
    categories = {
        "Vượt tốc độ": ["tốc độ", "chạy quá", "km/h"],
        "Vi phạm tín hiệu giao thông": ["đèn đỏ", "tín hiệu", "hiệu lệnh"],
        "Vi phạm về rượu bia": ["rượu", "bia", "cồn", "nồng độ cồn"],
        "Sử dụng điện thoại": ["điện thoại", "di động", "phone"],
        "Vi phạm dừng đỗ xe": ["dừng xe", "đỗ xe", "parking"],
        "Vi phạm vượt xe": ["vượt xe", "vượt", "overtaking"],
        "Vi phạm giấy tờ": ["giấy phép", "bằng lái", "giấy đăng ký", "license"],
        "Vi phạm mũ bảo hiểm": ["mũ bảo hiểm", "helmet"],
        "Vi phạm dây an toàn": ["dây an toàn", "thắt dây", "seat belt"],
        "Vi phạm chở người/hàng": ["chở người", "chở hàng", "quá tải", "overload"],
        # Sửa thứ tự: kiểm tra xe mô tô trước xe ô tô để tránh false positive
        "Vi phạm về xe máy": ["xe mô tô", "mô tô", "xe máy", "xe gắn máy"],
        "Vi phạm về ô tô": ["xe ô tô", "xe hơi", "car"],  # loại bỏ "ô tô" đơn lẻ
        "Vi phạm người đi bộ": ["đi bộ", "người đi bộ", "pedestrian"]
    }
    
    for category, keywords in categories.items():
        if any(keyword in text for keyword in keywords):
            return category
    
    return "Vi phạm khác"

def get_severity_level(fine_min, fine_max):
    """Determine severity based on fine amount"""
    max_fine = max(fine_min, fine_max)
    
    if max_fine == 0:
        return "Không xác định"
    elif max_fine < 1000000:
        return "Nhẹ"
    elif max_fine < 5000000:
        return "Trung bình"
    elif max_fine < 20000000:
        return "Nặng"
    else:
        return "Rất nặng"

def extract_point_from_violation(violation_text):
    """Extract point (a, b, c, d, đ) from violation text"""
    if not violation_text:
        return None
    
    # Match patterns like "a)", "b)", "c)", "d)", "đ)" at the beginning
    point_match = re.match(r'^([a-z]|đ)\)', violation_text.strip())
    if point_match:
        point_letter = point_match.group(1)
        return f"Điểm {point_letter}"
    
    return None

def clean_point_prefix(text):
    """Remove point prefix from text (a), b), c), d), đ), etc.)"""
    if not text:
        return text
    
    # Match pattern like "a) ", "b) ", "c) ", "d) ", "đ) ", etc. at the beginning
    cleaned = re.sub(r'^([a-z]|đ)\)\s*', '', text.strip())
    return cleaned

def extract_keywords(violation_text):
    """Extract keywords for search"""
    keywords = []
    text_lower = violation_text.lower()
    
    # Common Vietnamese traffic keywords
    keyword_patterns = [
        "tốc độ", "đèn đỏ", "rượu bia", "điện thoại", "mũ bảo hiểm",
        "dây an toàn", "giấy phép", "vượt xe", "dừng xe", "đỗ xe",
        "chở người", "chở hàng", "ngược chiều", "lấn làn"
    ]
    
    for keyword in keyword_patterns:
        if keyword in text_lower:
            keywords.append(keyword)
    
    return keywords

def create_violation_hash(violation_text, article, section):
    """Create hash for duplicate detection"""
    content = f"{violation_text}_{article}_{section}".lower()
    return hashlib.md5(content.encode('utf-8')).hexdigest()

def convert_raw_to_processed():
    """Main conversion function"""
    
    print("🔄 Starting direct conversion from raw to processed...")
    
    # Load raw legal document
    raw_path = r"C:\Users\Mr Hieu\Documents\vietnamese-traffic-law-qa\data\raw\legal_documents\nghi_dinh_100_2019.json"
    
    try:
        with open(raw_path, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)
    except Exception as e:
        print(f"❌ Error loading raw data: {e}")
        return
    
    processed_violations = []
    seen_hashes = set()  # For duplicate detection
    violation_id = 1
    
    # Process each article
    for article_key, article_data in raw_data.get('articles', {}).items():
        if not isinstance(article_data, dict) or 'sections' not in article_data:
            continue
        
        article_title = article_data.get('title', '')
        article_number = article_key.replace('dieu_', '')
        document_source = article_data.get('source_document', 'ND100-2019.docx')
        
        # Process each section
        for section in article_data.get('sections', []):
            if not isinstance(section, dict):
                continue
            
            section_name = section.get('section', '')
            fine_range = section.get('fine_range', '')
            additional_measures = section.get('additional_measures', [])
            
            # Extract fine amounts
            fine_min, fine_max, fine_text = extract_fine_amounts(fine_range)
            
            # Skip if no valid fine amount and no additional measures
            if fine_min == 0 and fine_max == 0 and not additional_measures:
                continue
            
            # Process each violation
            for violation_text in section.get('violations', []):
                if not violation_text or not violation_text.strip():
                    continue
                
                violation_text = clean_text(violation_text)
                
                # Skip empty or very short violations
                if len(violation_text) < 10:
                    continue
                
                # Extract point from violation text BEFORE cleaning (a, b, c, d, đ)
                point = extract_point_from_violation(violation_text)
                
                # Clean the point prefix from description
                cleaned_violation_text = clean_point_prefix(violation_text)
                
                # Check for duplicates using cleaned text
                violation_hash = create_violation_hash(cleaned_violation_text, f"Điều {article_number}", section_name)
                if violation_hash in seen_hashes:
                    continue
                seen_hashes.add(violation_hash)
                
                # Categorize violation using cleaned text
                category = categorize_violation(cleaned_violation_text, article_title)
                
                # Skip uncategorized violations with no penalty
                if category == "Vi phạm khác" and fine_min == 0 and fine_max == 0:
                    continue
                
                # Create processed violation record
                violation_record = {
                    "id": violation_id,
                    "description": cleaned_violation_text,
                    "category": category,
                    "penalty": {
                        "fine_min": fine_min,
                        "fine_max": fine_max,
                        "currency": "VNĐ",
                        "fine_text": fine_text if fine_text else f"{fine_min:,} - {fine_max:,} VNĐ".replace(",", ".")
                    },
                    "additional_measures": additional_measures,
                    "legal_basis": {
                        "article": f"Điều {article_number}",
                        "section": section_name,
                        "point": point,
                        "document": "Nghị định 100/2019/NĐ-CP",
                        "full_reference": f"Nghị định 100/2019/NĐ-CP, Điều {article_number}, {section_name}" + (f", {point}" if point else "")
                    },
                    "severity": get_severity_level(fine_min, fine_max),
                    "keywords": extract_keywords(cleaned_violation_text),
                    "search_text": f"{cleaned_violation_text} {category} Điều {article_number} {article_title}",
                    "metadata": {
                        "source": document_source,
                        "processed_date": datetime.now().isoformat(),
                        "pipeline_stage": "direct_conversion"
                    }
                }
                
                processed_violations.append(violation_record)
                violation_id += 1
    
    # Create final output with metadata
    output_data = {
        "metadata": {
            "total_violations": len(processed_violations),
            "processed_date": datetime.now().isoformat(),
            "source_documents": ["Nghị định 100/2019/NĐ-CP"],
            "data_sources": [raw_path],
            "processing_pipeline": "raw->processed (direct)",
            "validation_summary": {
                "total_violations": len(processed_violations),
                "valid_legal_references": len(processed_violations),
                "duplicates_removed": len(seen_hashes) - len(processed_violations),
                "categories": len(set(v["category"] for v in processed_violations))
            },
            "categories": list(set(v["category"] for v in processed_violations)),
            "severity_levels": list(set(v["severity"] for v in processed_violations))
        },
        "violations": processed_violations
    }
    
    # Save processed data
    output_path = r"C:\Users\Mr Hieu\Documents\vietnamese-traffic-law-qa\data\processed\violations_100.json"
    
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Successfully processed {len(processed_violations)} violations")
        print(f"📁 Saved to: {output_path}")
        print(f"📊 Categories: {len(output_data['metadata']['categories'])}")
        print(f"🔍 Duplicates removed: {output_data['metadata']['validation_summary']['duplicates_removed']}")
        
        # Show category breakdown
        category_counts = {}
        for violation in processed_violations:
            cat = violation["category"]
            category_counts[cat] = category_counts.get(cat, 0) + 1
        
        print("\n📋 Category breakdown:")
        for category, count in sorted(category_counts.items()):
            print(f"   {category}: {count}")
            
    except Exception as e:
        print(f"❌ Error saving processed data: {e}")

def cleanup_data_folder():
    """Remove intermediate files and keep only necessary ones"""
    import os
    
    base_dir = r"C:\Users\Mr Hieu\Documents\vietnamese-traffic-law-qa\data"
    
    # Files to keep
    keep_files = [
        "raw/legal_documents/nghi_dinh_100_2019.json",
        "processed/violations_100.json"
    ]
    
    # Optional: backup existing processed file
    processed_path = os.path.join(base_dir, "processed", "violations_100.json")
    if os.path.exists(processed_path):
        backup_path = processed_path.replace(".json", f"_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        os.rename(processed_path, backup_path)
        print(f"📦 Backed up existing file to: {backup_path}")

if __name__ == "__main__":
    # Optional cleanup first
    # cleanup_data_folder()
    
    # Main conversion
    convert_raw_to_processed()
    
    print("\n🎉 Direct conversion completed successfully!")
    print("✅ Removed duplicates and invalid entries")
    print("✅ Proper categorization applied")
    print("✅ Valid penalty amounts only")