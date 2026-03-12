import sys
from pathlib import Path
import logging
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from system.model import Model
from scripts.category_detector import VehicleCategoryDetector
from system.utils import log_results
import argparse
import json
from tqdm import tqdm
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Vietnamese Traffic Law QA - CLI Interface')
    parser.add_argument('--data_path', '-d', type=str, required=True, help='The path to the data file')
    parser.add_argument('--hybrid', action='store_true', help='Use hybrid search')
    parser.add_argument('--open-source', '-o', action='store_true', default=False, help='Use open source model')
    args = parser.parse_args()
    data_path = args.data_path
    logging.basicConfig(filename=f'evaluation/evaluation_{"hybrid" if args.hybrid else "vector"}_{"open-source" if args.open_source else "closed-source"}.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    detector = VehicleCategoryDetector()
    vehicle_patterns = [keywords for keywords in detector.vehicle_patterns] 
    business_patterns = [keywords for keywords in detector.business_patterns]
    fallback_patterns = [keywords for keywords in detector.fallback_categories]

    model = Model(uri="neo4j+s://7aa78485.databases.neo4j.io", auth=("neo4j", "iX59KTgWRNyZvmkh3dDBGe0Dwbm-_XQGdP1KCW_m7rs"))
    decree_filter = "ND100"

    with open(data_path, "r") as f:
        data = json.load(f)
    

    accuracy_1 = 0
    accuracy_5 = 0
    accuracy_10 = 0

    if args.open_source:
        model_name = "Qwen/Qwen3-4B"

        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model_llm = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype="auto",
            device_map="auto"
        )
    else:
        model_llm = None
        tokenizer = None

    for item in tqdm(data, total=len(data), desc="Evaluating"):
        query = item['question']
        logger.info(f"\n{'='*60}")
        logger.info(f"SEARCHING: {query}")
        logger.info(f"{'='*60}\n")
        if args.hybrid:
        
            results = model.hybrid_search(query, vehicle_patterns, business_patterns, fallback_patterns, model_llm=[tokenizer, model_llm], top_k=10, decree_filter=decree_filter)
        else:
            results = model.vector_search(query, vehicle_patterns, business_patterns, fallback_patterns, model_llm=[tokenizer, model_llm], top_k=10, decree_filter=decree_filter)

        logger.info(f"Results: {log_results(results)}")
        if len(results) == 0:
            if item['id'] == -1:
                accuracy_1 += 1
                accuracy_5 += 1
                accuracy_10 += 1
                continue
            else:
                continue
        logger.info(f"Results: {results[0]['data']['id']} == {item['id']}")
        if results[0]['data']['id'] == item['id']:
            accuracy_1 += 1
        if item['id'] in [result['data']['id'] for result in results[:5]]:
            accuracy_5 += 1
        if item['id'] in [result['data']['id'] for result in results[:10]]:
            accuracy_10 += 1

    logger.info(f"Accuracy@1: {accuracy_1 / len(data) * 100:.2f}%")
    logger.info(f"Accuracy@5: {accuracy_5 / len(data) * 100:.2f}%")
    logger.info(f"Accuracy@10: {accuracy_10 / len(data) * 100:.2f}%")