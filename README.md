# 🚦 Vietnamese Traffic Law Q&A System

An intelligent AI-powered traffic violation lookup system that combines **Vector Search** (Semantic search via AI Embeddings), **Knowledge Graph**, and a **Neo4j** database.

## 🏆 Key Features
- **Hybrid Search**: Leverages the `paraphrase-vietnamese-law` model for AI Vector search (BM25 + Semantic Search) combined with the powerful graph query capabilities of Neo4j.
- **Smart NLP Preprocessing**: Automatically detects vehicle types, violations, and extracts entities (e.g., vehicles, alcohol concentration, speed) directly from natural Vietnamese queries.
- **Production-ready Performance**: Lightning-fast retrieval (<0.5s) from over 1,000+ violation records derived from Decree 100/2019 and Decree 168/2024.
- **Cross-platform Interface**: Provides a Streamlit frontend suitable for administrators and a lightweight Vanilla HTML/CSS web client for end-users.

---

## 🚀 Quick Start

### 1. Prerequisites
- [Python 3.9+](https://www.python.org/downloads/) installed.
- Active internet connection (required for LLM models and API calls).

### 2. Installation

Clone the repository and install the required dependencies:

```bash
git clone https://github.com/vdt040499/traffic-law-qa.git
cd traffic-law-qa

# Create and activate a Virtual Environment
python -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows

# Install packages
pip install -r requirements.txt
```

### 3. Environment Configuration (`.env`)
Create a `.env` file in the root directory of the project and input your Neo4j Database and Gemini API credentials:

```ini
NEO4J_URI=neo4j+s://<your_database_address>
NEO4J_USER=neo4j
NEO4J_PASSWORD=<your_password>
GEMINI_API_KEY=<your_gemini_key>
```

*(Note: If you don't have accounts yet, you can register for a free database at [Neo4j Aura](https://console.neo4j.io) and get your API key from [Google AI Studio](https://aistudio.google.com/app/apikey)).*

### 4. Database Initialization
Run the loading scripts to create Vector Indexes and ingest the provided legal JSON data into your Neo4j instance (you only need to run these once):

```bash
# Create indexing structures for Neo4j
python create_indexes.py

# Load traffic violation data to the database
python load_neo4j_data.py
```

---

## 🖥 Running the System

### Option 1: Web Client Interface (For End-Users)
First, start the API Backend server on port 8000:
```bash
python src/traffic_law_qa/ui/api.py
```
Then, navigate to the `src/traffic_law_qa/ui/` directory and open the `index.html` file using any modern web browser (Google Chrome, Safari, etc.) to start using the app.

### Option 2: Streamlit Dashboard (For Admins)
Use Streamlit for analytics, data visualization, and assessing system performance:
```bash
streamlit run src/traffic_law_qa/ui/streamlit_app.py
```

### Option 3: Command Line Interface (CLI)
```bash
python system/main.py --query "How much is the fine for running a red light on a motorcycle?" --top-k 5
```

---

## 💡 Project Structure
```text
traffic-law-qa/
├── data/                       # Stores DOCX & JSON files for Decree 100, 168
├── src/traffic_law_qa/         
│   ├── nlp/                    # Tokenization and Entity Recognition for Vietnamese
│   └── ui/                     # Backend API & Frontend Web HTML
├── system/                     # Neo4j logic scripts and DB loader components
├── scripts/                    # Scripts for scraping and processing legal documents
├── .env.example                # Sample configuration file
└── run_streamlit.py            # Startup script for the UI
```

## ⚖️ Disclaimer
This system is powered by AI and aims to provide **reference materials only**. In all actual situations, please directly compare the information with the current Legal Documents and the official authorities of the State of Vietnam.
