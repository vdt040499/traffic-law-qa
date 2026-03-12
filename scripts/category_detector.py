#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ALL-IN-ONE Category Detection and Processing System
Merges all categorization functionality into a single script
"""

import json
import re
import os
import hashlib
from datetime import datetime
from collections import Counter

class VehicleCategoryDetector:
    """Enhanced vehicle type and category detection system"""
    
    def __init__(self):
        self.vehicle_patterns = {
            # Primary vehicle types
            "Xe ô tô": {
                "keywords": ["ô tô", "xe hơi", "car", "xe con"],
                "patterns": [r"xe\s+ô\s+tô", r"ô\s+tô", r"xe\s+hơi"],
                "priority": 10
            },
            "Xe mô tô, xe máy": {
                "keywords": ["mô tô", "xe máy", "xe gắn máy", "motorbike", "motorcycle"],
                "patterns": [r"xe\s+mô\s+tô", r"mô\s+tô", r"xe\s+máy", r"xe\s+gắn\s+máy"],
                "priority": 10
            },
            "Xe thô sơ": {
                "keywords": ["xe thô sơ", "xe bò", "sức người", "sức súc vật", "súc vật"],
                "patterns": [r"xe\s+thô\s+sơ", r"xe\s+bò", r"sức\s+người", r"sức\s+súc\s+vật", r"súc\s+vật"],
                "priority": 10
            },
            
            # Commercial vehicles
            "Xe khách, xe buýt": {
                "keywords": ["xe khách", "xe buýt", "xe bus", "bus", "buýt"],
                "patterns": [r"xe\s+khách", r"xe\s+buýt", r"xe\s+bus"],
                "priority": 9
            },
            "Xe tải, container": {
                "keywords": ["xe tải", "container", "xe container", "tải"],
                "patterns": [r"xe\s+tải", r"container"],
                "priority": 9
            },
            "Rơ moóc, sơ mi rơ moóc": {
                "keywords": ["rơ moóc", "moóc", "sơ mi rơ moóc", "trailer"],
                "patterns": [r"rơ\s+moóc", r"sơ\s+mi\s+rơ\s+moóc"],
                "priority": 9
            },
            
            # Special vehicles
            "Xe chuyên dụng": {
                "keywords": ["cứu thương", "cứu hỏa", "xe cứu", "xe cẩu", "xe ben", "xe bồn", "chuyên dụng"],
                "patterns": [r"cứu\s+thương", r"cứu\s+hỏa", r"xe\s+cứu", r"xe\s+cẩu", r"xe\s+ben", r"xe\s+bồn", r"chuyên\s+dụng"],
                "priority": 9
            },
            "Taxi, xe du lịch": {
                "keywords": ["taxi", "xe taxi", "xe du lịch", "du lịch"],
                "patterns": [r"taxi", r"xe\s+taxi", r"xe\s+du\s+lịch"],
                "priority": 8
            },
            
            # Other vehicles
            "Xe đạp": {
                "keywords": ["xe đạp", "bicycle", "bike", "đạp xe"],
                "patterns": [r"xe\s+đạp", r"đạp\s+xe"],
                "priority": 8
            },
            "Người đi bộ": {
                "keywords": ["người đi bộ", "pedestrian", "đi bộ"],
                "patterns": [r"người\s+đi\s+bộ", r"đi\s+bộ"],
                "priority": 8
            },
            "Xe lăn": {
                "keywords": ["xe lăn", "wheelchair", "người khuyết tật"],
                "patterns": [r"xe\s+lăn", r"người\s+khuyết\s+tật"],
                "priority": 8
            },
            
            # Railway and water transport
            "Tàu hỏa, đường sắt": {
                "keywords": ["tàu hỏa", "đường sắt", "railway", "train", "tàu lửa", "toa tàu"],
                "patterns": [r"tàu\s+hỏa", r"đường\s+sắt", r"tàu\s+lửa", r"toa\s+tàu"],
                "priority": 9
            },
            "Tàu thủy, thuyền": {
                "keywords": ["tàu thủy", "thuyền", "boat", "ship", "thủy"],
                "patterns": [r"tàu\s+thủy", r"thuyền"],
                "priority": 8
            },
            
            # Electric and special transport
            "Xe điện": {
                "keywords": ["xe điện", "tram", "xe buýt điện", "xe máy điện"],
                "patterns": [r"xe\s+điện", r"xe\s+buýt\s+điện", r"xe\s+máy\s+điện"],
                "priority": 8
            },
            "Máy kéo": {
                "keywords": ["máy kéo", "tractor"],
                "patterns": [r"máy\s+kéo"],
                "priority": 8
            }
        }
        
        # Business and administrative patterns
        self.business_patterns = {
            "Kinh doanh vận tải": {
                "keywords": ["kinh doanh vận tải", "vận tải", "kinh doanh", "doanh nghiệp vận tải"],
                "patterns": [r"kinh\s+doanh\s+vận\s+tải", r"doanh\s+nghiệp\s+vận\s+tải"],
                "priority": 9
            },
            "Đào tạo lái xe": {
                "keywords": ["đào tạo", "học lái xe", "trung tâm đào tạo", "cơ sở đào tạo"],
                "patterns": [r"đào\s+tạo", r"học\s+lái\s+xe", r"trung\s+tâm\s+đào\s+tạo", r"cơ\s+sở\s+đào\s+tạo"],
                "priority": 9
            },
            "Sát hạch lái xe": {
                "keywords": ["sát hạch", "thi bằng lái", "kiểm tra lái xe"],
                "patterns": [r"sát\s+hạch", r"thi\s+bằng\s+lái", r"kiểm\s+tra\s+lái\s+xe"],
                "priority": 9
            }
        }
        
        # Fallback categories
        self.fallback_categories = {
            "Vi phạm giấy tờ": ["giấy phép", "bằng lái", "đăng ký", "chứng nhận"],
            "Vi phạm tốc độ": ["tốc độ", "chạy quá", "km/h", "vượt tốc độ"],
            "Vi phạm tín hiệu giao thông": ["đèn đỏ", "tín hiệu", "hiệu lệnh", "biển báo"],
            "Vi phạm về rượu bia": ["rượu", "bia", "cồn", "nồng độ cồn"],
            "Sử dụng điện thoại": ["điện thoại", "di động", "phone"],
            "Vi phạm dừng đỗ xe": ["dừng xe", "đỗ xe", "parking"],
            "Vi phạm mũ bảo hiểm": ["mũ bảo hiểm", "helmet"],
            "Vi phạm dây an toàn": ["dây an toàn", "thắt dây", "seat belt"],
            "Vi phạm chở người/hàng": ["chở người", "chở hàng", "quá tải", "overload"],
            "Vi phạm vượt xe": ["vượt xe", "vượt", "overtaking"],
            "Quản lý nhà nước": ["cơ quan", "thanh tra", "kiểm tra", "quản lý nhà nước"]
        }
    
    def detect_category(self, text, article_title="", article_number="", using_fallback=True):
        """Detect category for a violation text"""
        combined_text = f"{text} {article_title}".lower()
        
        # Combine all patterns
        all_patterns = {**self.vehicle_patterns, **self.business_patterns}
        
        detected_types = []
        
        # Check each pattern
        for category_type, config in all_patterns.items():
            score = 0
            
            # Check keywords
            for keyword in config["keywords"]:
                if keyword in combined_text:
                    score += 1
            
            # Check regex patterns
            for pattern in config.get("patterns", []):
                if re.search(pattern, combined_text):
                    score += 2
            
            if score > 0:
                detected_types.append({
                    "type": category_type,
                    "score": score * config["priority"],
                    "priority": config["priority"]
                })
        
        # Sort by score and priority
        detected_types.sort(key=lambda x: (x["score"], x["priority"]), reverse=True)
        
        # Return the highest scoring type, or fallback categories
        if detected_types:
            return detected_types[0]["type"]
        
        # Check fallback categories
        if using_fallback:
            for category, keywords in self.fallback_categories.items():
                if any(keyword in combined_text for keyword in keywords):
                    return category
        
            return "Vi phạm khác"
        else:
            return None

class ViolationProcessor:
    """Process violations from raw to categorized format"""
    
    def __init__(self):
        self.detector = VehicleCategoryDetector()
        self.raw_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "raw", "legal_documents", "nghi_dinh_100_2019.json")
        self.processed_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "processed", "violations_100.json")
    
    def clean_text(self, text):
        """Clean and normalize text"""
        if not text:
            return ""
        
        text = re.sub(r'\s+', ' ', text).strip()
        text = re.sub(r'[^\w\s\-.,():;/]', '', text)
        return text
    
    def extract_fine_amounts(self, fine_range):
        """Extract min and max fine amounts from fine range string"""
        if not fine_range:
            return 0, 0, ""
        
        fine_text = fine_range.replace('VNĐ', '').strip()
        numbers = re.findall(r'(\d+(?:[.,]\d{3})*)', fine_text)
        
        if not numbers:
            return 0, 0, fine_range
        
        amounts = []
        for num in numbers:
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
    
    def get_severity_level(self, fine_min, fine_max):
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
    
    def extract_keywords(self, violation_text):
        """Extract keywords for search"""
        keywords = []
        text_lower = violation_text.lower()
        
        keyword_patterns = [
            "tốc độ", "đèn đỏ", "rượu bia", "điện thoại", "mũ bảo hiểm",
            "dây an toàn", "giấy phép", "vượt xe", "dừng xe", "đỗ xe",
            "chở người", "chở hàng", "ngược chiều", "lấn làn"
        ]
        
        for keyword in keyword_patterns:
            if keyword in text_lower:
                keywords.append(keyword)
        
        return keywords
    
    def create_violation_hash(self, violation_text, article, section):
        """Create hash for duplicate detection"""
        content = f"{violation_text}_{article}_{section}".lower()
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    def process_raw_to_violations(self):
        """Main processing function from raw to violations"""
        
        print("🔄 Processing raw legal documents to categorized violations...")
        
        # Load raw data
        try:
            with open(self.raw_path, 'r', encoding='utf-8') as f:
                raw_data = json.load(f)
        except Exception as e:
            print(f"❌ Error loading raw data: {e}")
            return False
        
        processed_violations = []
        seen_hashes = set()
        violation_id = 1
        category_stats = Counter()
        
        # Process each article
        for article_key, article_data in raw_data.get('key_articles', {}).items():
            if not isinstance(article_data, dict) or 'sections' not in article_data:
                continue
            
            article_title = article_data.get('title', '')
            article_number = article_key.replace('dieu_', '')
            
            # Process each section
            for section in article_data.get('sections', []):
                if not isinstance(section, dict):
                    continue
                
                section_name = section.get('section', '')
                fine_range = section.get('fine_range', '')
                additional_measures = section.get('additional_measures', [])
                
                # Extract fine amounts
                fine_min, fine_max, fine_text = self.extract_fine_amounts(fine_range)
                
                # Skip if no valid fine amount and no additional measures
                if fine_min == 0 and fine_max == 0 and not additional_measures:
                    continue
                
                # Process each violation
                for violation_text in section.get('violations', []):
                    if not violation_text or not violation_text.strip():
                        continue
                    
                    violation_text = self.clean_text(violation_text)
                    
                    if len(violation_text) < 10:
                        continue
                    
                    # Check for duplicates
                    violation_hash = self.create_violation_hash(violation_text, f"Điều {article_number}", section_name)
                    if violation_hash in seen_hashes:
                        continue
                    seen_hashes.add(violation_hash)
                    
                    # Detect category
                    category = self.detector.detect_category(violation_text, article_title, article_number)
                    
                    # Skip uncategorized violations with no penalty
                    if category == "Vi phạm khác" and fine_min == 0 and fine_max == 0:
                        continue
                    
                    # Create violation record
                    violation_record = {
                        "id": violation_id,
                        "description": violation_text,
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
                            "document": "Nghị định 100/2019/NĐ-CP",
                            "full_reference": f"Nghị định 100/2019/NĐ-CP, Điều {article_number}, {section_name}"
                        },
                        "severity": self.get_severity_level(fine_min, fine_max),
                        "keywords": self.extract_keywords(violation_text),
                        "search_text": f"{violation_text} {category} Điều {article_number} {article_title}",
                        "metadata": {
                            "source": "ND100-2019.docx",
                            "processed_date": datetime.now().isoformat()
                        }
                    }
                    
                    processed_violations.append(violation_record)
                    category_stats[category] += 1
                    violation_id += 1
        
        # Create final output
        output_data = {
            "metadata": {
                "total_violations": len(processed_violations),
                "processed_date": datetime.now().isoformat(),
                "source_documents": ["Nghị định 100/2019/NĐ-CP"],
                "data_sources": [self.raw_path],
                "processing_pipeline": "raw->processed (enhanced_direct)",
                "validation_summary": {
                    "total_violations": len(processed_violations),
                    "valid_legal_references": len(processed_violations),
                    "duplicates_removed": len(seen_hashes) - len(processed_violations),
                    "categories": len(category_stats)
                },
                "categories": list(category_stats.keys()),
                "severity_levels": list(set(v["severity"] for v in processed_violations))
            },
            "violations": processed_violations
        }
        
        # Save processed data
        try:
            # Backup existing file if it exists
            if os.path.exists(self.processed_path):
                backup_path = self.processed_path.replace(".json", f"_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
                os.rename(self.processed_path, backup_path)
                print(f"📦 Backed up existing file to: {os.path.basename(backup_path)}")
            
            with open(self.processed_path, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, ensure_ascii=False, indent=2)
            
            print(f"✅ Successfully processed {len(processed_violations)} violations")
            print(f"📊 Categories detected: {len(category_stats)}")
            
            # Show category breakdown
            print(f"\n📋 Category breakdown:")
            for category, count in sorted(category_stats.items(), key=lambda x: x[1], reverse=True):
                percentage = (count / len(processed_violations)) * 100
                print(f"   {category}: {count} ({percentage:.1f}%)")
            
            return True
            
        except Exception as e:
            print(f"❌ Error saving processed data: {e}")
            return False

class CategoryAnalyzer:
    """Analyze and report on categorization results"""
    
    def __init__(self, processed_path):
        self.processed_path = processed_path
    
    def analyze_results(self):
        """Analyze categorization results"""
        
        try:
            with open(self.processed_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            print(f"❌ Error loading processed data: {e}")
            return
        
        violations = data.get('violations', [])
        metadata = data.get('metadata', {})
        
        print(f"\n📊 CATEGORIZATION ANALYSIS REPORT")
        print("=" * 50)
        print(f"📄 Total violations: {len(violations)}")
        print(f"📅 Processed: {metadata.get('processed_date', 'Unknown')}")
        print(f"🔄 Method: {metadata.get('categorization_method', 'Unknown')}")
        
        categories = Counter(v.get('category') for v in violations)
        
        # Separate vehicle vs other categories
        vehicle_categories = {}
        other_categories = {}
        
        for category, count in categories.items():
            if any(vehicle in category.lower() for vehicle in [
                'xe ô tô', 'xe mô tô', 'xe máy', 'xe thô sơ', 'xe đạp', 
                'người đi bộ', 'xe lăn', 'tàu hỏa', 'đường sắt', 'xe điện',
                'xe tải', 'xe khách', 'xe buýt', 'taxi', 'rơ moóc', 'tàu thủy'
            ]):
                vehicle_categories[category] = count
            else:
                other_categories[category] = count
        
        print(f"\n🚗 Vehicle-specific categories ({len(vehicle_categories)} types):")
        for category, count in sorted(vehicle_categories.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / len(violations)) * 100
            print(f"   {category}: {count} ({percentage:.1f}%)")
        
        print(f"\n📋 Other categories ({len(other_categories)} types):")
        for category, count in sorted(other_categories.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / len(violations)) * 100
            print(f"   {category}: {count} ({percentage:.1f}%)")
        
        # Summary statistics
        total_vehicle = sum(vehicle_categories.values())
        total_other = sum(other_categories.values())
        
        print(f"\n📈 Summary:")
        print(f"   🚗 Vehicle-specific: {total_vehicle} ({(total_vehicle/len(violations)*100):.1f}%)")
        print(f"   📋 Other violations: {total_other} ({(total_other/len(violations)*100):.1f}%)")
        print(f"   🏷️  Total categories: {len(categories)}")
        
        return {
            'total_violations': len(violations),
            'vehicle_categories': len(vehicle_categories),
            'other_categories': len(other_categories),
            'vehicle_percentage': (total_vehicle/len(violations)*100)
        }

def main():
    """Main function to run the complete categorization process"""
    
    print("🚗 ENHANCED CATEGORY DETECTION SYSTEM")
    print("=" * 60)
    print("🔄 Processing raw legal documents → categorized violations")
    
    # Initialize processor
    processor = ViolationProcessor()
    
    # Process raw data to violations
    success = processor.process_raw_to_violations()
    
    if success:
        # Analyze results
        analyzer = CategoryAnalyzer(processor.processed_path)
        stats = analyzer.analyze_results()
        
        print(f"\n🎉 CATEGORIZATION COMPLETED SUCCESSFULLY!")
        print("=" * 50)
        print(f"✅ {stats['total_violations']} violations processed and categorized")
        print(f"🚗 {stats['vehicle_categories']} vehicle-specific categories detected")
        print(f"📋 {stats['other_categories']} other categories detected")
        print(f"🎯 {stats['vehicle_percentage']:.1f}% are vehicle-specific violations")
        
        print(f"\n📁 Output saved to: data/processed/violations_100.json")
        print(f"🔍 Ready for Q&A system usage!")
    else:
        print(f"\n❌ Categorization failed. Please check the error messages above.")

if __name__ == "__main__":
    main()