"""Core configuration and settings for the Traffic Law Q&A system."""

import os
from typing import Optional
from pydantic import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Application settings
    app_name: str = "Vietnamese Traffic Law Q&A"
    version: str = "0.1.0"
    debug: bool = False
    
    # API settings
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    # Database settings
    vector_db_path: str = "./data/embeddings/chroma_db"
    violations_data_path: str = "./data/processed/violations_100.json"
    
    # NLP Model settings
    embedding_model: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    vietnamese_model: str = "vinai/phobert-base"
    max_sequence_length: int = 512
    
    # Search settings
    max_search_results: int = 10
    similarity_threshold: float = 0.7
    
    # Legal document settings
    legal_docs_path: str = "./data/raw/legal_documents"
    processed_docs_path: str = "./data/processed"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings."""
    return settings