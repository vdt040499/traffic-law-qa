"""
Simple launcher for the Vietnamese Traffic Law QA System.
This script sets up the correct Python path and runs the demo.
"""

import sys
import os
from pathlib import Path

# Add the src directory to Python path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

# Now we can import our modules
try:
    print("🚦 Vietnamese Traffic Law QA System - Simple Demo")
    print("=" * 50)
    
    # Check if data exists
    violations_path = current_dir / "data" / "processed" / "violations_100.json"
    if not violations_path.exists():
        print("❌ Error: violations_100.json not found!")
        print(f"Expected at: {violations_path}")
        print("\nPlease ensure the data processing pipeline has been run.")
        sys.exit(1)
    
    print("✅ Data file found")
    print("🔄 Loading QA system (this may take a moment)...")
    
    from traffic_law_qa.knowledge.qa_system import TrafficLawQASystem
    
    # Initialize system
    qa_system = TrafficLawQASystem(str(violations_path))
    
    print("✅ System loaded successfully!")
    
    # Get system statistics
    stats = qa_system.get_system_statistics()
    print(f"\n📊 System Info:")
    print(f"  - Total violations: {stats['knowledge_graph']['node_types'].get('behavior', 0)}")
    print(f"  - Knowledge nodes: {stats['knowledge_graph']['total_nodes']}")
    print(f"  - Relations: {stats['knowledge_graph']['total_relations']}")
    
    # Test queries
    test_queries = [
        "Đi xe máy vượt đèn đỏ bị phạt bao nhiêu?",
        "Không đội mũ bảo hiểm khi lái xe máy",
        "Lái xe ô tô sau khi uống rượu"
    ]
    
    print(f"\n🔍 Testing {len(test_queries)} sample queries:")
    print("-" * 50)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. Question: {query}")
        
        try:
            result = qa_system.ask_question(query, max_results=1)
            
            confidence = result.get('confidence', 'unknown')
            answer = result.get('answer', 'No answer')
            
            print(f"   Confidence: {confidence}")
            
            if confidence in ['high', 'medium']:
                # Extract first 150 characters of answer
                short_answer = answer[:150] + "..." if len(answer) > 150 else answer
                print(f"   Answer: {short_answer}")
                
                # Show citations if available
                citations = result.get('citations', [])
                if citations:
                    print(f"   Legal basis: {citations[0]['source']}")
            else:
                print(f"   Result: No definitive answer found")
                
        except Exception as e:
            print(f"   Error: {e}")
    
    print(f"\n🎉 Demo completed!")
    print(f"\n💡 To run the full web interface, use:")
    print(f"   python run_streamlit.py")
    
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("\nPlease ensure all dependencies are installed:")
    print("  pip install -r requirements.txt")
    print("  pip install -r requirements-knowledge.txt")
    
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)