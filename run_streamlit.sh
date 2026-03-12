#!/bin/bash
# Launch script for Vietnamese Traffic Law QA Streamlit UI

cd "$(dirname "$0")"

echo "🚦 Starting Vietnamese Traffic Law QA System..."
echo "================================================"
echo ""
echo "System: Neo4j-based Hybrid Search (Vector + BM25)"
echo "UI: Streamlit Web Interface"
echo ""
echo "Once started, the app will be available at:"
echo "  🌐 http://localhost:8501"
echo ""
echo "================================================"
echo ""

# Run Streamlit
streamlit run src/traffic_law_qa/ui/streamlit_app.py

