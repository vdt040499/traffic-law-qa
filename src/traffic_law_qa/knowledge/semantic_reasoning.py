"""
Semantic Reasoning Engine for Vietnamese Traffic Law QA System.
Implements intent analysis, entity extraction, and semantic search.
"""

from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass
import logging
import re
import json
from datetime import datetime
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import openai

from .knowledge_graph import TrafficLawKnowledgeGraph, NodeType, KnowledgeNode


class IntentType:
    """Types of user intents."""
    PENALTY_INQUIRY = "penalty_inquiry"         # Hỏi về mức phạt
    LAW_REFERENCE = "law_reference"             # Hỏi về điều luật
    BEHAVIOR_CHECK = "behavior_check"           # Kiểm tra hành vi có vi phạm không
    SIMILAR_CASES = "similar_cases"             # Tìm các trường hợp tương tự
    ADDITIONAL_MEASURES = "additional_measures" # Hỏi về biện pháp bổ sung
    GENERAL_INFO = "general_info"               # Thông tin chung
    UNKNOWN = "unknown"                         # Không xác định được


@dataclass
class Entity:
    """Extracted entity from user query."""
    text: str
    entity_type: str
    start: int
    end: int
    confidence: float = 1.0


@dataclass
class Intent:
    """Detected user intent."""
    intent_type: str
    confidence: float
    entities: List[Entity]


@dataclass
class SemanticSearchResult:
    """Result from semantic search."""
    node: KnowledgeNode
    similarity_score: float
    matched_entities: List[Entity]
    reasoning_path: List[KnowledgeNode]


