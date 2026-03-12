"""
Adapter to integrate Neo4j-based Model with Streamlit UI.
Provides a compatible interface with TrafficLawQASystem.
"""

from typing import Dict, List, Any, Optional
from system.model import Model
from scripts.category_detector import VehicleCategoryDetector
import logging


class Neo4jQAAdapter:
    """
    Adapter that wraps the Neo4j Model to provide a compatible interface
    with the Streamlit UI expectations.
    """
    
    def __init__(self, neo4j_uri: str, neo4j_auth: tuple, 
                 embedding_model: str = "minhquan6203/paraphrase-vietnamese-law"):
        """
        Initialize the adapter with Neo4j connection details.
        
        Args:
            neo4j_uri: Neo4j database URI
            neo4j_auth: Tuple of (username, password)
            embedding_model: Sentence transformer model name
        """
        self.logger = logging.getLogger(__name__)
        
        # Initialize the Neo4j Model
        self.model = Model(uri=neo4j_uri, auth=neo4j_auth, embedding_model=embedding_model)
        
        # Initialize category detector for pattern extraction
        self.detector = VehicleCategoryDetector()
        self.vehicle_patterns = [keywords for keywords in self.detector.vehicle_patterns]
        self.business_patterns = [keywords for keywords in self.detector.business_patterns]
        self.fallback_patterns = [keywords for keywords in self.detector.fallback_categories]
        
        # Store system info
        self.embedding_model = embedding_model
        self.neo4j_uri = neo4j_uri
        
        self.logger.info("Neo4j QA Adapter initialized successfully")
    
    def ask_question(self, question: str, max_results: int = 5, 
                    ) -> Dict[str, Any]:
        """
        Ask a question and get formatted results compatible with Streamlit UI.
        
        Args:
            question: User's question in Vietnamese
            max_results: Maximum number of results to return
            similarity_threshold: Minimum similarity score (for compatibility, not used in RRF)
            
        Returns:
            Formatted results dict compatible with Streamlit UI expectations
        """
        try:
            # Call the hybrid search
            raw_results = self.model.hybrid_search(
                query=question,
                vehicle_patterns=self.vehicle_patterns,
                business_patterns=self.business_patterns,
                fallback_patterns=self.fallback_patterns,
                top_k=max_results,
                verbose=False
            )
            
            # Format results for Streamlit UI
            formatted_results = self._format_for_ui(question, raw_results)
            
            return formatted_results
            
        except Exception as e:
            self.logger.error(f"Error processing question '{question}': {e}")
            return self._create_error_response(question, str(e))
    
    def _format_for_ui(self, question: str, results: List[Dict]) -> Dict[str, Any]:
        """Convert Model results to Streamlit UI format."""
        
        if not results or len(results) == 0:
            return {
                'confidence': 'none',
                'similarity_score': 0.0,
                'intent': {'type': 'unknown', 'text': question},
                'answer': 'Không tìm thấy thông tin phù hợp với câu hỏi của bạn. Vui lòng thử diễn đạt lại hoặc hỏi chi tiết hơn.',
                'similar_cases': [],
                'citations': [],
                'additional_info': {
                    'total_results_found': 0,
                    'matched_entities': [],
                    'suggestions': [
                        'Hãy thử mô tả vi phạm cụ thể hơn',
                        'Sử dụng các từ khóa như: vượt đèn đỏ, không đội mũ bảo hiểm, uống rượu bia, quá tốc độ'
                    ]
                }
            }
        
        # Get top result for main answer
        top_result = results[0]
        top_score = top_result['score']
        top_data = top_result['data']
        
        # Determine confidence based on RRF score
        # RRF scores typically range from 0.01 to 0.03 for good matches
        if top_score >= 0.025:
            confidence = 'high'
        elif top_score >= 0.018:
            confidence = 'medium'
        elif top_score >= 0.012:
            confidence = 'low'
        else:
            confidence = 'none'
        
        # Build similar cases list
        similar_cases = []
        for result in results:
            data = result['data']
            
            # Format penalty information
            fine_min = data.get('fine_min', 0)
            fine_max = data.get('fine_max', 0)
            penalty_info = {
                'fine_min': fine_min,
                'fine_max': fine_max,
                'currency': 'VNĐ',
                'fine_text': f"{fine_min:,} - {fine_max:,} VNĐ" if fine_min and fine_max else 'Chưa có thông tin'
            }
            
            # Format legal basis
            legal_basis = {
                'document': data.get('law_article', 'N/A').split('-')[0].strip() if data.get('law_article') else 'N/A',
                'article': data.get('law_article', 'N/A'),
                'section': data.get('law_clause', 'N/A'),
                'full_reference': f"{data.get('law_article', 'N/A')} - {data.get('law_clause', 'N/A')}"
            }
            
            # Extract additional measures from extra field
            extra = data.get('extra', [])
            additional_measures = extra if isinstance(extra, list) else [extra] if extra else []
            # Filter out empty strings
            additional_measures = [m for m in additional_measures if m]
            
            case = {
                'description': data.get('text', ''),
                'category': data.get('category', 'N/A'),
                'similarity': result['score'],
                'penalty': penalty_info,
                'legal_basis': legal_basis,
                'additional_measures': additional_measures
            }
            similar_cases.append(case)
        
        # Build main answer text
        answer = self._generate_answer(top_data, confidence)
        
        # Build citations list
        citations = []
        if top_data.get('law_article'):
            citations.append({
                'source': f"{top_data.get('law_article')} - {top_data.get('law_clause', '')}",
                'type': 'legal_document'
            })
        
        # Determine intent type
        text_lower = question.lower()
        if any(word in text_lower for word in ['bao nhiêu', 'mức phạt', 'phạt', 'tiền']):
            intent_type = 'penalty_inquiry'
        elif any(word in text_lower for word in ['có bị', 'có phải', 'được không']):
            intent_type = 'legality_check'
        else:
            intent_type = 'general_inquiry'
        
        return {
            'confidence': confidence,
            'similarity_score': top_score,
            'intent': {
                'type': intent_type,
                'text': question
            },
            'answer': answer,
            'similar_cases': similar_cases,
            'citations': citations,
            'additional_info': {
                'total_results_found': len(results),
                'matched_entities': [],
                'suggestions': []
            }
        }
    
    def _generate_answer(self, data: Dict, confidence: str) -> str:
        """Generate natural language answer from data."""
        
        if confidence == 'none':
            return "Không tìm thấy thông tin chính xác. Vui lòng thử lại với câu hỏi cụ thể hơn."
        
        description = data.get('text', 'Vi phạm không xác định')
        fine_min = data.get('fine_min', 0)
        fine_max = data.get('fine_max', 0)
        law_article = data.get('law_article', 'N/A')
        law_clause = data.get('law_clause', 'N/A')
        extra = data.get('extra', [])
        
        # Build answer
        answer_parts = []
        
        # Description
        answer_parts.append(f"**Vi phạm:** {description}")
        
        # Penalty
        if fine_min and fine_max:
            answer_parts.append(f"\n**💰 Mức phạt:** {fine_min:,} - {fine_max:,} VNĐ")
        else:
            answer_parts.append(f"\n**💰 Mức phạt:** Chưa có thông tin cụ thể")
        
        # Legal basis
        if law_article != 'N/A' and law_clause != 'N/A':
            answer_parts.append(f"\n**⚖️ Căn cứ pháp lý:** {law_article} - {law_clause}")
        
        # Additional measures
        if extra and isinstance(extra, list) and len([e for e in extra if e]) > 0:
            measures = [m for m in extra if m]
            answer_parts.append(f"\n**🚫 Biện pháp bổ sung:**")
            for measure in measures[:3]:  # Show top 3
                answer_parts.append(f"  • {measure}")
        
        return "\n".join(answer_parts)
    
    def _create_error_response(self, question: str, error_msg: str) -> Dict[str, Any]:
        """Create error response."""
        return {
            'confidence': 'error',
            'similarity_score': 0.0,
            'intent': {'type': 'unknown', 'text': question},
            'answer': f'Đã xảy ra lỗi khi xử lý câu hỏi: {error_msg}',
            'similar_cases': [],
            'citations': [],
            'additional_info': {
                'total_results_found': 0,
                'matched_entities': [],
                'error': error_msg
            }
        }
    
    def get_system_statistics(self) -> Dict[str, Any]:
        """
        Get system statistics compatible with Streamlit UI.
        Returns mock statistics for compatibility.
        """
        return {
            'knowledge_graph': {
                'total_nodes': 0,  # Neo4j doesn't expose this easily
                'total_relations': 0,
                'node_types': {
                    'behavior': 0,  # Would need separate query
                    'penalty': 0,
                    'law_article': 0,
                    'additional_measure': 0
                },
                'relation_types': {},
                'graph_density': 0.0,
                'average_degree': 0.0
            },
            'system_info': {
                'embedding_model': self.embedding_model,
                'embeddings_cached': 'N/A',
                'last_updated': 'N/A',
                'capabilities': {
                    'intent_detection': True,
                    'entity_extraction': True,
                    'semantic_search': True,
                    'knowledge_reasoning': True,
                    'vietnamese_nlp': True,
                    'hybrid_search': True,
                    'neo4j_backend': True
                }
            }
        }
    
    def benchmark_system(self, queries: List[str]) -> Dict[str, Any]:
        """
        Run benchmark tests on the system.
        
        Args:
            queries: List of test queries
            
        Returns:
            Benchmark results
        """
        import time
        
        results = []
        processing_times = []
        confidence_dist = {'high': 0, 'medium': 0, 'low': 0, 'none': 0, 'error': 0}
        intent_dist = {}
        successful = 0
        
        for query in queries:
            start = time.time()
            result = self.ask_question(query, max_results=5)
            elapsed = time.time() - start
            
            processing_times.append(elapsed)
            confidence = result.get('confidence', 'none')
            confidence_dist[confidence] = confidence_dist.get(confidence, 0) + 1
            
            intent_type = result.get('intent', {}).get('type', 'unknown')
            intent_dist[intent_type] = intent_dist.get(intent_type, 0) + 1
            
            if confidence in ['high', 'medium']:
                successful += 1
            
            results.append({
                'query': query,
                'confidence': confidence,
                'similarity_score': result.get('similarity_score', 0),
                'processing_time': f"{elapsed:.3f}s",
                'results_found': result.get('additional_info', {}).get('total_results_found', 0)
            })
        
        return {
            'total_queries': len(queries),
            'successful_answers': successful,
            'success_rate': successful / len(queries) if queries else 0,
            'average_processing_time': sum(processing_times) / len(processing_times) if processing_times else 0,
            'confidence_distribution': confidence_dist,
            'intent_distribution': intent_dist,
            'query_results': results
        }
    
    # Stub methods for compatibility with Streamlit UI
    @property
    def knowledge_graph(self):
        """Stub property for compatibility."""
        class StubKG:
            def find_nodes_by_type(self, node_type):
                return []
            def get_behavior_penalty_chain(self, behavior_id):
                return None
        return StubKG()
    
    @property
    def reasoning_engine(self):
        """Stub property for compatibility."""
        class StubReasoning:
            def get_similar_behaviors(self, behavior_id, limit=5):
                return []
        return StubReasoning()

