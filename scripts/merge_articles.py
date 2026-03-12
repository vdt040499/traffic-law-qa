#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to merge parsed articles from DOCX into the main legal document JSON
"""

import json
import os
from datetime import datetime

def load_json_file(file_path):
    """Load JSON file with error handling"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading file {file_path}: {e}")
        return None

def save_json_file(data, file_path):
    """Save JSON file with error handling"""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Error saving file {file_path}: {e}")
        return False

def format_currency_range(range_str):
    """Format currency range to standard format"""
    if not range_str:
        return None
    
    # Extract numbers and format them properly
    range_str = range_str.replace(" VNĐ", "").replace("VNĐ", "")
    if " - " in range_str:
        min_val, max_val = range_str.split(" - ")
        min_val = min_val.replace(".", "").replace(",", "")
        max_val = max_val.replace(".", "").replace(",", "")
        return f"{min_val} - {max_val} VNĐ"
    return range_str

def clean_violations(violations):
    """Clean and format violation descriptions"""
    if not violations:
        return []
    
    cleaned = []
    for violation in violations:
        if isinstance(violation, str):
            # Remove reference patterns and clean up text
            violation = violation.strip()
            if violation and not violation.startswith(("điểm ", "khoản ", "Điều ")):
                # Capitalize first letter if needed
                if violation and violation[0].islower():
                    violation = violation[0].upper() + violation[1:]
                cleaned.append(violation)
    
    return cleaned

def merge_articles(main_doc, parsed_articles):
    """Merge parsed articles into main document"""
    if not main_doc or not parsed_articles:
        return None
    
    # Create backup of original
    backup_key_articles = main_doc.get("key_articles", {}).copy()
    
    # Update statistics
    total_new_violations = 0
    updated_articles = 0
    
    for article_key, article_data in parsed_articles.items():
        if article_key in main_doc.get("key_articles", {}):
            print(f"Updating existing article: {article_key}")
        else:
            print(f"Adding new article: {article_key}")
        
        # Format the article data
        formatted_article = {
            "title": article_data.get("title", ""),
            "sections": []
        }
        
        # Add metadata
        if "source_document" in article_data:
            formatted_article["source_document"] = article_data["source_document"]
        if "extraction_date" in article_data:
            formatted_article["extraction_date"] = article_data["extraction_date"]
        
        # Process sections
        for section in article_data.get("sections", []):
            formatted_section = {
                "section": section.get("section", ""),
                "fine_range": format_currency_range(section.get("fine_range")),
                "violations": clean_violations(section.get("violations", []))
            }
            
            if section.get("additional_measures"):
                formatted_section["additional_measures"] = section["additional_measures"]
            
            formatted_article["sections"].append(formatted_section)
            total_new_violations += len(formatted_section["violations"])
        
        # Update the main document
        main_doc["key_articles"][article_key] = formatted_article
        updated_articles += 1
    
    # Update document metadata
    main_doc["document_info"]["last_updated"] = datetime.now().strftime("%Y-%m-%d")
    main_doc["document_info"]["update_source"] = "ND100-2019.docx extraction"
    
    # Update statistics
    if "statistics" not in main_doc:
        main_doc["statistics"] = {}
    
    main_doc["statistics"]["total_updated_articles"] = updated_articles
    main_doc["statistics"]["total_extracted_violations"] = total_new_violations
    main_doc["statistics"]["last_extraction_date"] = datetime.now().strftime("%Y-%m-%d")
    
    print(f"\nMerge Summary:")
    print(f"- Updated articles: {updated_articles}")
    print(f"- Total violations extracted: {total_new_violations}")
    
    return main_doc

def main():
    """Main function to merge parsed articles"""
    base_dir = r"c:\Users\Mr Hieu\Documents\vietnamese-traffic-law-qa"
    
    # File paths
    main_doc_path = os.path.join(base_dir, "data", "raw", "legal_documents", "nghi_dinh_100_2019.json")
    parsed_articles_path = os.path.join(base_dir, "docs", "ND100-2019-parsed-articles.json")
    backup_path = os.path.join(base_dir, "data", "raw", "legal_documents", f"nghi_dinh_100_2019_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    
    print("Loading files...")
    
    # Load main document
    main_doc = load_json_file(main_doc_path)
    if not main_doc:
        print("Failed to load main document")
        return
    
    # Load parsed articles
    parsed_articles = load_json_file(parsed_articles_path)
    if not parsed_articles:
        print("Failed to load parsed articles")
        return
    
    # Create backup
    print(f"Creating backup at: {backup_path}")
    if not save_json_file(main_doc, backup_path):
        print("Failed to create backup - aborting merge")
        return
    
    # Merge articles
    print("Merging articles...")
    merged_doc = merge_articles(main_doc, parsed_articles)
    
    if merged_doc:
        # Save updated document
        print(f"Saving updated document to: {main_doc_path}")
        if save_json_file(merged_doc, main_doc_path):
            print("✅ Successfully merged all articles into main document!")
        else:
            print("❌ Failed to save updated document")
    else:
        print("❌ Failed to merge articles")

if __name__ == "__main__":
    main()