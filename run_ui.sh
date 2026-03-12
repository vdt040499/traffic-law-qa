conda activate traffic_law 

# Search query example 
cd vietnamese-traffic-law-qa-master/
python system/main.py --query "không đội mũ bảo hiểm khi đi xe máy thì phạt bao nhiêu?"

# Chạy đồng thời 
# 1. Terminal 1: Backend: FastAPI
conda activate traffic_law 
cd src/traffic_law_qa/ui
export NEO4J_URI="neo4j+s://7aa78485.databases.neo4j.io"
export NEO4J_USER="neo4j"
export NEO4J_PASS="iX59KTgWRNyZvmkh3dDBGe0Dwbm-_XQGdP1KCW_m7rs"
python3 -m uvicorn api:app --host 0.0.0.0 --port 8000 --reload

# 2. Terminal 2: Frontend: Static website (HTML + CSS + JS)
conda activate traffic_law 
cd src/traffic_law_qa/ui
python3 -m http.server 5500




'''
Web UI = Static website (HTML + CSS + JS)
Backend = FastAPI (Python)
Giao tiếp = REST API → /search
'''
┌─────────────────┐
│  Browser        │
│  localhost:5500 │  ← Static HTML/CSS/JS
└────────┬────────┘
         │ HTTP POST
         │ /search
         ▼
┌─────────────────┐
│  FastAPI        │
│  localhost:8000 │  ← Python backend
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Neo4j Database │  ← Graph database
└─────────────────┘

'''
