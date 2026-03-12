from neo4j import GraphDatabase
from system.utils import extract_entities_with_llm
from sentence_transformers import SentenceTransformer
import re

def escape_lucene_query(text):
    r"""
    Escape special characters for Lucene fulltext search.
    Special characters: + - && || ! ( ) { } [ ] ^ " ~ * ? : \ /
    """
    # List of special characters that need to be escaped
    special_chars = r'[\+\-\&\|\!\(\)\{\}\[\]\^\"\~\*\?\:\\/]'
    # Escape each special character with a backslash
    escaped = re.sub(special_chars, r'\\\g<0>', text)
    return escaped

class Model:
    def __init__(self, uri, auth, embedding_model="minhquan6203/paraphrase-vietnamese-law"):
        self.model = SentenceTransformer(embedding_model)
        self.uri = uri
        self.auth = auth
        self.embedding_model = embedding_model

    def vector_search(self, query, vehicle_patterns, business_patterns, fallback_patterns, model_llm=[None, None], decree_filter=None, top_k=10, verbose=False):
        driver = GraphDatabase.driver(self.uri, auth=self.auth)
        extraction = extract_entities_with_llm(query, vehicle_patterns, business_patterns, fallback_patterns, model_llm)
        target_category = extraction['category']
        query_intent = extraction['intent']
        if query_intent == None:
            print("Không biết.")
            return []
        vector = self.model.encode(f"query: {query_intent}").tolist()
        category_filters = []
        if isinstance(target_category, list):
            category_filters = [c.capitalize() for c in target_category if c]
        elif target_category:
            category_filters = [target_category.capitalize()]
        print(f"🔍 Filter: {category_filters or 'All'} | Search: {query} | Intent: {query_intent}")
        vector_query_template = """
        CALL db.index.vector.queryNodes('violation_index', {vector_limit}, $embedding)
        YIELD node, score
        {filters} 
        MATCH (node)-[:HAS_FINE]->(fine:Fine)
        MATCH (node)-[:APPLIES_TO]->(veh:VehicleType)
        MATCH (node)-[:DEFINED_IN]->(clause:Clause)-[:BELONGS_TO]->(article:Article)-[:PART_OF]->(doc:LegalDocument)
        OPTIONAL MATCH (node)-[:HAS_ADDITIONAL_PENALTY]->(sup:SupplementaryPenalty)
        
        RETURN node.id as id, 
            node.description as text, 
            veh.name as category, 
            fine.min as fine_min, 
            fine.max as fine_max, 
            article.name as law_article, 
            clause.name as law_clause, 
            doc.name as document,
            collect(sup.text) as extra, 
            score as vector_score
        """
        with driver.session() as session:
            category_clause = ""
            vec_params = {"embedding": vector}
            vec_results = session.run(vector_query_template.format(category_filter=category_clause), **vec_params).data()
            if category_filters and not vec_results:
                print("⚠️ No matches in filtered category. Falling back to full database.")
                vec_results = session.run(vector_query_template.format(category_filter=""), **vec_params).data()
        final_scores = {}
        for rank, item in enumerate(vec_results):
            doc_id = item['id']
            final_scores[doc_id] = {"data": item, "score": item['score']}
        sorted_results = sorted(final_scores.values(), key=lambda x: x['score'], reverse=True)
        return sorted_results[:top_k]

    def hybrid_search(self, query, vehicle_patterns, business_patterns, fallback_patterns, model_llm=[None, None], decree_filter=None, top_k=10, verbose=False):
        driver = GraphDatabase.driver(self.uri, auth=self.auth)
        extraction = extract_entities_with_llm(query, vehicle_patterns, business_patterns, fallback_patterns, model_llm)
        target_category = extraction['category']
        query_intent = extraction['intent']

        if query_intent == None:
            print("Không biết.")
            return []

        vector = self.model.encode(f"query: {query_intent}").tolist()
        category_filters = []
        if isinstance(target_category, list):
            category_filters = [c.capitalize() for c in target_category if c]
        elif target_category:
            category_filters = [target_category.capitalize()]
        
        # Display filters
        filter_info = []
        if category_filters:
            filter_info.append(f"Category: {category_filters}")
        print(f"🔍 Filter: {' | '.join(filter_info) if filter_info else 'All'} | Search: {query} | Intent: {query_intent}")
        # 1. Vector Search (Semantic)
        # When using document filter, fetch more results to ensure some match the filter
        vector_limit = 50
        
        vector_query_template = """
        CALL db.index.vector.queryNodes('violation_index', {vector_limit}, $embedding)
        YIELD node, score
        MATCH (node)-[:DEFINED_IN]->(clause:Clause)-[:BELONGS_TO]->(article:Article)-[:PART_OF]->(doc:LegalDocument)
        {filters} 
        MATCH (node)-[:HAS_FINE]->(fine:Fine)
        MATCH (node)-[:APPLIES_TO]->(veh:VehicleType)
        OPTIONAL MATCH (node)-[:HAS_ADDITIONAL_PENALTY]->(sup:SupplementaryPenalty)
        
        RETURN node.id as id, 
            node.description as text, 
            veh.name as category, 
            fine.min as fine_min, 
            fine.max as fine_max, 
            article.name as law_article, 
            clause.name as law_clause, 
            clause.full_ref as full_ref,
            doc.name as document,
            collect(sup.text) as extra, 
            score as vector_score
        """

        # 2. Keyword Search (BM25 - Lexical)
        keyword_limit = 50
        
        keyword_query_template = """
        CALL db.index.fulltext.queryNodes("violation_text_index", $text) 
        YIELD node, score
        MATCH (node)-[:DEFINED_IN]->(clause:Clause)-[:BELONGS_TO]->(article:Article)-[:PART_OF]->(doc:LegalDocument)
        {filters}
        MATCH (node)-[:HAS_FINE]->(fine:Fine)
        MATCH (node)-[:APPLIES_TO]->(veh:VehicleType)
        OPTIONAL MATCH (node)-[:HAS_ADDITIONAL_PENALTY]->(sup:SupplementaryPenalty)
        
        RETURN node.id as id, 
            node.description as text, 
            veh.name as category, 
            fine.min as fine_min, 
            fine.max as fine_max, 
            article.name as law_article, 
            clause.name as law_clause, 
            clause.full_ref as full_ref,
            doc.name as document,
            collect(sup.text) as extra, 
            score as bm25_score
        LIMIT {keyword_limit}
        """
        
        
        def run_queries(session, filter_clause, extra_params=None):
            extra_params = extra_params or {}
            vector_query = vector_query_template.format(vector_limit=vector_limit, filters=filter_clause)
            keyword_query = keyword_query_template.format(keyword_limit=keyword_limit, filters=filter_clause)
            escaped_query_intent = escape_lucene_query(query_intent)
            vec_params = {"embedding": vector, **extra_params}
            kw_params = {"text": escaped_query_intent, **extra_params}
            vec_results_local = session.run(vector_query, **vec_params).data()
            kw_results_local = session.run(keyword_query, **kw_params).data()
            return vec_results_local, kw_results_local
        
        with driver.session() as session:
            # Build filter clause
            filter_conditions = []
            params = {}
            
            if decree_filter:
                filter_conditions.append("doc.name = $decree_id")
                params["decree_id"] = decree_filter

            # if category_filters:
            #     filter_conditions.append("EXISTS { (node)-[:APPLIES_TO]->(v:VehicleType) WHERE v.name IN $categories }")
            #     params["categories"] = category_filters
            
            # Tạo mệnh đề WHERE
            filter_clause = "WHERE " + " AND ".join(filter_conditions) if filter_conditions else ""
            
            if verbose:
                print(f"Debug: filter_clause = '{filter_clause}'")
                print(f"Debug: params = {params}")
            
            vec_results, kw_results = run_queries(session, filter_clause, params)
            
            # Debug: Show how many results found with filter
            if verbose and filter_conditions:
                print(f"Debug: Vector results with filter: {len(vec_results)}")
                print(f"Debug: Keyword results with filter: {len(kw_results)}")
            
            if filter_conditions and not vec_results and not kw_results:
                print("⚠️ No matches with current filters. Falling back to full database.")
                vec_results, kw_results = run_queries(session, "", None)
            
        # 3. RRF Fusion (Merge results)
        final_scores = {}
        k = 60 # Constant used
        
        if verbose:
            print("--------------------------------")
        # Add score from Vector List
        for rank, item in enumerate(vec_results):
            doc_id = item['id']
            if doc_id not in final_scores: final_scores[doc_id] = {"data": item, "score": 0}
            final_scores[doc_id]["score"] += 1 / (k + rank + 1)
            if verbose:
                print(f"Rank {rank+1}: id={item['id']} - Text: {item['text']} - Vector Score: {final_scores[doc_id]['score']:.4f}")
        
        if verbose:
            print("--------------------------------")
        # Add score from Keyword List
        for rank, item in enumerate(kw_results):
            doc_id = item['id']
            if doc_id not in final_scores: final_scores[doc_id] = {"data": item, "score": 0}
            # If item appears in both lists, the score will be very high
            final_scores[doc_id]["score"] += 1 / (k + rank + 1)
            if verbose:
                print(f"Rank {rank+1}: id={item['id']} - Text: {item['text']} - BM25 Score: {final_scores[doc_id]['score']:.4f}")
        
        if verbose:
            print("--------------------------------")
        # 4. Sort and get Top results
        sorted_results = sorted(final_scores.values(), key=lambda x: x['score'], reverse=True)
        return sorted_results[:top_k]
    
