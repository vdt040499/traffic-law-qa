from google import genai
from system.constant import SYSTEM_PROMPT
import json
import logging
import os
from dotenv import load_dotenv
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

load_dotenv()

def analyze_traffic_query(user_query, tokenizer, model):
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_query}
    ]

    try:
        text = tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
            enable_thinking=False 
        )
    except TypeError:
        text = tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )

    model_inputs = tokenizer([text], return_tensors="pt").to(model.device)

    with torch.no_grad():
        generated_ids = model.generate(
            **model_inputs,
            max_new_tokens=1024,
            temperature=0.1,    
            do_sample=True
        )

    output_ids = generated_ids[0][len(model_inputs.input_ids[0]):].tolist()

    try:
        delimiter_index = len(output_ids) - output_ids[::-1].index(151668)
        
        thinking_content = tokenizer.decode(output_ids[:delimiter_index], skip_special_tokens=True).strip()
        content = tokenizer.decode(output_ids[delimiter_index:], skip_special_tokens=True).strip()
    except ValueError:
        delimiter_index = 0
        thinking_content = "N/A (No thinking block found)"
        content = tokenizer.decode(output_ids, skip_special_tokens=True).strip()

    return thinking_content, content



def extract_entities_with_llm(query, vehicle_patterns, business_patterns, fallback_patterns, model_llm=[None, None]):
    if model_llm[0] is not None and model_llm[1] is not None:
        thinking_content, content = analyze_traffic_query(query, model_llm[0], model_llm[1])
        clean_json = content.replace("```json", "").replace("```", "").strip()
        extraction = json.loads(clean_json)
    else:
        client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            config= genai.types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT.format(vehicle_patterns, business_patterns, fallback_patterns),
                response_mime_type="application/json",
                temperature=0.0,
            ),
            contents=query
        )
        extraction = json.loads(response.text)

    return {"category": extraction['category'], "intent": extraction['intent']}



def log_results(results, logger=None):
    if logger is None:
        logger = logging.getLogger(__name__)
    for i,result in enumerate(results):
        logger.info(f"Top {i+1}: {result['score']:.4f}")
        logger.info(f"Description: {result['data']['text']}")
        logger.info(f"Category: {result['data']['category']}")
        logger.info(f"Fine: {result['data']['fine_min']} - {result['data']['fine_max']} VNĐ")
        logger.info(f"Law: {result['data']['law_article']}, {result['data']['law_clause']}")
        logger.info(f"Document: {result['data'].get('document', 'N/A')}")
        logger.info(f"Extra: {result['data']['extra']}")
        logger.info("--------------------------------")

def print_results(results):
    for i,result in enumerate(results):
        print(f"Top {i+1}: {result['score']:.4f}")
        print(f"Description: {result['data']['text']}")
        print(f"Category: {result['data']['category']}")
        print(f"Fine: {result['data']['fine_min']} - {result['data']['fine_max']} VNĐ")
        # print(f"Law: {result['data']['law_article']}, {result['data']['law_clause']}", f", {result['data']['law_point'] if result['data'].get('law_point') else ''}")
        print(f"Law: {result['data']['full_ref']}")
        print(f"Document: {result['data'].get('document', 'N/A')}")
        print(f"Extra: {result['data']['extra']}")
        print("--------------------------------")
