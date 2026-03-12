#!/usr/bin/env python3
"""Test if the document filter is working in Cypher queries."""

import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from neo4j import GraphDatabase

URI = "neo4j+s://7aa78485.databases.neo4j.io"
AUTH = ("neo4j", "iX59KTgWRNyZvmkh3dDBGe0Dwbm-_XQGdP1KCW_m7rs")

driver = GraphDatabase.driver(URI, auth=AUTH)

print("\n" + "=" * 70)
print("TESTING DOCUMENT FILTER IN CYPHER")
print("=" * 70)

with driver.session() as session:
    # Test 1: Simple count without filter
    print("\n1. Count violations by document (no filter):")
    print("-" * 70)
    result = session.run("""
        MATCH (v:Violation)-[:DEFINED_IN]->(clause:Clause)-[:BELONGS_TO]->(article:Article)-[:PART_OF]->(doc:LegalDocument)
        RETURN doc.name as document, count(v) as count
        ORDER BY doc.name
    """)
    
    for record in result:
        print(f"   {record['document']}: {record['count']} violations")
    
    # Test 2: Count with ND168 filter
    print("\n2. Count violations with ND168 filter:")
    print("-" * 70)
    doc_name = "Nghị định 168/2024/NĐ-CP"
    result = session.run("""
        MATCH (v:Violation)-[:DEFINED_IN]->(clause:Clause)-[:BELONGS_TO]->(article:Article)-[:PART_OF]->(doc:LegalDocument)
        WHERE doc.name = $document
        RETURN count(v) as count
    """, document=doc_name)
    
    count = result.single()['count']
    print(f"   Filter: doc.name = '{doc_name}'")
    print(f"   Result: {count} violations")
    
    if count == 0:
        print("   ❌ PROBLEM: Filter returns 0 results!")
    elif count == 721:
        print("   ✓ Filter works correctly!")
    
    # Test 3: Sample ND168 violations
    print("\n3. Sample ND168 violations (first 3):")
    print("-" * 70)
    result = session.run("""
        MATCH (v:Violation)-[:DEFINED_IN]->(clause:Clause)-[:BELONGS_TO]->(article:Article)-[:PART_OF]->(doc:LegalDocument)
        WHERE doc.name = $document
        RETURN v.id as id, v.description as description, doc.name as document
        ORDER BY v.id
        LIMIT 3
    """, document=doc_name)
    
    for i, record in enumerate(result, 1):
        print(f"   {i}. ID {record['id']}: {record['description'][:60]}...")
        print(f"      Document: {record['document']}")
    
    # Test 4: Test the actual vector query structure
    print("\n4. Testing vector query with filter:")
    print("-" * 70)
    
    # Create a dummy embedding vector (all zeros, just for testing structure)
    dummy_vector = [0.0] * 768
    
    # This is the query structure used in model.py
    test_query = """
        CALL db.index.vector.queryNodes('violation_index', 50, $embedding)
        YIELD node, score
        MATCH (node)-[:HAS_FINE]->(fine:Fine)
        MATCH (node)-[:APPLIES_TO]->(veh:VehicleType)
        MATCH (node)-[:DEFINED_IN]->(clause:Clause)-[:BELONGS_TO]->(article:Article)-[:PART_OF]->(doc:LegalDocument)
        OPTIONAL MATCH (node)-[:HAS_ADDITIONAL_PENALTY]->(sup:SupplementaryPenalty)
        WHERE doc.name = $document
        RETURN node.id as id, doc.name as document, count(*) as total
        LIMIT 5
    """
    
    try:
        result = session.run(test_query, embedding=dummy_vector, document=doc_name)
        results = list(result)
        
        if results:
            print(f"   ✓ Query returned {len(results)} results")
            for r in results:
                print(f"      ID {r['id']}: {r['document']}")
        else:
            print("   ❌ Query returned 0 results!")
            print("   This means vector search + filter combination fails")
    except Exception as e:
        print(f"   ❌ Error: {e}")

print("\n" + "=" * 70)
print("DIAGNOSIS:")
print("=" * 70)

print("""
The issue is likely that:
1. Vector index returns top 50 violations by similarity from ALL documents
2. If those 50 don't include any ND168 violations, the WHERE filter eliminates all
3. This results in 0 or very few results, triggering the fallback

SOLUTION: Increase the vector search limit from 50 to a higher number
when using filters, to ensure we get results from the filtered document.
""")

driver.close()

