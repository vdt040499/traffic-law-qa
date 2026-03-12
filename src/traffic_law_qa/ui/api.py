# api.py
import os
import json
import sys
from pathlib import Path
from typing import Optional 

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

# Lấy thư mục gốc của project
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))




def remove_duplicates(input_list):
    """
    Loại bỏ trùng lặp và giữ nguyên thứ tự.
    """
    if not input_list:
        return []
    return list(dict.fromkeys(input_list))


# --------- KHỞI TẠO FastAPI App ----------
app = FastAPI(
    title="Vietnamese Traffic Law Search API",
    description="Hybrid (vector + BM25) search trên Neo4j cho luật giao thông",
    version="1.0.0",
)

# Cho phép gọi từ web tĩnh (Vercel/localhost/…)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],         
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------- LOAD DETECTOR ----------
global_detector = None
global_patterns = None

def get_detector_patterns():
    global global_detector, global_patterns
    if global_detector is None:
        from scripts.category_detector import VehicleCategoryDetector
        global_detector = VehicleCategoryDetector()
        global_patterns = (
            [k for k in global_detector.vehicle_patterns],
            [k for k in global_detector.business_patterns],
            [k for k in global_detector.fallback_categories]
        )
    return global_patterns


# ---------  Neo4j database connection ----------
from dotenv import load_dotenv
load_dotenv()

NEO4J_URI  = os.getenv("NEO4J_URI", "neo4j+s://7aa78485.databases.neo4j.io")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASS = os.getenv("NEO4J_PASSWORD", "iX59KTgWRNyZvmkh3dDBGe0Dwbm-_XQGdP1KCW_m7rs")

global_model = None

def get_model():
    global global_model
    if global_model is None:
        print("Đang khởi tạo AI Model và tải dữ liệu (có thể mất một lúc)...")
        from system.model import Model
        global_model = Model(uri=NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))
    return global_model


# API /search receive JSON include: question, top_k, verbose
class SearchRequest(BaseModel):
    question: str
    top_k: int = 10
    verbose: bool = False
    document_name: Optional[str]


@app.post("/search")
def search(req: SearchRequest):
    """
    Nhận câu hỏi tiếng Việt tự nhiên, trả về danh sách điều luật phù hợp.
    """
    # Dùng LLM để bóc tách intent & category (chỉ để trả về cho frontend)
    from system.utils import extract_entities_with_llm
    vehicle_patterns, business_patterns, fallback_patterns = get_detector_patterns()
    extraction = extract_entities_with_llm(
        req.question,
        vehicle_patterns,
        business_patterns,
        fallback_patterns,
    )
    target_category = extraction.get("category")
    query_intent = extraction.get("intent")

    # Khởi tạo mô hình (Lazy Load)
    current_model = get_model()

    # Gọi hybrid_search để lấy kết quả
    raw_results = current_model.hybrid_search(
        req.question,
        vehicle_patterns,
        business_patterns,
        fallback_patterns,
        top_k=req.top_k,
        verbose=req.verbose,
        decree_filter=req.document_name
    )
    

    article2category = {}
    if req.document_name == "ND168":
        with open(project_root / "data" / "processed" / "article2category_ND168.json", "r") as f:
            article2category = json.load(f)
    elif req.document_name == "ND100":
        with open(project_root / "data" / "processed" / "article2category_ND100.json", "r") as f:
            article2category = json.load(f)
            
    for result in raw_results:
        # Use .get() to prevent KeyError on unknown articles
        result['data']['category'] = article2category.get(result['data']['law_article'], "Chung/Không xác định")
        
        if result['data']['document'] == "ND168":
            result['data']['document'] = "Nghị định 168/2024/NĐ-CP"
        elif result['data']['document'] == "ND100":
            result['data']['document'] = "Nghị định 100/2019/NĐ-CP"
            
        result['data']['extra'] = remove_duplicates(result['data']['extra'])
    print('raw_results: ', raw_results)


    # hybrid_search trả về list các phần tử:
    # { "data": item, "score": tổng RRF }
    # trong đó item có: id, text, category, fine_min, fine_max, law_article, law_clause, extra, vector_score/bm25_score
    results = []
    for r in raw_results:
        data = r["data"]
        score = float(r["score"])
        fine_min = data.get("fine_min")
        fine_max = data.get("fine_max")

        if fine_min is not None and fine_max is not None:
            fine_text = f"{fine_min:,} - {fine_max:,} VNĐ".replace(",", ".")
        elif fine_min is not None:
            fine_text = f"Tối thiểu {fine_min:,} VNĐ".replace(",", ".")
        else:
            fine_text = ""

        # Extract law_point from full_ref if available
        law_point = None
        full_ref = data.get("full_ref", "")
        if full_ref and "Điểm" in full_ref:
            # Extract "Điểm x" from full_ref (e.g., "Nghị định 168/2024/NĐ-CP, Điều 6, Khoản 5, Điểm p")
            parts = full_ref.split(", ")
            for part in parts:
                if part.startswith("Điểm"):
                    law_point = part
                    break

        # print("req.document_name: ", req.document_name)
        # print('results: ', results)
        results.append(
            {
                "id": data.get("id"),
                "description": data.get("text"),
                "vehicle_category": data.get("category"),
                "fine_min": fine_min,
                "fine_max": fine_max,
                "fine_text": fine_text,
                "law_article": data.get("law_article"),
                "law_clause": data.get("law_clause"),
                "law_point": law_point,
                "extra_penalties": data.get("extra") or [],
                "score": score,
            }
        )

    return {
        "query": req.question,
        "detected_category": target_category,
        "detected_intent": query_intent,
        "document_filter": req.document_name,
        "results": results,
    }


@app.get("/stats")
def get_stats():
    # Gọi hàm dummy hoặc trả về cấu trúc mà UI mong đợi
    return {
        "neo4j_version": "5.14.0",
        "nodes": {"Article": 0, "Clause": 0, "Point": 0, "VehicleType": 0, "Fine": 0},
        "relationships": 0,
        "graph_density": 0.05
    }

@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/", response_class=HTMLResponse)
def serve_frontend():
    """
    Trả về giao diện index.html trực tiếp tại đường dẫn gốc.
    """
    html_path = project_root / "src" / "traffic_law_qa" / "ui" / "index.html"
    try:
        with open(html_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "<h1>File index.html không tồn tại!</h1>"



if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    # Trên server (như Render) thì reload=False, port được lấy ở môi trường
    uvicorn.run("src.traffic_law_qa.ui.api:app", host="0.0.0.0", port=port, reload=False)

