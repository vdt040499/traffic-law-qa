"""
Traffic Law QA System with Knowledge Graph and Semantic Reasoning.
Integrated system combining knowledge representation and semantic search.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

from .knowledge_graph import TrafficLawKnowledgeGraph, NodeType, KnowledgeNode
from .semantic_reasoning import SemanticReasoningEngine, IntentType


class TrafficLawQASystem:
    """
    Main QA system integrating knowledge graph and semantic reasoning.
    """
    
    def __init__(self, violations_data_path: str, 
                 sentence_model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"):
        """
        Initialize the QA system.
        
        Args:
            violations_data_path: Path to violations JSON data
            sentence_model_name: Name of sentence transformer model for Vietnamese
        """
        self.logger = logging.getLogger(__name__)
        
        # Store path to violations data for direct access
        self.violations_data_path = violations_data_path
        self.violations_data = None
        self.violations_by_id = {}  # For quick lookup
        
        # Initialize knowledge graph
        self.knowledge_graph = TrafficLawKnowledgeGraph()
        
        # Load and build knowledge graph
        self._load_violations_data(violations_data_path)
        
        # Initialize semantic reasoning engine
        self.reasoning_engine = SemanticReasoningEngine(
            self.knowledge_graph, 
            sentence_model_name
        )
        
        # Build embeddings index
        self.reasoning_engine.build_embeddings_index()
        
        self.logger.info("Traffic Law QA System initialized successfully")
        
    def _load_violations_data(self, data_path: str) -> None:
        """Load violations data and build knowledge graph."""
        try:
            with open(data_path, 'r', encoding='utf-8') as f:
                self.violations_data = json.load(f)
                
            # Build lookup dictionary for quick access
            violations = self.violations_data.get('violations', [])
            for violation in violations:
                violation_id = str(violation.get('id', ''))
                self.violations_by_id[violation_id] = violation
                
            self.knowledge_graph.build_from_violations_data(self.violations_data)
            self.logger.info(f"Loaded {len(violations)} violations")
            
        except Exception as e:
            self.logger.error(f"Failed to load violations data: {e}")
            raise
            
    def ask_question(self, question: str, max_results: int = 5, 
                    similarity_threshold: float = 0.6) -> Dict[str, Any]:
        """
        Ask a question about traffic law and get comprehensive answer.
        
        Args:
            question: User's question in Vietnamese
            max_results: Maximum number of results to return
            similarity_threshold: Minimum similarity score for results
            
        Returns:
            Comprehensive answer with reasoning and citations
        """
        try:
            # Process query using semantic reasoning
            raw_results = self.reasoning_engine.process_query(
                question, 
                max_results=max_results,
                similarity_threshold=similarity_threshold
            )
            
            # Format results for user presentation
            formatted_results = self._format_results(raw_results)
            
            return formatted_results
            
        except Exception as e:
            self.logger.error(f"Error processing question '{question}': {e}")
            return self._create_error_response(question, str(e))
            
    def _format_results(self, raw_results: Dict[str, Any]) -> Dict[str, Any]:
        """Format raw results for user-friendly presentation."""
        
        if not raw_results.get('has_definitive_answer', False):
            return {
                'question': raw_results['query'],
                'answer': raw_results.get('message', 'Không tìm thấy thông tin phù hợp.'),
                'confidence': 'low',
                'citations': [],
                'additional_info': {
                    'suggestions': raw_results.get('suggestions', []),
                    'intent': raw_results.get('intent', {}),
                    'processing_time': raw_results.get('processing_time', 0)
                }
            }
            
        # Format definitive answers
        results = raw_results.get('results', [])
        if not results:
            return self._create_no_data_response(raw_results['query'])
            
        primary_result = results[0]
        
        # Build comprehensive answer
        answer_parts = []
        citations = []
        
        # Extract information from reasoning path
        behavior_info = None
        penalty_info = []
        law_info = []
        additional_measures = []
        
        for path_node in primary_result.get('reasoning_path', []):
            if path_node['type'] == 'behavior':
                behavior_info = path_node
            elif path_node['type'] == 'penalty':
                penalty_info.append(path_node)
            elif path_node['type'] == 'law_article':
                law_info.append(path_node)
            elif path_node['type'] == 'additional_measure':
                additional_measures.append(path_node)
                
        # Build answer text
        if behavior_info:
            answer_parts.append(f"**Hành vi vi phạm:** {behavior_info['label']}")
            
        if penalty_info:
            for penalty in penalty_info:
                fine_min = penalty['properties'].get('fine_min', 0)
                fine_max = penalty['properties'].get('fine_max', 0)
                if fine_min > 0 and fine_max > 0:
                    answer_parts.append(f"**Mức phạt:** {fine_min:,} - {fine_max:,} VNĐ")
                elif penalty.get('label'):
                    answer_parts.append(f"**Mức phạt:** {penalty['label']}")
                    
        if additional_measures:
            measures_text = []
            for measure in additional_measures:
                measures_text.append(f"- {measure['label']}")
            if measures_text:
                answer_parts.append(f"**Biện pháp bổ sung:**\n" + "\n".join(measures_text))
                
        if law_info:
            for law in law_info:
                legal_ref = law['properties'].get('legal_reference', law['label'])
                citations.append({
                    'source': legal_ref,
                    'type': 'legal_document',
                    'relevance': 'high'
                })
                
        # Combine answer parts
        main_answer = "\n\n".join(answer_parts) if answer_parts else "Đã tìm thấy thông tin liên quan."
        
        # Add similar cases if available - including the primary result for UI display
        similar_cases = []
        all_results_to_process = [primary_result] + results[1:4] if len(results) > 1 else [primary_result]
        
        for result in all_results_to_process:
            behavior_data = result.get('behavior', {})
            
            # Get original violation data using the behavior ID
            original_id = behavior_data.get('id', '').replace('behavior_', '') if behavior_data.get('id', '').startswith('behavior_') else behavior_data.get('id', '')
            
            # Try to find the original violation data
            original_violation = None
            if original_id in self.violations_by_id:
                original_violation = self.violations_by_id[original_id]
            else:
                # Fallback: search by description match
                description = behavior_data.get('description', '')
                if description and self.violations_data:
                    for violation in self.violations_data.get('violations', []):
                        if violation.get('description', '').strip() == description.strip():
                            original_violation = violation
                            break
            
            # Default values
            legal_basis = {}
            penalty_data = {}
            additional_measures = []
            
            if original_violation:
                # Extract legal basis from original data
                legal_basis_data = original_violation.get('legal_basis', {})
                if legal_basis_data:
                    legal_basis = {
                        'document': legal_basis_data.get('document', 'N/A'),
                        'article': legal_basis_data.get('article', 'N/A'),
                        'section': legal_basis_data.get('section', 'N/A'),
                        'full_reference': legal_basis_data.get('full_reference', 'N/A')
                    }
                
                # Extract penalty information
                penalty_info = original_violation.get('penalty', {})
                if penalty_info:
                    penalty_data = {
                        'fine_min': penalty_info.get('fine_min', 0),
                        'fine_max': penalty_info.get('fine_max', 0),
                        'currency': penalty_info.get('currency', 'VNĐ'),
                        'fine_text': penalty_info.get('fine_text', 'N/A')
                    }
                
                # Extract additional measures
                additional_measures = original_violation.get('additional_measures', [])
                
                # Use original violation data for other fields too
                description = original_violation.get('description', behavior_data.get('description', 'N/A'))
                category = original_violation.get('category', behavior_data.get('category', 'N/A'))
            else:
                # Fallback to behavior data
                description = behavior_data.get('description', 'N/A')
                category = behavior_data.get('category', 'N/A')
            
            similar_case = {
                'description': description,
                'similarity': result.get('similarity_score', 0.0),
                'category': category,
                'legal_basis': legal_basis,
                'penalty': penalty_data,
                'additional_measures': additional_measures
            }
            
            similar_cases.append(similar_case)
                
        confidence_level = 'high' if primary_result['similarity_score'] > 0.8 else 'medium'
        
        return {
            'question': raw_results['query'],
            'answer': main_answer,
            'confidence': confidence_level,
            'similarity_score': primary_result['similarity_score'],
            'intent': raw_results.get('intent', {}),
            'citations': citations,
            'similar_cases': similar_cases,
            'additional_info': {
                'matched_entities': primary_result.get('matched_entities', []),
                'processing_time': raw_results.get('processing_time', 0),
                'total_results_found': raw_results.get('total_results', 0)
            }
        }
        
    def _create_error_response(self, question: str, error_msg: str) -> Dict[str, Any]:
        """Create error response."""
        return {
            'question': question,
            'answer': f"Xin lỗi, đã xảy ra lỗi khi xử lý câu hỏi: {error_msg}",
            'confidence': 'error',
            'citations': [],
            'additional_info': {
                'error': True,
                'error_message': error_msg
            }
        }
        
    def _create_no_data_response(self, question: str) -> Dict[str, Any]:
        """Create response when no data is found."""
        return {
            'question': question,
            'answer': "**Không biết / Không có dữ liệu**\n\nHệ thống không tìm thấy thông tin phù hợp với câu hỏi của bạn. Vui lòng thử:\n- Diễn đạt câu hỏi khác cách\n- Cung cấp thêm chi tiết về hành vi vi phạm\n- Sử dụng từ khóa chính xác hơn",
            'confidence': 'none',
            'citations': [],
            'additional_info': {
                'no_data': True,
                'suggestions': [
                    'Thử sử dụng từ khóa khác',
                    'Mô tả hành vi cụ thể hơn',
                    'Kiểm tra chính tả'
                ]
            }
        }
        
    def get_violation_by_behavior(self, behavior_description: str) -> Optional[Dict[str, Any]]:
        """Get violation information by behavior description."""
        results = self.ask_question(behavior_description, max_results=1)
        
        if results.get('confidence') in ['high', 'medium']:
            return results
        return None
        
    def find_similar_violations(self, behavior_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Find violations similar to given behavior."""
        similar_behaviors = self.reasoning_engine.get_similar_behaviors(behavior_id, limit)
        
        similar_violations = []
        for behavior_node, similarity in similar_behaviors:
            chain = self.knowledge_graph.get_behavior_penalty_chain(behavior_node.id)
            
            violation_info = {
                'behavior': behavior_node.label,
                'similarity_score': similarity,
                'category': behavior_node.properties.get('category', ''),
                'penalties': [],
                'legal_basis': []
            }
            
            # Extract penalty information
            for penalty in chain.get('penalties', []):
                fine_min = penalty.properties.get('fine_min', 0)
                fine_max = penalty.properties.get('fine_max', 0)
                violation_info['penalties'].append({
                    'fine_range': f"{fine_min:,} - {fine_max:,} VNĐ" if fine_min and fine_max else penalty.label
                })
                
            # Extract legal basis
            for law in chain.get('law_articles', []):
                violation_info['legal_basis'].append(law.label)
                
            similar_violations.append(violation_info)
            
        return similar_violations
        
    def get_system_statistics(self) -> Dict[str, Any]:
        """Get system statistics and health information."""
        kg_stats = self.knowledge_graph.get_statistics()
        
        return {
            'knowledge_graph': kg_stats,
            'system_info': {
                'total_violations': kg_stats['node_types'].get('behavior', 0),
                'embedding_model': 'paraphrase-multilingual-MiniLM-L12-v2',
                'embeddings_cached': len(self.reasoning_engine.embeddings_cache),
                'last_updated': datetime.now().isoformat()
            },
            'capabilities': {
                'intent_detection': True,
                'entity_extraction': True,
                'semantic_search': True,
                'knowledge_reasoning': True,
                'vietnamese_nlp': True
            }
        }
        
    def export_knowledge_graph(self, filepath: str) -> None:
        """Export knowledge graph to file."""
        self.knowledge_graph.export_graph(filepath)
        
    def benchmark_system(self, test_queries: List[str]) -> Dict[str, Any]:
        """Benchmark system performance with test queries."""
        results = {
            'total_queries': len(test_queries),
            'successful_answers': 0,
            'average_processing_time': 0.0,
            'confidence_distribution': {'high': 0, 'medium': 0, 'low': 0, 'none': 0},
            'intent_distribution': {},
            'query_results': []
        }
        
        total_time = 0.0
        
        for query in test_queries:
            start_time = datetime.now()
            
            try:
                answer = self.ask_question(query)
                processing_time = (datetime.now() - start_time).total_seconds()
                total_time += processing_time
                
                # Update statistics
                confidence = answer.get('confidence', 'none')
                results['confidence_distribution'][confidence] += 1
                
                if confidence in ['high', 'medium']:
                    results['successful_answers'] += 1
                    
                intent_type = answer.get('intent', {}).get('type', 'unknown')
                results['intent_distribution'][intent_type] = results['intent_distribution'].get(intent_type, 0) + 1
                
                results['query_results'].append({
                    'query': query,
                    'confidence': confidence,
                    'processing_time': processing_time,
                    'intent': intent_type
                })
                
            except Exception as e:
                self.logger.error(f"Benchmark error for query '{query}': {e}")
                results['query_results'].append({
                    'query': query,
                    'error': str(e),
                    'processing_time': (datetime.now() - start_time).total_seconds()
                })
                
        results['average_processing_time'] = total_time / len(test_queries) if test_queries else 0.0
        results['success_rate'] = results['successful_answers'] / len(test_queries) if test_queries else 0.0
        
        return results