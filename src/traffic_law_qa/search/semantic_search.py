"""Semantic search engine for traffic violations."""

import json
import time
from typing import List, Optional, Dict, Any
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from ..data.models import TrafficViolation, SearchResult, QueryRequest, QueryResponse
from ..nlp.vietnamese_processor import get_vietnamese_processor


class SemanticSearchEngine:
    """Semantic search engine for traffic law violations."""
    
    def __init__(self, model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"):
        """Initialize the semantic search engine."""
        self.model_name = model_name
        self.model = None
        self.violations: List[TrafficViolation] = []
        self.embeddings: Optional[np.ndarray] = None
        self.vietnamese_processor = get_vietnamese_processor()
        
    def load_model(self):
        """Load the sentence transformer model."""
        if self.model is None:
            self.model = SentenceTransformer(self.model_name)
    
    def load_violations(self, violations_path: str):
        """Load traffic violations from JSON file."""
        try:
            with open(violations_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.violations = [TrafficViolation(**v) for v in data]
        except FileNotFoundError:
            print(f"Violations file not found: {violations_path}")
            self.violations = []
    
    def generate_embeddings(self) -> np.ndarray:
        """Generate embeddings for all violation descriptions."""
        if not self.violations:
            return np.array([])
        
        self.load_model()
        
        # Preprocess descriptions for better embeddings
        descriptions = []
        for violation in self.violations:
            processed_desc = self.vietnamese_processor.preprocess_for_embedding(violation.description)
            # Combine with keywords for richer representation
            keywords_text = ' '.join(violation.keywords)
            full_text = f"{processed_desc} {keywords_text}"
            descriptions.append(full_text)
        
        # Generate embeddings
        self.embeddings = self.model.encode(descriptions, convert_to_tensor=False)
        return self.embeddings
    
    def search(self, query: str, max_results: int = 10, similarity_threshold: float = 0.7) -> List[SearchResult]:
        """Search for violations matching the query."""
        if not self.violations or self.embeddings is None:
            return []
        
        self.load_model()
        
        # Preprocess query
        processed_query = self.vietnamese_processor.preprocess_for_embedding(query)
        
        # Generate query embedding
        query_embedding = self.model.encode([processed_query])
        
        # Calculate similarities
        similarities = cosine_similarity(query_embedding, self.embeddings)[0]
        
        # Get top results above threshold
        results = []
        for i, similarity in enumerate(similarities):
            if similarity >= similarity_threshold:
                # Extract matched keywords
                query_keywords = set(self.vietnamese_processor.extract_keywords(query))
                violation_keywords = set(self.violations[i].keywords)
                matched_keywords = list(query_keywords.intersection(violation_keywords))
                
                result = SearchResult(
                    violation=self.violations[i],
                    similarity_score=float(similarity),
                    matched_keywords=matched_keywords
                )
                results.append(result)
        
        # Sort by similarity score
        results.sort(key=lambda x: x.similarity_score, reverse=True)
        
        return results[:max_results]
    
    def process_query(self, request: QueryRequest) -> QueryResponse:
        """Process a search query and return formatted response."""
        start_time = time.time()
        
        results = self.search(
            query=request.query,
            max_results=request.max_results,
            similarity_threshold=request.similarity_threshold
        )
        
        # Filter by violation types if specified
        if request.violation_types:
            results = [r for r in results if r.violation.violation_type in request.violation_types]
        
        processing_time = time.time() - start_time
        
        return QueryResponse(
            query=request.query,
            results=results,
            total_results=len(results),
            processing_time=processing_time
        )
    
    def get_violation_by_id(self, violation_id: str) -> Optional[TrafficViolation]:
        """Get a specific violation by ID."""
        for violation in self.violations:
            if violation.id == violation_id:
                return violation
        return None
    
    def get_similar_violations(self, violation_id: str, max_results: int = 5) -> List[SearchResult]:
        """Find violations similar to a given violation."""
        violation = self.get_violation_by_id(violation_id)
        if not violation:
            return []
        
        return self.search(
            query=violation.description,
            max_results=max_results + 1,  # +1 to exclude the original
            similarity_threshold=0.5
        )[1:]  # Skip the first result (original violation)


# Global search engine instance
search_engine = SemanticSearchEngine()


def get_search_engine() -> SemanticSearchEngine:
    """Get semantic search engine instance."""
    return search_engine