class VietnameseNLPProcessor:
    """Vietnamese NLP processor for traffic law domain."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Traffic law specific patterns
        self.penalty_patterns = [
            r'phạt\s+(?:bao nhiêu|mức nào|như thế nào)',
            r'mức\s+phạt',
            r'tiền\s+phạt',
            r'bị\s+phạt',
            r'phạt\s+(?:tiền|how much)',
        ]
        
        self.law_patterns = [
            r'điều\s+\d+',
            r'khoản\s+\d+',
            r'nghị\s+định',
            r'luật\s+giao\s+thông',
            r'quy\s+định',
            r'theo\s+luật'
        ]
        
        self.behavior_patterns = [
            r'có\s+được\s+(?:phép|không)',
            r'có\s+vi\s+phạm\s+không',
            r'được\s+(?:phép|không)',
            r'có\s+bị\s+phạt\s+không',
            r'hành\s+vi\s+này',
            r'trường\s+hợp\s+này'
        ]
        
        # Entity patterns
        self.vehicle_patterns = [
            r'(?:xe\s+máy|motorbike|motor)',
            r'(?:xe\s+hơi|ô\s+tô|car)',
            r'(?:xe\s+tải|truck)',
            r'(?:xe\s+buýt|bus)',
            r'(?:xe\s+đạp|bicycle)',
            r'(?:container)',
            r'(?:xe\s+khách)'
        ]
        
        self.speed_patterns = [
            r'(\d+)\s*(?:km/h|kmh|km)',
            r'tốc\s+độ\s+(\d+)',
            r'vượt\s+quá\s+(\d+)',
            r'chạy\s+(\d+)'
        ]
        
        self.alcohol_patterns = [
            r'(\d+(?:\.\d+)?)\s*(?:mg/l|mg)',
            r'nồng\s+độ\s+cồn\s+(\d+(?:\.\d+)?)',
            r'say\s+rượu',
            r'uống\s+rượu',
            r'cồn'
        ]
        
    def detect_intent(self, query: str) -> Intent:
        """Detect user intent from query."""
        query_lower = query.lower()
        entities = self.extract_entities(query)
        
        # Check for penalty inquiry
        if any(re.search(pattern, query_lower) for pattern in self.penalty_patterns):
            return Intent(
                intent_type=IntentType.PENALTY_INQUIRY,
                confidence=0.9,
                entities=entities
            )
            
        # Check for law reference
        if any(re.search(pattern, query_lower) for pattern in self.law_patterns):
            return Intent(
                intent_type=IntentType.LAW_REFERENCE,
                confidence=0.8,
                entities=entities
            )
            
        # Check for behavior check
        if any(re.search(pattern, query_lower) for pattern in self.behavior_patterns):
            return Intent(
                intent_type=IntentType.BEHAVIOR_CHECK,
                confidence=0.8,
                entities=entities
            )
            
        # Check for similar cases
        if any(keyword in query_lower for keyword in ['tương tự', 'giống', 'như', 'trường hợp khác']):
            return Intent(
                intent_type=IntentType.SIMILAR_CASES,
                confidence=0.7,
                entities=entities
            )
            
        # Default to general info
        return Intent(
            intent_type=IntentType.GENERAL_INFO,
            confidence=0.5,
            entities=entities
        )
        
    def extract_entities(self, query: str) -> List[Entity]:
        """Extract entities from query."""
        entities = []
        
        # Extract vehicle types
        for pattern in self.vehicle_patterns:
            matches = re.finditer(pattern, query, re.IGNORECASE)
            for match in matches:
                entities.append(Entity(
                    text=match.group(),
                    entity_type="VEHICLE",
                    start=match.start(),
                    end=match.end(),
                    confidence=0.9
                ))
                
        # Extract speeds
        for pattern in self.speed_patterns:
            matches = re.finditer(pattern, query, re.IGNORECASE)
            for match in matches:
                entities.append(Entity(
                    text=match.group(),
                    entity_type="SPEED",
                    start=match.start(),
                    end=match.end(),
                    confidence=0.9
                ))
                
        # Extract alcohol levels
        for pattern in self.alcohol_patterns:
            matches = re.finditer(pattern, query, re.IGNORECASE)
            for match in matches:
                entities.append(Entity(
                    text=match.group(),
                    entity_type="ALCOHOL",
                    start=match.start(),
                    end=match.end(),
                    confidence=0.8
                ))
                
        return entities
        
    def preprocess_query(self, query: str) -> str:
        """Preprocess Vietnamese query for better matching."""
        # Remove diacritics normalization
        # Normalize whitespace
        query = re.sub(r'\s+', ' ', query.strip())
        
        # Handle common misspellings and variations
        replacements = {
            'xe máy': 'xe_may',
            'ô tô': 'o_to',
            'xe hơi': 'o_to',
            'tốc độ': 'toc_do',
            'phạt tiền': 'phat_tien',
            'vi phạm': 'vi_pham',
            'nồng độ cồn': 'nong_do_con'
        }
        
        for old, new in replacements.items():
            query = query.replace(old, new)
            
        return query


class SemanticReasoningEngine:
    """
    Semantic reasoning engine using sentence embeddings and knowledge graph.
    """
    
    def __init__(self, knowledge_graph: TrafficLawKnowledgeGraph, 
                 model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"):
        self.knowledge_graph = knowledge_graph
        self.nlp_processor = VietnameseNLPProcessor()
        self.logger = logging.getLogger(__name__)
        
        # Load sentence transformer model
        try:
            self.sentence_model = SentenceTransformer(model_name)
            self.logger.info(f"Loaded sentence transformer model: {model_name}")
        except Exception as e:
            self.logger.error(f"Failed to load sentence transformer: {e}")
            self.sentence_model = None
            
        # Cache for embeddings
        self.embeddings_cache: Dict[str, np.ndarray] = {}
        
    def process_query(self, query: str, max_results: int = 10, 
                     similarity_threshold: float = 0.5) -> Dict[str, Any]:
        """
        Process user query and return comprehensive results.
        """
        start_time = datetime.now()
        
        # Step 1: Intent detection and entity extraction
        intent = self.nlp_processor.detect_intent(query)
        self.logger.info(f"Detected intent: {intent.intent_type} (confidence: {intent.confidence})")
        
        # Step 2: Preprocess query
        processed_query = self.nlp_processor.preprocess_query(query)
        
        # Step 3: Semantic search
        search_results = self.semantic_search(
            processed_query, 
            max_results=max_results,
            similarity_threshold=similarity_threshold
        )
        
        # Step 4: Reasoning and path finding
        reasoned_results = []
        for result in search_results:
            if result.node.node_type == NodeType.BEHAVIOR:
                # Get complete chain: Behavior → Penalty → Law → Additional Measures
                chain = self.knowledge_graph.get_behavior_penalty_chain(result.node.id)
                result.reasoning_path = self._build_reasoning_path(chain)
                
            reasoned_results.append(result)
            
        # Step 5: Handle unknown cases
        if not reasoned_results or max(r.similarity_score for r in reasoned_results) < similarity_threshold:
            return self._handle_unknown_query(query, intent)
            
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return {
            'query': query,
            'processed_query': processed_query,
            'intent': {
                'type': intent.intent_type,
                'confidence': intent.confidence,
                'entities': [
                    {
                        'text': e.text,
                        'type': e.entity_type,
                        'confidence': e.confidence
                    }
                    for e in intent.entities
                ]
            },
            'results': [
                {
                    'behavior': {
                        'id': r.node.id,
                        'description': r.node.label,
                        'category': r.node.properties.get('category', ''),
                        'keywords': r.node.keywords
                    },
                    'similarity_score': r.similarity_score,
                    'reasoning_path': [
                        {
                            'type': node.node_type.value,
                            'label': node.label,
                            'properties': node.properties
                        }
                        for node in r.reasoning_path
                    ],
                    'matched_entities': [
                        {'text': e.text, 'type': e.entity_type}
                        for e in r.matched_entities
                    ]
                }
                for r in reasoned_results
            ],
            'total_results': len(reasoned_results),
            'processing_time': processing_time,
            'has_definitive_answer': len(reasoned_results) > 0 and reasoned_results[0].similarity_score > 0.7
        }
        
    def semantic_search(self, query: str, max_results: int = 10, 
                       similarity_threshold: float = 0.5) -> List[SemanticSearchResult]:
        """
        Perform semantic search using sentence embeddings.
        """
        if not self.sentence_model:
            return self._fallback_keyword_search(query, max_results)
            
        # Get query embedding
        query_embedding = self._get_query_embedding(query)
        if query_embedding is None:
            return self._fallback_keyword_search(query, max_results)
            
        # Get node embeddings and calculate similarities
        similarities = []
        behavior_nodes = self.knowledge_graph.find_nodes_by_type(NodeType.BEHAVIOR)
        
        for node in behavior_nodes:
            node_embedding = self._get_node_embedding(node)
            if node_embedding is not None:
                similarity = cosine_similarity([query_embedding], [node_embedding])[0][0]
                
                if similarity >= similarity_threshold:
                    # Extract matched entities
                    matched_entities = self._find_matched_entities(query, node)
                    
                    similarities.append(SemanticSearchResult(
                        node=node,
                        similarity_score=float(similarity),
                        matched_entities=matched_entities,
                        reasoning_path=[]
                    ))
                    
        # Sort by similarity score
        similarities.sort(key=lambda x: x.similarity_score, reverse=True)
        return similarities[:max_results]
        
    def _get_query_embedding(self, query: str) -> Optional[np.ndarray]:
        """Get embedding for query."""
        if query in self.embeddings_cache:
            return self.embeddings_cache[query]
            
        try:
            embedding = self.sentence_model.encode([query])[0]
            self.embeddings_cache[query] = embedding
            return embedding
        except Exception as e:
            self.logger.error(f"Failed to get query embedding: {e}")
            return None
            
    def _get_node_embedding(self, node: KnowledgeNode) -> Optional[np.ndarray]:
        """Get embedding for knowledge graph node."""
        cache_key = f"node_{node.id}"
        if cache_key in self.embeddings_cache:
            return self.embeddings_cache[cache_key]
            
        try:
            # Use node label and keywords for embedding
            text = f"{node.label} {' '.join(node.keywords)}"
            embedding = self.sentence_model.encode([text])[0]
            self.embeddings_cache[cache_key] = embedding
            return embedding
        except Exception as e:
            self.logger.error(f"Failed to get node embedding for {node.id}: {e}")
            return None
            
    def _find_matched_entities(self, query: str, node: KnowledgeNode) -> List[Entity]:
        """Find entities in query that match node keywords."""
        matched_entities = []
        query_lower = query.lower()
        
        for keyword in node.keywords:
            if keyword.lower() in query_lower:
                start = query_lower.find(keyword.lower())
                if start != -1:
                    matched_entities.append(Entity(
                        text=keyword,
                        entity_type="KEYWORD",
                        start=start,
                        end=start + len(keyword),
                        confidence=0.8
                    ))
                    
        return matched_entities
        
    def _build_reasoning_path(self, chain: Dict[str, Any]) -> List[KnowledgeNode]:
        """Build reasoning path from behavior chain."""
        path = []
        
        # Add behavior
        if 'behavior' in chain:
            path.append(chain['behavior'])
            
        # Add penalties
        for penalty in chain.get('penalties', []):
            path.append(penalty)
            
        # Add law articles
        for law in chain.get('law_articles', []):
            path.append(law)
            
        # Add additional measures
        for measure in chain.get('additional_measures', []):
            path.append(measure)
            
        return path
        
    def _fallback_keyword_search(self, query: str, max_results: int) -> List[SemanticSearchResult]:
        """Fallback to keyword-based search when semantic search fails."""
        self.logger.warning("Using fallback keyword search")
        
        # Extract keywords from query
        keywords = re.findall(r'\b\w+\b', query.lower())
        keywords = [kw for kw in keywords if len(kw) > 2]
        
        # Find matching nodes
        matching_nodes = self.knowledge_graph.find_nodes_by_keywords(keywords)
        
        results = []
        for node in matching_nodes[:max_results]:
            # Calculate simple keyword overlap score
            node_keywords = [kw.lower() for kw in node.keywords]
            overlap = len(set(keywords) & set(node_keywords))
            score = overlap / max(len(keywords), len(node_keywords)) if keywords and node_keywords else 0
            
            if score > 0:
                results.append(SemanticSearchResult(
                    node=node,
                    similarity_score=score,
                    matched_entities=[],
                    reasoning_path=[]
                ))
                
        results.sort(key=lambda x: x.similarity_score, reverse=True)
        return results
        
    def _handle_unknown_query(self, query: str, intent: Intent) -> Dict[str, Any]:
        """Handle queries that don't match any known violations."""
        return {
            'query': query,
            'intent': {
                'type': intent.intent_type,
                'confidence': intent.confidence,
                'entities': []
            },
            'results': [],
            'total_results': 0,
            'processing_time': 0.0,
            'has_definitive_answer': False,
            'message': 'Không biết / Không có dữ liệu. Hệ thống không tìm thấy thông tin phù hợp với câu hỏi của bạn.',
            'suggestions': [
                'Hãy thử diễn đạt câu hỏi khác cách',
                'Cung cấp thêm chi tiết về hành vi vi phạm',
                'Sử dụng từ khóa chính xác hơn'
            ]
        }
        
    def build_embeddings_index(self) -> None:
        """Build embeddings index for all behavior nodes."""
        if not self.sentence_model:
            self.logger.warning("Cannot build embeddings index: sentence model not available")
            return
            
        self.logger.info("Building embeddings index for knowledge graph...")
        behavior_nodes = self.knowledge_graph.find_nodes_by_type(NodeType.BEHAVIOR)
        
        texts = []
        node_ids = []
        
        for node in behavior_nodes:
            text = f"{node.label} {' '.join(node.keywords)}"
            texts.append(text)
            node_ids.append(node.id)
            
        if texts:
            try:
                embeddings = self.sentence_model.encode(texts)
                
                for i, node_id in enumerate(node_ids):
                    cache_key = f"node_{node_id}"
                    self.embeddings_cache[cache_key] = embeddings[i]
                    
                self.logger.info(f"Built embeddings for {len(texts)} behavior nodes")
            except Exception as e:
                self.logger.error(f"Failed to build embeddings index: {e}")
                
    def get_similar_behaviors(self, behavior_id: str, limit: int = 5) -> List[Tuple[KnowledgeNode, float]]:
        """Get behaviors similar to the given behavior using semantic similarity."""
        if behavior_id not in self.knowledge_graph.nodes:
            return []
            
        behavior_node = self.knowledge_graph.nodes[behavior_id]
        behavior_embedding = self._get_node_embedding(behavior_node)
        
        if behavior_embedding is None:
            # Fallback to knowledge graph similarity
            return self.knowledge_graph.find_similar_behaviors(behavior_id, limit)
            
        similar_behaviors = []
        behavior_nodes = self.knowledge_graph.find_nodes_by_type(NodeType.BEHAVIOR)
        
        for node in behavior_nodes:
            if node.id == behavior_id:
                continue
                
            node_embedding = self._get_node_embedding(node)
            if node_embedding is not None:
                similarity = cosine_similarity([behavior_embedding], [node_embedding])[0][0]
                similar_behaviors.append((node, float(similarity)))
                
        similar_behaviors.sort(key=lambda x: x[1], reverse=True)
        return similar_behaviors[:limit]