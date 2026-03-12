#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cleanup data folder - keep only essential files as requested
"""

import os
import shutil
from datetime import datetime

def cleanup_data_folder():
    """Remove unnecessary files and folders, keep only core files"""
    
    base_dir = r"C:\Users\Mr Hieu\Documents\vietnamese-traffic-law-qa\data"
    
    print("🧹 Starting data folder cleanup...")
    
    # Essential files to keep
    essential_files = [
        "raw/legal_documents/nghi_dinh_100_2019.json",
        "processed/violations_100.json"
    ]
    
    # Get all current files and folders
    all_items = []
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, base_dir).replace('\\', '/')
            all_items.append(('file', full_path, rel_path))
    
    # Check what will be kept vs removed
    kept_files = []
    removed_files = []
    
    for item_type, full_path, rel_path in all_items:
        if rel_path in essential_files:
            kept_files.append((full_path, rel_path))
        else:
            removed_files.append((full_path, rel_path))
    
    print(f"\n📊 Cleanup Analysis:")
    print(f"   Files to keep: {len(kept_files)}")
    print(f"   Files to remove: {len(removed_files)}")
    
    # Show what will be kept
    print(f"\n✅ Files to keep:")
    for full_path, rel_path in kept_files:
        size = os.path.getsize(full_path) / (1024*1024)  # MB
        print(f"   📄 {rel_path} ({size:.1f} MB)")
    
    # Show what will be removed
    print(f"\n🗑️  Files to remove:")
    for full_path, rel_path in removed_files[:10]:  # Show first 10
        try:
            size = os.path.getsize(full_path) / (1024*1024)  # MB
            print(f"   ❌ {rel_path} ({size:.1f} MB)")
        except:
            print(f"   ❌ {rel_path}")
    
    if len(removed_files) > 10:
        print(f"   ... and {len(removed_files) - 10} more files")
    
    # Ask for confirmation
    print(f"\n⚠️  This will remove {len(removed_files)} files and keep only the 2 essential files.")
    response = input("Continue? (y/N): ").lower()
    
    if response != 'y':
        print("❌ Cleanup cancelled")
        return
    
    # Create backup of structure before cleanup
    backup_dir = f"backup_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    backup_path = os.path.join(os.path.dirname(base_dir), backup_dir)
    
    print(f"\n📦 Creating backup at: {backup_path}")
    shutil.copytree(base_dir, backup_path)
    
    # Remove files
    removed_count = 0
    for full_path, rel_path in removed_files:
        try:
            os.remove(full_path)
            removed_count += 1
        except Exception as e:
            print(f"⚠️  Could not remove {rel_path}: {e}")
    
    # Remove empty directories
    for root, dirs, files in os.walk(base_dir, topdown=False):
        for dir_name in dirs:
            dir_path = os.path.join(root, dir_name)
            try:
                # Only remove if empty
                if not os.listdir(dir_path):
                    os.rmdir(dir_path)
                    print(f"📁 Removed empty directory: {os.path.relpath(dir_path, base_dir)}")
            except:
                pass
    
    print(f"\n✅ Cleanup completed!")
    print(f"   📄 Files removed: {removed_count}")
    print(f"   📄 Files kept: {len(kept_files)}")
    print(f"   📦 Backup created: {backup_path}")
    
    # Verify final structure
    print(f"\n📋 Final data folder structure:")
    for root, dirs, files in os.walk(base_dir):
        level = root.replace(base_dir, '').count(os.sep)
        indent = ' ' * 2 * level
        folder_name = os.path.basename(root)
        if level == 0:
            folder_name = 'data/'
        print(f"{indent}{folder_name}/")
        
        sub_indent = ' ' * 2 * (level + 1)
        for file in files:
            file_path = os.path.join(root, file)
            size = os.path.getsize(file_path) / (1024*1024)  # MB
            print(f"{sub_indent}{file} ({size:.1f} MB)")

def verify_essential_files():
    """Verify that essential files exist and are valid"""
    base_dir = r"C:\Users\Mr Hieu\Documents\vietnamese-traffic-law-qa\data"
    
    essential_files = {
        "raw/legal_documents/nghi_dinh_100_2019.json": "Raw legal document",
        "processed/violations_100.json": "Processed violations"
    }
    
    print("\n🔍 Verifying essential files:")
    
    all_good = True
    for rel_path, description in essential_files.items():
        full_path = os.path.join(base_dir, rel_path.replace('/', os.sep))
        
        if os.path.exists(full_path):
            size = os.path.getsize(full_path) / (1024*1024)  # MB
            print(f"   ✅ {description}: {rel_path} ({size:.1f} MB)")
            
            # Quick validation
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    import json
                    data = json.load(f)
                    if 'violations' in data:
                        print(f"      📊 Contains {len(data['violations'])} violations")
                    elif 'key_articles' in data:
                        print(f"      📊 Contains {len(data['key_articles'])} articles")
            except Exception as e:
                print(f"      ⚠️  Warning: {e}")
                all_good = False
        else:
            print(f"   ❌ Missing: {description} at {rel_path}")
            all_good = False
    
    return all_good

if __name__ == "__main__":
    print("🧹 Data Folder Cleanup Tool")
    print("=" * 50)
    
    # First verify current essential files
    if verify_essential_files():
        print("\n✅ All essential files are present and valid")
        cleanup_data_folder()
    else:
        print("\n❌ Some essential files are missing or invalid")
        print("Please ensure the direct conversion was successful first")