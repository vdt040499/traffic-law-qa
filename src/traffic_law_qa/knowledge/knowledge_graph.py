"""
Knowledge Graph for Vietnamese Traffic Law System.
Implements knowledge representation: Behavior → Penalty → Law Article → Additional Measures
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple, Any
from enum import Enum
import json
import logging
from pathlib import Path
import networkx as nx
from datetime import datetime


class NodeType(Enum):
    """Types of nodes in the knowledge graph."""
    BEHAVIOR = "behavior"           # Hành vi vi phạm
    PENALTY = "penalty"             # Mức phạt
    LAW_ARTICLE = "law_article"     # Điều luật
    ADDITIONAL_MEASURE = "additional_measure"  # Hình thức bổ sung
    VEHICLE_TYPE = "vehicle_type"   # Loại phương tiện
    VIOLATION_CONTEXT = "violation_context"  # Bối cảnh vi phạm


class RelationType(Enum):
    """Types of relationships in the knowledge graph."""
    LEADS_TO_PENALTY = "leads_to_penalty"     # Hành vi → Mức phạt
    BASED_ON_LAW = "based_on_law"             # Mức phạt → Điều luật
    HAS_ADDITIONAL = "has_additional"         # Mức phạt → Hình thức bổ sung
    APPLIES_TO_VEHICLE = "applies_to_vehicle" # Hành vi → Loại phương tiện
    IN_CONTEXT = "in_context"                 # Hành vi → Bối cảnh
    SIMILAR_TO = "similar_to"                 # Hành vi ∼ Hành vi (tương đồng)


@dataclass
class KnowledgeNode:
    """Node in the knowledge graph."""
    id: str
    node_type: NodeType
    label: str
    properties: Dict[str, Any] = field(default_factory=dict)
    embeddings: Optional[List[float]] = None
    keywords: List[str] = field(default_factory=list)
    synonyms: List[str] = field(default_factory=list)
    
    def __hash__(self):
        return hash(self.id)


@dataclass
class KnowledgeRelation:
    """Relationship between nodes in the knowledge graph."""
    source_id: str
    target_id: str
    relation_type: RelationType
    weight: float = 1.0
    properties: Dict[str, Any] = field(default_factory=dict)


class TrafficLawKnowledgeGraph:
    """
    Knowledge Graph for Vietnamese Traffic Law.
    Represents relationships between behaviors, penalties, laws, and additional measures.
    """
    
    def __init__(self):
        self.graph = nx.MultiDiGraph()
        self.nodes: Dict[str, KnowledgeNode] = {}
        self.relations: List[KnowledgeRelation] = []
        self.embeddings_index: Dict[str, List[float]] = {}
        self.logger = logging.getLogger(__name__)
        
    def add_node(self, node: KnowledgeNode) -> None:
        """Add a node to the knowledge graph."""
        self.nodes[node.id] = node
        self.graph.add_node(
            node.id,
            node_type=node.node_type.value,
            label=node.label,
            properties=node.properties,
            keywords=node.keywords,
            synonyms=node.synonyms
        )
        
        if node.embeddings:
            self.embeddings_index[node.id] = node.embeddings
            
    def add_relation(self, relation: KnowledgeRelation) -> None:
        """Add a relationship to the knowledge graph."""
        if relation.source_id not in self.nodes or relation.target_id not in self.nodes:
            self.logger.warning(f"Cannot add relation: missing nodes {relation.source_id} or {relation.target_id}")
            return
            
        self.relations.append(relation)
        self.graph.add_edge(
            relation.source_id,
            relation.target_id,
            relation_type=relation.relation_type.value,
            weight=relation.weight,
            properties=relation.properties
        )
        
    def get_node(self, node_id: str) -> Optional[KnowledgeNode]:
        """Get a node by ID."""
        return self.nodes.get(node_id)
        
    def find_nodes_by_type(self, node_type: NodeType) -> List[KnowledgeNode]:
        """Find all nodes of a specific type."""
        return [node for node in self.nodes.values() if node.node_type == node_type]
        
    def find_nodes_by_keywords(self, keywords: List[str]) -> List[KnowledgeNode]:
        """Find nodes that match any of the given keywords."""
        matching_nodes = []
        keywords_lower = [kw.lower() for kw in keywords]
        
        for node in self.nodes.values():
            node_keywords = [kw.lower() for kw in node.keywords + node.synonyms]
            if any(kw in node_keywords for kw in keywords_lower):
                matching_nodes.append(node)
                
        return matching_nodes
        
    def get_behavior_penalty_chain(self, behavior_id: str) -> Dict[str, Any]:
        """
        Get the complete chain: Behavior → Penalty → Law Article → Additional Measures
        """
        if behavior_id not in self.nodes:
            return {}
            
        chain = {
            'behavior': self.nodes[behavior_id],
            'penalties': [],
            'law_articles': [],
            'additional_measures': []
        }
        
        # Find penalties
        penalty_edges = [(u, v, d) for u, v, d in self.graph.edges(behavior_id, data=True) 
                        if d.get('relation_type') == RelationType.LEADS_TO_PENALTY.value]
        
        for _, penalty_id, _ in penalty_edges:
            penalty_node = self.nodes[penalty_id]
            chain['penalties'].append(penalty_node)
            
            # Find law articles for this penalty
            law_edges = [(u, v, d) for u, v, d in self.graph.edges(penalty_id, data=True)
                        if d.get('relation_type') == RelationType.BASED_ON_LAW.value]
            
            for _, law_id, _ in law_edges:
                law_node = self.nodes[law_id]
                if law_node not in chain['law_articles']:
                    chain['law_articles'].append(law_node)
            
            # Find additional measures for this penalty
            additional_edges = [(u, v, d) for u, v, d in self.graph.edges(penalty_id, data=True)
                              if d.get('relation_type') == RelationType.HAS_ADDITIONAL.value]
            
            for _, additional_id, _ in additional_edges:
                additional_node = self.nodes[additional_id]
                if additional_node not in chain['additional_measures']:
                    chain['additional_measures'].append(additional_node)
                    
        return chain
        
    def find_similar_behaviors(self, behavior_id: str, limit: int = 5) -> List[Tuple[KnowledgeNode, float]]:
        """Find behaviors similar to the given behavior."""
        if behavior_id not in self.nodes:
            return []
            
        similar_behaviors = []
        
        # Find direct similarity relationships
        similar_edges = [(u, v, d) for u, v, d in self.graph.edges(behavior_id, data=True)
                        if d.get('relation_type') == RelationType.SIMILAR_TO.value]
        
        for _, similar_id, edge_data in similar_edges:
            similar_node = self.nodes[similar_id]
            weight = edge_data.get('weight', 0.0)
            similar_behaviors.append((similar_node, weight))
            
        # Sort by similarity weight and return top results
        similar_behaviors.sort(key=lambda x: x[1], reverse=True)
        return similar_behaviors[:limit]
        
    def query_knowledge_paths(self, start_node_id: str, end_node_types: List[NodeType], 
                            max_depth: int = 3) -> List[List[KnowledgeNode]]:
        """
        Find all paths from start node to nodes of specific types within max depth.
        """
        if start_node_id not in self.nodes:
            return []
            
        paths = []
        end_type_values = [nt.value for nt in end_node_types]
        
        def dfs_paths(current_id: str, path: List[str], depth: int):
            if depth > max_depth:
                return
                
            current_node = self.nodes[current_id]
            
            # Check if current node is a target type
            if current_node.node_type.value in end_type_values:
                node_path = [self.nodes[node_id] for node_id in path + [current_id]]
                paths.append(node_path)
                
            # Continue exploring
            if depth < max_depth:
                for neighbor in self.graph.successors(current_id):
                    if neighbor not in path:  # Avoid cycles
                        dfs_paths(neighbor, path + [current_id], depth + 1)
                        
        dfs_paths(start_node_id, [], 0)
        return paths
        
    def build_from_violations_data(self, violations_data: Dict[str, Any]) -> None:
        """
        Build knowledge graph from processed violations data.
        """
        self.logger.info("Building knowledge graph from violations data...")
        
        violations = violations_data.get('violations', [])
        
        for violation in violations:
            self._process_violation(violation)
            
        self._create_similarity_relations()
        self.logger.info(f"Knowledge graph built with {len(self.nodes)} nodes and {len(self.relations)} relations")
        
    def _process_violation(self, violation: Dict[str, Any]) -> None:
        """Process a single violation to create nodes and relations."""
        violation_id = str(violation.get('id', ''))
        description = violation.get('description', '')
        category = violation.get('category', '')
        
        # Create behavior node
        behavior_node = KnowledgeNode(
            id=f"behavior_{violation_id}",
            node_type=NodeType.BEHAVIOR,
            label=description,
            properties={
                'category': category,
                'original_id': violation_id,
                'full_description': description
            },
            keywords=self._extract_keywords(description)
        )
        self.add_node(behavior_node)
        
        # Process penalty information
        penalty_info = violation.get('penalty', {})
        if penalty_info:
            self._create_penalty_nodes(behavior_node.id, penalty_info, violation_id)
            
    def _create_penalty_nodes(self, behavior_id: str, penalty_info: Dict[str, Any], violation_id: str) -> None:
        """Create penalty-related nodes and relationships."""
        
        # Create penalty node
        fine_min = penalty_info.get('fine_min', 0)
        fine_max = penalty_info.get('fine_max', 0)
        penalty_text = penalty_info.get('penalty_text', '')
        
        penalty_id = f"penalty_{violation_id}"
        penalty_node = KnowledgeNode(
            id=penalty_id,
            node_type=NodeType.PENALTY,
            label=f"Phạt tiền từ {fine_min:,} đến {fine_max:,} VNĐ",
            properties={
                'fine_min': fine_min,
                'fine_max': fine_max,
                'penalty_text': penalty_text,
                'currency': 'VND'
            }
        )
        self.add_node(penalty_node)
        
        # Create relation: Behavior → Penalty
        penalty_relation = KnowledgeRelation(
            source_id=behavior_id,
            target_id=penalty_id,
            relation_type=RelationType.LEADS_TO_PENALTY,
            weight=1.0
        )
        self.add_relation(penalty_relation)
        
        # Create law article node
        legal_basis = penalty_info.get('legal_basis', '')
        if legal_basis:
            law_id = f"law_article_{violation_id}"
            law_node = KnowledgeNode(
                id=law_id,
                node_type=NodeType.LAW_ARTICLE,
                label=legal_basis,
                properties={
                    'legal_reference': legal_basis,
                    'document_type': self._extract_document_type(legal_basis)
                }
            )
            self.add_node(law_node)
            
            # Create relation: Penalty → Law Article
            law_relation = KnowledgeRelation(
                source_id=penalty_id,
                target_id=law_id,
                relation_type=RelationType.BASED_ON_LAW,
                weight=1.0
            )
            self.add_relation(law_relation)
            
        # Create additional measures nodes
        additional_measures = penalty_info.get('additional_measures', [])
        for i, measure in enumerate(additional_measures):
            if measure and measure.strip():
                measure_id = f"additional_{violation_id}_{i}"
                measure_node = KnowledgeNode(
                    id=measure_id,
                    node_type=NodeType.ADDITIONAL_MEASURE,
                    label=measure,
                    properties={'measure_text': measure}
                )
                self.add_node(measure_node)
                
                # Create relation: Penalty → Additional Measure
                measure_relation = KnowledgeRelation(
                    source_id=penalty_id,
                    target_id=measure_id,
                    relation_type=RelationType.HAS_ADDITIONAL,
                    weight=1.0
                )
                self.add_relation(measure_relation)
                
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text for indexing."""
        # Simple keyword extraction - can be enhanced with NLP
        import re
        
        # Remove special characters and split
        words = re.findall(r'\b\w+\b', text.lower())
        
        # Filter out common stop words
        stop_words = {'của', 'và', 'với', 'trong', 'trên', 'tại', 'để', 'cho', 'từ', 'khi', 'không', 'có', 'là', 'được'}
        keywords = [word for word in words if len(word) > 2 and word not in stop_words]
        
        return list(set(keywords))
        
    def _extract_document_type(self, legal_basis: str) -> str:
        """Extract document type from legal basis."""
        if 'Nghị định' in legal_basis or 'NĐ-CP' in legal_basis:
            return 'Nghị định'
        elif 'Luật' in legal_basis:
            return 'Luật'
        elif 'Thông tư' in legal_basis:
            return 'Thông tư'
        else:
            return 'Khác'
            
    def _create_similarity_relations(self) -> None:
        """Create similarity relations between behaviors based on keywords overlap."""
        behavior_nodes = self.find_nodes_by_type(NodeType.BEHAVIOR)
        
        for i, node1 in enumerate(behavior_nodes):
            for node2 in behavior_nodes[i+1:]:
                similarity = self._calculate_keyword_similarity(node1.keywords, node2.keywords)
                
                if similarity > 0.3:  # Threshold for similarity
                    # Create bidirectional similarity relations
                    rel1 = KnowledgeRelation(
                        source_id=node1.id,
                        target_id=node2.id,
                        relation_type=RelationType.SIMILAR_TO,
                        weight=similarity
                    )
                    rel2 = KnowledgeRelation(
                        source_id=node2.id,
                        target_id=node1.id,
                        relation_type=RelationType.SIMILAR_TO,
                        weight=similarity
                    )
                    self.add_relation(rel1)
                    self.add_relation(rel2)
                    
    def _calculate_keyword_similarity(self, keywords1: List[str], keywords2: List[str]) -> float:
        """Calculate Jaccard similarity between two keyword lists."""
        if not keywords1 or not keywords2:
            return 0.0
            
        set1 = set(keywords1)
        set2 = set(keywords2)
        
        intersection = set1.intersection(set2)
        union = set1.union(set2)
        
        return len(intersection) / len(union) if union else 0.0
        
    def export_graph(self, filepath: str) -> None:
        """Export knowledge graph to JSON file."""
        export_data = {
            'metadata': {
                'created_at': datetime.now().isoformat(),
                'total_nodes': len(self.nodes),
                'total_relations': len(self.relations),
                'node_types': {nt.value: len(self.find_nodes_by_type(nt)) for nt in NodeType}
            },
            'nodes': [
                {
                    'id': node.id,
                    'type': node.node_type.value,
                    'label': node.label,
                    'properties': node.properties,
                    'keywords': node.keywords,
                    'synonyms': node.synonyms
                }
                for node in self.nodes.values()
            ],
            'relations': [
                {
                    'source': rel.source_id,
                    'target': rel.target_id,
                    'type': rel.relation_type.value,
                    'weight': rel.weight,
                    'properties': rel.properties
                }
                for rel in self.relations
            ]
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
            
        self.logger.info(f"Knowledge graph exported to {filepath}")
        
    def get_statistics(self) -> Dict[str, Any]:
        """Get knowledge graph statistics."""
        node_type_counts = {}
        for node_type in NodeType:
            node_type_counts[node_type.value] = len(self.find_nodes_by_type(node_type))
            
        relation_type_counts = {}
        for relation_type in RelationType:
            count = sum(1 for rel in self.relations if rel.relation_type == relation_type)
            relation_type_counts[relation_type.value] = count
            
        return {
            'total_nodes': len(self.nodes),
            'total_relations': len(self.relations),
            'node_types': node_type_counts,
            'relation_types': relation_type_counts,
            'graph_density': nx.density(self.graph),
            'average_degree': sum(dict(self.graph.degree()).values()) / len(self.graph.nodes()) if self.graph.nodes() else 0
        }