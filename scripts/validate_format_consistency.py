#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to validate that nghi_dinh_123_2021.json format matches nghi_dinh_100_2019.json format
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Any

class FormatValidator:
    """Validate format consistency between the two legal documents"""
    
    def __init__(self, file_123_path: str, file_100_path: str):
        with open(file_123_path, 'r', encoding='utf-8') as f:
            self.data_123 = json.load(f)
        
        with open(file_100_path, 'r', encoding='utf-8') as f:
            self.data_100 = json.load(f)
    
    def validate_format(self) -> Dict[str, Any]:
        """Validate format consistency"""
        
        print("🔍 Đang kiểm tra format consistency...")
        
        validation_results = {
            "format_consistency": True,
            "issues": [],
            "statistics": {
                "file_123": self._get_file_stats(self.data_123),
                "file_100": self._get_file_stats(self.data_100)
            },
            "lettered_points_validation": {
                "file_123": self._validate_lettered_points(self.data_123),
                "file_100": self._validate_lettered_points(self.data_100)
            }
        }
        
        # Check structure consistency
        self._check_structure_consistency(validation_results)
        
        # Check violations format
        self._check_violations_format(validation_results)
        
        return validation_results
    
    def _get_file_stats(self, data: Dict[str, Any]) -> Dict[str, int]:
        """Get statistics for a file"""
        
        stats = {
            "total_articles": 0,
            "articles_with_sections": 0,
            "total_sections": 0,
            "sections_with_violations": 0,
            "total_violations": 0,
            "violations_with_letters": 0
        }
        
        articles = data.get("articles", {})
        stats["total_articles"] = len(articles)
        
        for article_key, article_data in articles.items():
            if "sections" in article_data:
                stats["articles_with_sections"] += 1
                
                sections = article_data["sections"]
                stats["total_sections"] += len(sections)
                
                for section in sections:
                    if "violations" in section:
                        stats["sections_with_violations"] += 1
                        violations = section["violations"]
                        stats["total_violations"] += len(violations)
                        
                        # Count violations that start with letters
                        for violation in violations:
                            if re.match(r'^[a-zđ]+\)\s*', violation, re.IGNORECASE):
                                stats["violations_with_letters"] += 1
        
        return stats
    
    def _validate_lettered_points(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate lettered points format"""
        
        validation = {
            "total_violations": 0,
            "violations_with_letters": 0,
            "violations_without_letters": 0,
            "percentage_with_letters": 0.0,
            "sample_violations_without_letters": []
        }
        
        articles = data.get("articles", {})
        
        for article_key, article_data in articles.items():
            if "sections" not in article_data:
                continue
                
            for section in article_data["sections"]:
                if "violations" not in section:
                    continue
                
                for violation in section["violations"]:
                    validation["total_violations"] += 1
                    
                    if re.match(r'^[a-zđ]+\)\s*', violation, re.IGNORECASE):
                        validation["violations_with_letters"] += 1
                    else:
                        validation["violations_without_letters"] += 1
                        
                        # Collect samples
                        if len(validation["sample_violations_without_letters"]) < 5:
                            validation["sample_violations_without_letters"].append({
                                "article": article_key,
                                "section": section.get("section", "Unknown"),
                                "violation": violation[:100] + "..." if len(violation) > 100 else violation
                            })
        
        if validation["total_violations"] > 0:
            validation["percentage_with_letters"] = (
                validation["violations_with_letters"] / validation["total_violations"]
            ) * 100
        
        return validation
    
    def _check_structure_consistency(self, results: Dict[str, Any]) -> None:
        """Check if both files have consistent structure"""
        
        # Check if both have articles
        if "articles" not in self.data_123:
            results["issues"].append("File 123 missing 'articles' key")
            results["format_consistency"] = False
        
        if "articles" not in self.data_100:
            results["issues"].append("File 100 missing 'articles' key")
            results["format_consistency"] = False
        
        # Check document_info vs metadata structure difference
        if "document_info" in self.data_123 and "metadata" in self.data_100:
            results["issues"].append("Different metadata structure: 'document_info' vs 'metadata'")
    
    def _check_violations_format(self, results: Dict[str, Any]) -> None:
        """Check violations format consistency"""
        
        lettered_123 = results["lettered_points_validation"]["file_123"]
        lettered_100 = results["lettered_points_validation"]["file_100"]
        
        # Check if both files have similar percentage of lettered violations
        diff = abs(lettered_123["percentage_with_letters"] - lettered_100["percentage_with_letters"])
        
        if diff > 10:  # More than 10% difference
            results["issues"].append(
                f"Significant difference in lettered points: "
                f"123: {lettered_123['percentage_with_letters']:.1f}%, "
                f"100: {lettered_100['percentage_with_letters']:.1f}%"
            )
            results["format_consistency"] = False
        
        # Check if file 123 has reasonable number of lettered violations
        if lettered_123["percentage_with_letters"] < 80:
            results["issues"].append(
                f"File 123 has only {lettered_123['percentage_with_letters']:.1f}% violations with letters"
            )
            results["format_consistency"] = False
    
    def print_validation_report(self, results: Dict[str, Any]) -> None:
        """Print detailed validation report"""
        
        print("=" * 70)
        print("📋 FORMAT VALIDATION REPORT")
        print("=" * 70)
        
        # Overall status
        status = "✅ PASSED" if results["format_consistency"] else "❌ FAILED"
        print(f"Overall Status: {status}")
        
        if results["issues"]:
            print(f"\n🚨 Issues Found ({len(results['issues'])}):")
            for i, issue in enumerate(results["issues"], 1):
                print(f"   {i}. {issue}")
        
        # Statistics comparison
        print("\n📊 Statistics Comparison:")
        stats_123 = results["statistics"]["file_123"]
        stats_100 = results["statistics"]["file_100"]
        
        print(f"                           File 123    File 100")
        print(f"   Total Articles:         {stats_123['total_articles']:8d}    {stats_100['total_articles']:8d}")
        print(f"   Articles with Sections: {stats_123['articles_with_sections']:8d}    {stats_100['articles_with_sections']:8d}")
        print(f"   Total Sections:         {stats_123['total_sections']:8d}    {stats_100['total_sections']:8d}")
        print(f"   Sections with Violations:{stats_123['sections_with_violations']:8d}    {stats_100['sections_with_violations']:8d}")
        print(f"   Total Violations:       {stats_123['total_violations']:8d}    {stats_100['total_violations']:8d}")
        print(f"   Violations with Letters:{stats_123['violations_with_letters']:8d}    {stats_100['violations_with_letters']:8d}")
        
        # Lettered points validation
        print("\n🔤 Lettered Points Validation:")
        lettered_123 = results["lettered_points_validation"]["file_123"]
        lettered_100 = results["lettered_points_validation"]["file_100"]
        
        print(f"   File 123: {lettered_123['violations_with_letters']}/{lettered_123['total_violations']} "
              f"({lettered_123['percentage_with_letters']:.1f}%) have letters")
        print(f"   File 100: {lettered_100['violations_with_letters']}/{lettered_100['total_violations']} "
              f"({lettered_100['percentage_with_letters']:.1f}%) have letters")
        
        # Sample violations without letters (for file 123)
        if lettered_123["sample_violations_without_letters"]:
            print(f"\n📝 Sample violations without letters (File 123):")
            for sample in lettered_123["sample_violations_without_letters"]:
                print(f"   • {sample['article']} {sample['section']}: {sample['violation']}")
        
        print("=" * 70)

def main():
    """Main execution function"""
    
    print("🚀 Kiểm tra format consistency giữa 2 files...")
    
    base_dir = Path(__file__).parent.parent
    file_123_path = base_dir / "data" / "raw" / "legal_documents" / "nghi_dinh_123_2021.json"
    file_100_path = base_dir / "data" / "raw" / "legal_documents" / "nghi_dinh_100_2019.json"
    
    if not file_123_path.exists():
        print(f"❌ File không tồn tại: {file_123_path}")
        return
    
    if not file_100_path.exists():
        print(f"❌ File không tồn tại: {file_100_path}")
        return
    
    # Create validator
    validator = FormatValidator(str(file_123_path), str(file_100_path))
    
    # Run validation
    results = validator.validate_format()
    
    # Print report
    validator.print_validation_report(results)
    
    # Return appropriate exit code
    if results["format_consistency"]:
        print("\n✨ Format validation PASSED! Both files have consistent format.")
        return 0
    else:
        print("\n⚠️  Format validation FAILED! Please check the issues above.")
        return 1

if __name__ == "__main__":
    exit(main())