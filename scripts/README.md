# Vietnamese Traffic Law Q&A - Scripts Documentation

## 📁 Scripts Overview

This folder contains scripts for processing Vietnamese traffic law documents and categorizing violations by vehicle types and other criteria.

## 🚀 Quick Start - One Command Processing

### Main Script: `category_detector.py`
**The ALL-IN-ONE solution for category detection and processing**

```bash
python scripts/category_detector.py
```

This single script will:
- ✅ Load raw legal documents from `data/raw/legal_documents/nghi_dinh_100_2019.json`
- ✅ Detect and categorize violations by vehicle types
- ✅ Remove duplicates and invalid entries
- ✅ Generate clean `data/processed/violations_100.json`
- ✅ Provide comprehensive analysis report

## 🔧 Core Scripts (Active)

### 1. `category_detector.py` ⭐ **MAIN SCRIPT**
**Purpose**: Complete categorization pipeline in one script
- Merges all categorization functionality
- Detects 13+ vehicle types automatically
- Processes business/administrative categories
- Removes duplicates and invalid data
- Generates analysis report

**Usage**:
```bash
python scripts/category_detector.py
```

### 2. `direct_raw_to_processed.py`
**Purpose**: Direct conversion from raw JSON to processed violations
- Clean data pipeline without intermediate formats
- Basic categorization (legacy support)

**Usage**:
```bash
python scripts/direct_raw_to_processed.py
```

## 📋 Vehicle Types Detected

The system automatically detects these vehicle categories:

### 🚗 Primary Vehicles
- **Xe ô tô** - Cars and automobiles
- **Xe mô tô, xe máy** - Motorcycles and motorbikes
- **Xe thô sơ** - Primitive vehicles (ox carts, human-powered)

### 🚚 Commercial Vehicles
- **Xe tải, container** - Trucks and containers
- **Xe khách, xe buýt** - Buses and passenger vehicles
- **Rơ moóc, sơ mi rơ moóc** - Trailers and semi-trailers
- **Taxi, xe du lịch** - Taxis and tourism vehicles

### 🚲 Other Vehicles
- **Xe đạp** - Bicycles
- **Xe điện** - Electric vehicles
- **Xe lăn** - Wheelchairs
- **Máy kéo** - Tractors

### 🚂 Rail & Water Transport
- **Tàu hỏa, đường sắt** - Trains and railways
- **Tàu thủy, thuyền** - Ships and boats

### 🚶 Pedestrians
- **Người đi bộ** - Pedestrians

## 🏢 Additional Categories

### Business & Administrative
- **Kinh doanh vận tải** - Transport business
- **Đào tạo lái xe** - Driving training
- **Sát hạch lái xe** - Driving examination
- **Quản lý nhà nước** - State management

### Behavioral Violations
- **Vi phạm tốc độ** - Speed violations
- **Vi phạm tín hiệu giao thông** - Traffic signal violations
- **Vi phạm về rượu bia** - Alcohol violations
- **Sử dụng điện thoại** - Phone usage violations
- **Vi phạm dừng đỗ xe** - Parking violations
- **Vi phạm vượt xe** - Overtaking violations

## 📊 Output Format

The processed `violations_100.json` contains:
```json
{
  "metadata": {
    "total_violations": 1110,
    "processed_date": "2025-11-19T...",
    "categories": ["Xe ô tô", "Xe mô tô, xe máy", ...],
    "validation_summary": {...}
  },
  "violations": [
    {
      "id": 1,
      "description": "Violation description",
      "category": "Xe ô tô",
      "penalty": {
        "fine_min": 200000,
        "fine_max": 400000,
        "currency": "VNĐ",
        "fine_text": "200,000 - 400,000 VNĐ"
      },
      "legal_basis": {
        "article": "Điều 5",
        "section": "Khoản 1",
        "document": "Nghị định 100/2019/NĐ-CP"
      },
      "severity": "Nhẹ",
      "keywords": [...],
      "search_text": "..."
    }
  ]
}
```

## 🔄 Workflow

### For New Legal Documents

1. **Add raw document**: Place new JSON in `data/raw/legal_documents/`
2. **Run detection**: `python scripts/category_detector.py`  
3. **Review results**: Check the analysis report
4. **Use processed data**: File ready at `data/processed/violations_100.json`

### For Category Improvements

1. **Edit patterns**: Modify `VehicleCategoryDetector` class in `category_detector.py`
2. **Add new vehicle types**: Update `vehicle_patterns` dictionary
3. **Test changes**: Run `python scripts/category_detector.py`
4. **Validate results**: Review the generated report

## 🛠️ Maintenance Scripts

### `extractor.py` & `update_manager.py`
- Extract new articles from DOCX files
- Merge updates from amended regulations
- Handle document version control

### `cleanup_data.py`
- Remove unnecessary intermediate files
- Clean up data folder structure

## 📈 Performance Metrics

Expected results with current system:
- **1,110+ violations** processed
- **27+ categories** detected
- **13 vehicle types** identified  
- **65%+ vehicle-specific** categorization
- **0 duplicates** after processing
- **Processing time**: ~5-10 seconds

## 🚨 Troubleshooting

### Common Issues

1. **Import errors**: Ensure all dependencies installed
2. **File not found**: Check file paths in script
3. **JSON format errors**: Validate raw JSON structure
4. **Memory issues**: Large files may need chunked processing

### Debug Mode

Add debug prints in `category_detector.py`:
```python
print(f"Debug: Processing article {article_number}")
print(f"Debug: Detected category: {category}")
```

## 🔮 Future Enhancements

### Planned Features
- [ ] Multi-document processing
- [ ] Category confidence scoring  
- [ ] Interactive category review
- [ ] Export to different formats
- [ ] API endpoint for categorization

### Integration Points
- **Q&A System**: Use processed violations for semantic search
- **Web Interface**: Display categorized violations  
- **Analytics**: Generate violation statistics by category
- **Updates**: Automatic processing of new regulations

---

## 📞 Support

For issues or improvements:
1. Check existing categories in processed output
2. Review vehicle patterns in `category_detector.py`
3. Test with sample violations
4. Adjust detection patterns as needed

**Last updated**: November 19, 2025
**Version**: Enhanced Vehicle Detection v3