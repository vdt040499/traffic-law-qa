# Vietnamese Traffic Law Q&A System - Project Instructions

This project is a semantic search system for Vietnamese traffic law violations and penalties.

## Project Overview
- **Domain**: Vietnamese Traffic Law (Luật Giao thông Việt Nam)
- **Technology**: Python, NLP, Semantic Search, Vector Database
- **Data Sources**: Nghị định 100/2019/NĐ-CP và các văn bản sửa đổi
- **Dataset**: 300+ traffic violations and penalty levels

## Key Components
1. **Legal Document Processing**: Extract and process Vietnamese traffic law documents
2. **Semantic Search Engine**: Understand similarity between violation descriptions
3. **Penalty Lookup System**: Return accurate fines, additional measures, and legal basis
4. **Natural Language Interface**: Handle complex Vietnamese queries
5. **Vector Database**: Store embeddings for semantic similarity matching

## Development Guidelines
- Use Vietnamese language processing capabilities
- Implement robust semantic search for legal text
- Ensure accurate penalty information retrieval
- Handle complex natural language violation descriptions
- Maintain legal document references and citations

## Technical Stack
- **Backend**: Python with FastAPI/Flask
- **NLP**: Transformers, sentence-transformers for Vietnamese
- **Vector DB**: Chroma/Pinecone for semantic search
- **Frontend**: Streamlit/Gradio for demo interface
- **Data**: JSON/CSV for violation database

## Legal Documents to Process
- Nghị định 100/2019/NĐ-CP (base regulation)
- Nghị định 123/2021/NĐ-CP (amendments)
- Nghị định 168/2024/NĐ-CP (latest amendments)