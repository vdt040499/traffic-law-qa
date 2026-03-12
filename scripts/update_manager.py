#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Document Update Manager for Vietnamese Traffic Law System
Handles incremental updates, change detection, and merging strategies
"""

import json
import os
import shutil
from datetime import datetime
from extractor import VietnameseTrafficLawExtractor

class DocumentUpdateManager:
    """Manages document updates and incremental changes"""
    
    def __init__(self, base_dir=None):
        self.base_dir = base_dir or r"C:\Users\Mr Hieu\Documents\vietnamese-traffic-law-qa"
        self.extractor = VietnameseTrafficLawExtractor()
        self.main_doc_path = os.path.join(self.base_dir, "data/raw/legal_documents/nghi_dinh_100_2019.json")
        self.metadata_path = os.path.join(self.base_dir, "data/metadata/update_history.json")
        
    def detect_new_files(self, watch_directory):
        """Detect new or modified files in watch directory"""
        if not os.path.exists(watch_directory):
            return []
        
        new_files = []
        metadata = self.load_update_metadata()
        
        for root, dirs, files in os.walk(watch_directory):
            for file in files:
                file_path = os.path.join(root, file)
                file_hash = self.extractor.calculate_file_hash(file_path)
                
                # Check if file is new or modified
                relative_path = os.path.relpath(file_path, watch_directory)
                
                if relative_path not in metadata.get("file_hashes", {}) or \
                   metadata["file_hashes"][relative_path] != file_hash:
                    
                    new_files.append({
                        "path": file_path,
                        "relative_path": relative_path,
                        "hash": file_hash,
                        "size": os.path.getsize(file_path),
                        "modified": datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat()
                    })
        
        return new_files
    
    def load_update_metadata(self):
        """Load update history metadata"""
        try:
            os.makedirs(os.path.dirname(self.metadata_path), exist_ok=True)
            with open(self.metadata_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {
                "file_hashes": {},
                "update_history": [],
                "last_check": None
            }
    
    def save_update_metadata(self, metadata):
        """Save update history metadata"""
        try:
            os.makedirs(os.path.dirname(self.metadata_path), exist_ok=True)
            with open(self.metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Warning: Could not save metadata: {e}")
    
    def process_new_file(self, file_info):
        """Process a single new/modified file"""
        file_path = file_info["path"]
        
        try:
            # Detect document structure
            doc_structure = self.extractor.detect_document_type(file_path)
            print(f"Processing {file_info['relative_path']} - Type: {doc_structure['decree_type']}")
            
            # Extract content based on file type
            if file_path.endswith('.docx'):
                raw_content = self.extractor.extract_from_docx(file_path)
            else:
                raise ValueError(f"Unsupported file type: {file_path}")
            
            # Parse content
            parsed_articles = self.extractor.parse_with_adaptive_patterns(
                raw_content, doc_structure['decree_type']
            )
            
            if not parsed_articles:
                print(f"No articles found in {file_info['relative_path']}")
                return None
            
            # Add metadata
            extraction_info = {
                "source_file": file_info["relative_path"],
                "source_hash": file_info["hash"],
                "extraction_date": datetime.now().isoformat(),
                "document_type": doc_structure['decree_type'],
                "articles_count": len(parsed_articles),
                "total_violations": sum(
                    sum(len(section.get("violations", [])) for section in article.get("sections", []))
                    for article in parsed_articles.values()
                )
            }
            
            return {
                "articles": parsed_articles,
                "metadata": extraction_info
            }
            
        except Exception as e:
            print(f"Error processing {file_info['relative_path']}: {e}")
            return None
    
    def merge_strategies(self):
        """Available merge strategies"""
        return {
            "replace": self.merge_replace,
            "append": self.merge_append, 
            "smart_merge": self.merge_smart,
            "version_control": self.merge_version_control
        }
    
    def merge_replace(self, main_doc, new_data):
        """Replace strategy: completely replace matching articles"""
        for article_key, article_data in new_data["articles"].items():
            main_doc["key_articles"][article_key] = article_data
            print(f"Replaced {article_key}")
        return main_doc
    
    def merge_append(self, main_doc, new_data):
        """Append strategy: add new articles, keep existing ones"""
        for article_key, article_data in new_data["articles"].items():
            if article_key not in main_doc["key_articles"]:
                main_doc["key_articles"][article_key] = article_data
                print(f"Added new {article_key}")
            else:
                print(f"Skipped existing {article_key}")
        return main_doc
    
    def merge_smart(self, main_doc, new_data):
        """Smart merge: compare content and merge intelligently"""
        for article_key, new_article in new_data["articles"].items():
            if article_key in main_doc["key_articles"]:
                existing_article = main_doc["key_articles"][article_key]
                
                # Compare sections
                merged_sections = []
                existing_sections = {s.get("section", ""): s for s in existing_article.get("sections", [])}
                
                for new_section in new_article.get("sections", []):
                    section_key = new_section.get("section", "")
                    
                    if section_key in existing_sections:
                        # Merge violations from both
                        existing_violations = set(existing_sections[section_key].get("violations", []))
                        new_violations = set(new_section.get("violations", []))
                        
                        merged_violations = list(existing_violations.union(new_violations))
                        
                        merged_section = existing_sections[section_key].copy()
                        merged_section["violations"] = merged_violations
                        
                        # Update other fields if different
                        if new_section.get("fine_range") != merged_section.get("fine_range"):
                            merged_section["fine_range"] = new_section.get("fine_range")
                            merged_section["_updated"] = datetime.now().isoformat()
                        
                        merged_sections.append(merged_section)
                        del existing_sections[section_key]
                    else:
                        # New section
                        merged_sections.append(new_section)
                
                # Add remaining existing sections
                merged_sections.extend(existing_sections.values())
                
                # Update article
                main_doc["key_articles"][article_key]["sections"] = merged_sections
                main_doc["key_articles"][article_key]["_last_updated"] = datetime.now().isoformat()
                
                print(f"Smart merged {article_key}")
            else:
                # New article
                main_doc["key_articles"][article_key] = new_article
                print(f"Added new {article_key}")
        
        return main_doc
    
    def merge_version_control(self, main_doc, new_data):
        """Version control merge: keep history of changes"""
        if "_versions" not in main_doc:
            main_doc["_versions"] = {}
        
        for article_key, new_article in new_data["articles"].items():
            # Create version entry
            version_key = f"{article_key}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            if article_key in main_doc["key_articles"]:
                # Save current version to history
                main_doc["_versions"][version_key] = {
                    "article_key": article_key,
                    "timestamp": datetime.now().isoformat(),
                    "previous_data": main_doc["key_articles"][article_key].copy(),
                    "source": new_data["metadata"]["source_file"]
                }
            
            # Update with new data
            main_doc["key_articles"][article_key] = new_article
            main_doc["key_articles"][article_key]["_version"] = version_key
            
            print(f"Version controlled update for {article_key}")
        
        return main_doc
    
    def update_from_directory(self, watch_dir, merge_strategy="smart_merge"):
        """Main update process from directory"""
        print(f"🔍 Checking for updates in: {watch_dir}")
        
        # Detect new/modified files
        new_files = self.detect_new_files(watch_dir)
        
        if not new_files:
            print("✅ No new files detected")
            return
        
        print(f"📄 Found {len(new_files)} new/modified files:")
        for file_info in new_files:
            print(f"  - {file_info['relative_path']}")
        
        # Create backup
        self.create_backup()
        
        # Load main document
        main_doc = self.load_main_document()
        
        # Process each file
        updates_applied = 0
        metadata = self.load_update_metadata()
        
        for file_info in new_files:
            print(f"\n🔄 Processing: {file_info['relative_path']}")
            
            processed_data = self.process_new_file(file_info)
            
            if processed_data:
                # Apply merge strategy
                merge_func = self.merge_strategies().get(merge_strategy, self.merge_smart)
                main_doc = merge_func(main_doc, processed_data)
                
                # Update metadata
                metadata["file_hashes"][file_info["relative_path"]] = file_info["hash"]
                metadata["update_history"].append(processed_data["metadata"])
                
                updates_applied += 1
                
                print(f"✅ Successfully processed {file_info['relative_path']}")
            else:
                print(f"❌ Failed to process {file_info['relative_path']}")
        
        if updates_applied > 0:
            # Update document metadata
            main_doc["document_info"]["last_updated"] = datetime.now().strftime("%Y-%m-%d")
            main_doc["document_info"]["update_source"] = f"Batch update - {updates_applied} files"
            
            # Save updated document
            self.save_main_document(main_doc)
            
            # Save update metadata
            metadata["last_check"] = datetime.now().isoformat()
            self.save_update_metadata(metadata)
            
            print(f"\n🎉 Update completed! {updates_applied} files processed successfully.")
        else:
            print(f"\n⚠️  No updates applied.")
    
    def create_backup(self):
        """Create backup of main document"""
        if os.path.exists(self.main_doc_path):
            backup_dir = os.path.join(self.base_dir, "data/backups")
            os.makedirs(backup_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = os.path.join(backup_dir, f"nghi_dinh_100_2019_backup_{timestamp}.json")
            
            shutil.copy2(self.main_doc_path, backup_path)
            print(f"📦 Backup created: {backup_path}")
    
    def load_main_document(self):
        """Load main legal document"""
        try:
            with open(self.main_doc_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            raise Exception(f"Failed to load main document: {e}")
    
    def save_main_document(self, doc):
        """Save main legal document"""
        try:
            with open(self.main_doc_path, 'w', encoding='utf-8') as f:
                json.dump(doc, f, ensure_ascii=False, indent=2)
        except Exception as e:
            raise Exception(f"Failed to save main document: {e}")

# CLI Interface
def main():
    """Main CLI function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Vietnamese Traffic Law Document Update Manager")
    parser.add_argument("watch_dir", help="Directory to watch for new/modified files")
    parser.add_argument("--strategy", choices=["replace", "append", "smart_merge", "version_control"], 
                       default="smart_merge", help="Merge strategy to use")
    parser.add_argument("--base-dir", help="Base directory of the project")
    
    args = parser.parse_args()
    
    manager = DocumentUpdateManager(args.base_dir)
    manager.update_from_directory(args.watch_dir, args.strategy)

if __name__ == "__main__":
    main()