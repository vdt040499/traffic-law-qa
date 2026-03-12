import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from system.model import Model
from scripts.category_detector import VehicleCategoryDetector
from system.utils import print_results
import argparse
from transformers import AutoTokenizer, AutoModelForCausalLM
import json

def remove_duplicates(input_list):
    """
    Loại bỏ trùng lặp và giữ nguyên thứ tự.
    """
    if not input_list:
        return []
    return list(dict.fromkeys(input_list))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Vietnamese Traffic Law QA - CLI Interface')
    parser.add_argument('--query', '-q', type=str, required=True, help='The query to search for')
    parser.add_argument('--top-k', '-k', type=int, default=10, help='Number of results to return (default: 10)')
    parser.add_argument('--document-name', '-d', type=str, help='The name of the document to search for', choices=['ND100', 'ND168'])
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose output')
    parser.add_argument('--llm', '-l', default="gemini-2.5-flash", help='select the LLM model to use', choices=['gemini-2.5-flash', 'Qwen/Qwen3-4B'])
    args = parser.parse_args()
    query = args.query
    detector = VehicleCategoryDetector()
    vehicle_patterns = [keywords for keywords in detector.vehicle_patterns] 
    business_patterns = [keywords for keywords in detector.business_patterns]
    fallback_patterns = [keywords for keywords in detector.fallback_categories]

    model = Model(uri="neo4j+s://7aa78485.databases.neo4j.io", auth=("neo4j", "iX59KTgWRNyZvmkh3dDBGe0Dwbm-_XQGdP1KCW_m7rs"))

    print(f"\n{'='*60}")
    print(f"SEARCHING: {query}")
    print(f"{'='*60}\n")
    
    if args.llm == "gemini-2.5-flash":
        model_llm = [None, None]
    elif args.llm == "Qwen/Qwen3-4B":
        model_llm = [AutoTokenizer.from_pretrained(args.llm), AutoModelForCausalLM.from_pretrained(args.llm)]

    results = model.hybrid_search(
        query, 
        vehicle_patterns, 
        business_patterns, 
        fallback_patterns, 
        model_llm=model_llm,
        top_k=args.top_k, 
        verbose=args.verbose,
        decree_filter=args.document_name
    )
    if args.document_name == "ND168":
        with open("/home/taidvt/vietnamese-traffic-law-qa/data/processed/article2category_ND168.json", "r") as f:
            article2category = json.load(f)
    elif args.document_name == "ND100":
        with open("/home/taidvt/vietnamese-traffic-law-qa/data/processed/article2category_ND100.json", "r") as f:
            article2category = json.load(f)
    for result in results:
        result['data']['category'] = article2category[result['data']['law_article']]
        if result['data']['document'] == "ND168":
            result['data']['document'] = "Nghị định 168/2024/NĐ-CP"
        elif result['data']['document'] == "ND100":
            result['data']['document'] = "Nghị định 100/2019/NĐ-CP"
        result['data']['extra'] = remove_duplicates(result['data']['extra'])
    print_results(results)
