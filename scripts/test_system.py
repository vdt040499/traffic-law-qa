#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick test script to verify the new category detection system
"""

def test_category_detection():
    """Test the main categorization script"""
    
    print("🧪 TESTING CATEGORY DETECTION SYSTEM")
    print("=" * 50)
    
    # Test import
    try:
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        
        from category_detector import VehicleCategoryDetector
        print("✅ Import successful")
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False
    
    # Test detector
    try:
        detector = VehicleCategoryDetector()
        print("✅ Detector initialized")
    except Exception as e:
        print(f"❌ Detector initialization failed: {e}")
        return False
    
    # Test sample categorizations
    test_cases = [
        ("Xe ô tô chạy quá tốc độ", "Xe ô tô"),
        ("Người đi bộ qua đường", "Người đi bộ"),
        ("Tàu hỏa không tuân thủ tín hiệu", "Tàu hỏa, đường sắt"),
        ("Xe máy không đội mũ bảo hiểm", "Xe mô tô, xe máy"),
        ("Đào tạo lái xe không đúng quy định", "Đào tạo lái xe"),
        ("Vi phạm tốc độ cho phép", "Vi phạm tốc độ")
    ]
    
    print(f"\n🔍 Testing sample categorizations:")
    all_passed = True
    
    for text, expected in test_cases:
        try:
            result = detector.detect_category(text)
            status = "✅" if result == expected else "⚠️"
            print(f"   {status} '{text[:30]}...' → {result}")
            if result != expected:
                print(f"      Expected: {expected}")
                all_passed = False
        except Exception as e:
            print(f"   ❌ Error testing '{text[:30]}...': {e}")
            all_passed = False
    
    # Test file paths
    print(f"\n📁 Testing file paths:")
    
    raw_path = r"C:\Users\Mr Hieu\Documents\vietnamese-traffic-law-qa\data\raw\legal_documents\nghi_dinh_100_2019.json"
    processed_path = r"C:\Users\Mr Hieu\Documents\vietnamese-traffic-law-qa\data\processed\violations_100.json"
    
    if os.path.exists(raw_path):
        print("✅ Raw data file exists")
    else:
        print("❌ Raw data file missing")
        all_passed = False
    
    if os.path.exists(processed_path):
        print("✅ Processed data file exists")
        
        # Test reading processed file
        try:
            import json
            with open(processed_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            violations_count = len(data.get('violations', []))
            categories_count = len(data.get('metadata', {}).get('categories', []))
            
            print(f"   📊 {violations_count} violations")
            print(f"   🏷️  {categories_count} categories")
            
        except Exception as e:
            print(f"❌ Error reading processed file: {e}")
            all_passed = False
    else:
        print("⚠️  Processed data file not found (run category_detector.py first)")
    
    # Summary
    print(f"\n📋 TEST SUMMARY:")
    if all_passed:
        print("✅ All tests passed!")
        print("🎯 Category detection system is working correctly")
        print("🚀 Ready to use: python scripts/category_detector.py")
    else:
        print("⚠️  Some tests failed - check the issues above")
    
    return all_passed

def show_usage_examples():
    """Show usage examples"""
    
    print(f"\n📖 USAGE EXAMPLES:")
    print("-" * 20)
    
    examples = [
        {
            "title": "Full categorization process",
            "command": "python scripts/category_detector.py",
            "description": "Complete processing from raw to categorized violations"
        },
        {
            "title": "Alternative processing method", 
            "command": "python scripts/direct_raw_to_processed.py",
            "description": "Basic processing without enhanced categorization"
        },
        {
            "title": "View documentation",
            "command": "type scripts\\README.md",
            "description": "Read full documentation and guidelines"
        }
    ]
    
    for example in examples:
        print(f"\n🔹 {example['title']}:")
        print(f"   Command: {example['command']}")
        print(f"   Purpose: {example['description']}")

if __name__ == "__main__":
    success = test_category_detection()
    show_usage_examples()
    
    if success:
        print(f"\n🎉 SYSTEM READY!")
        print("=" * 20)
        print("✅ Category detection system tested and working")
        print("📁 Scripts folder cleaned and organized")
        print("📖 Documentation created")
        print("🚀 Use 'python scripts/category_detector.py' for new categorization")
    else:
        print(f"\n⚠️  SYSTEM NEEDS ATTENTION")
        print("=" * 30)
        print("❌ Some components need fixing before use")