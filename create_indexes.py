#!/usr/bin/env python3
"""
Create required indexes for the Vietnamese Traffic Law QA system.
This script creates:
1. Vector index for semantic search
2. Fulltext index for keyword search
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

import os
from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()
URI = os.environ.get("NEO4J_URI", "")
USER = os.environ.get("NEO4J_USER", "neo4j")
PASSWORD = os.environ.get("NEO4J_PASSWORD", "")
AUTH = (USER, PASSWORD)

driver = GraphDatabase.driver(URI, auth=AUTH)

print("\n" + "=" * 70)
print("CREATING INDEXES FOR TRAFFIC LAW QA SYSTEM")
print("=" * 70)

with driver.session() as session:
    # Check existing indexes
    print("\n1. Checking existing indexes...")
    print("-" * 70)
    
    result = session.run("SHOW INDEXES")
    existing_indexes = list(result)
    
    existing_names = [idx['name'] for idx in existing_indexes]
    
    if existing_indexes:
        print(f"   Found {len(existing_indexes)} existing index(es):")
        for idx in existing_indexes:
            print(f"   - {idx['name']} ({idx['type']})")
    else:
        print("   No existing indexes found")
    
    # Create vector index
    print("\n2. Creating vector index 'violation_index'...")
    print("-" * 70)
    
    if 'violation_index' in existing_names:
        print("   ⚠️  Index 'violation_index' already exists. Dropping it first...")
        try:
            session.run("DROP INDEX violation_index IF EXISTS")
            print("   ✓ Old index dropped")
        except Exception as e:
            print(f"   ⚠️  Could not drop index: {e}")
    
    try:
        # Create vector index for embeddings
        # Dimension: 768 (paraphrase-vietnamese-law model dimension)
        session.run("""
            CREATE VECTOR INDEX violation_index IF NOT EXISTS
            FOR (v:Violation)
            ON v.embedding
            OPTIONS {
                indexConfig: {
                    `vector.dimensions`: 768,
                    `vector.similarity_function`: 'cosine'
                }
            }
        """)
        print("   ✓ Vector index created successfully!")
        print("   - Index name: violation_index")
        print("   - Property: Violation.embedding")
        print("   - Dimensions: 768")
        print("   - Similarity: cosine")
    except Exception as e:
        print(f"   ❌ Error creating vector index: {e}")
    
    # Create fulltext index
    print("\n3. Creating fulltext index 'violation_text_index'...")
    print("-" * 70)
    
    if 'violation_text_index' in existing_names:
        print("   ⚠️  Index 'violation_text_index' already exists. Dropping it first...")
        try:
            session.run("DROP INDEX violation_text_index IF EXISTS")
            print("   ✓ Old index dropped")
        except Exception as e:
            print(f"   ⚠️  Could not drop index: {e}")
    
    try:
        # Create fulltext index for text search
        session.run("""
            CREATE FULLTEXT INDEX violation_text_index IF NOT EXISTS
            FOR (v:Violation)
            ON EACH [v.description]
        """)
        print("   ✓ Fulltext index created successfully!")
        print("   - Index name: violation_text_index")
        print("   - Property: Violation.description")
    except Exception as e:
        print(f"   ❌ Error creating fulltext index: {e}")
    
    # Wait for indexes to come online
    print("\n4. Waiting for indexes to come online...")
    print("-" * 70)
    print("   (This may take a few seconds...)")
    
    import time
    max_wait = 30  # seconds
    start_time = time.time()
    
    while time.time() - start_time < max_wait:
        result = session.run("""
            SHOW INDEXES
            WHERE name IN ['violation_index', 'violation_text_index']
        """)
        
        indexes = list(result)
        
        if len(indexes) == 2:
            all_online = all(idx['state'] == 'ONLINE' for idx in indexes)
            
            if all_online:
                print("   ✓ All indexes are ONLINE!")
                for idx in indexes:
                    print(f"   - {idx['name']}: {idx['state']}")
                break
            else:
                print(f"   ⏳ Waiting... ({int(time.time() - start_time)}s)")
                for idx in indexes:
                    print(f"      {idx['name']}: {idx['state']}")
                time.sleep(2)
        else:
            time.sleep(2)
    else:
        print("   ⚠️  Timeout waiting for indexes to come online")
        print("   They may still be building. Check with: SHOW INDEXES")
    
    # Verify indexes
    print("\n5. Final verification...")
    print("-" * 70)
    
    result = session.run("SHOW INDEXES")
    all_indexes = list(result)
    
    vector_index = next((i for i in all_indexes if i['name'] == 'violation_index'), None)
    fulltext_index = next((i for i in all_indexes if i['name'] == 'violation_text_index'), None)
    
    if vector_index and fulltext_index:
        print("   ✅ SUCCESS! Both indexes are created:")
        print(f"      1. violation_index: {vector_index['state']}")
        print(f"      2. violation_text_index: {fulltext_index['state']}")
    else:
        print("   ❌ Some indexes are missing:")
        if not vector_index:
            print("      - violation_index: NOT FOUND")
        if not fulltext_index:
            print("      - violation_text_index: NOT FOUND")

print("\n" + "=" * 70)
print("INDEX CREATION COMPLETE")
print("=" * 70)

print("\n📝 NEXT STEPS:")
print("-" * 70)
print("1. Wait for indexes to fully build (if they're still POPULATING)")
print("2. Test your search:")
print('   python system/main.py -q "vượt đèn đỏ" -d ND168_2024')
print()

driver.close()

