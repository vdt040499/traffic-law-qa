"""
Demo script to showcase the Vietnamese Traffic Law QA System.
Demonstrates knowledge graph, semantic reasoning, and intelligent Q&A capabilities.
"""

import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from traffic_law_qa.knowledge.qa_system import TrafficLawQASystem


def main():
    """Main demo function."""
    print("🚦 Vietnamese Traffic Law QA System - Knowledge Graph Demo")
    print("=" * 60)
    
    # Initialize system
    violations_path = Path(__file__).parent / "data" / "processed" / "violations_100.json"
    
    try:
        print("🔄 Initializing QA System...")
        qa_system = TrafficLawQASystem(str(violations_path))
        print("✅ System initialized successfully!")
        
        # Display statistics
        print("\n📊 System Statistics:")
        stats = qa_system.get_system_statistics()
        print(f"  - Total violations: {stats['knowledge_graph']['node_types'].get('behavior', 0)}")
        print(f"  - Knowledge nodes: {stats['knowledge_graph']['total_nodes']}")
        print(f"  - Relations: {stats['knowledge_graph']['total_relations']}")
        print(f"  - Graph density: {stats['knowledge_graph'].get('graph_density', 0):.3f}")
        
        # Demo queries
        demo_queries = [
            "Đi xe máy vượt đèn đỏ không đội mũ bảo hiểm",
            "Lái xe ô tô sau khi uống rượu", 
            "Đỗ xe trên vỉa hè",
            "Không có bằng lái xe khi lái xe máy",
            "Chở quá 2 người trên xe máy"
        ]
        
        print("\n🔍 Demo Q&A with Semantic Reasoning:")
        print("-" * 40)
        
        for i, query in enumerate(demo_queries, 1):
            print(f"\n{i}. Question: {query}")
            
            try:
                result = qa_system.ask_question(query, max_results=3)
                
                print(f"   Answer: {result.get('answer', 'No answer')[:200]}...")
                print(f"   Confidence: {result.get('confidence', 'unknown')}")
                print(f"   Intent: {result.get('intent', {}).get('type', 'unknown')}")
                
                if result.get('citations'):
                    print(f"   Legal basis: {result['citations'][0]['source']}")
                    
            except Exception as e:
                print(f"   Error: {e}")
        
        # Benchmark
        print("\n🔬 Running Benchmark...")
        benchmark_results = qa_system.benchmark_system(demo_queries)
        
        print(f"   Success rate: {benchmark_results['success_rate']*100:.1f}%")
        print(f"   Average processing time: {benchmark_results['average_processing_time']:.3f}s")
        print(f"   Confidence distribution: {benchmark_results['confidence_distribution']}")
        
        print("\n🎉 Demo completed successfully!")
        print("\n💡 To run the full web interface:")
        print("   cd src/traffic_law_qa/ui")
        print("   streamlit run streamlit_app.py")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
        
    return 0


if __name__ == "__main__":
    exit(main())