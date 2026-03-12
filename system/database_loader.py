import json
from neo4j import GraphDatabase
from sentence_transformers import SentenceTransformer

IMPORT_QUERY = """
// --- 1. Legal Hierarchy ---
MERGE (doc:LegalDocument {name: $doc_name})
MERGE (art:Article {name: $art_name})
MERGE (art)-[:PART_OF]->(doc)

MERGE (clause:Clause {name: $clause_name, full_ref: $full_ref})
MERGE (clause)-[:BELONGS_TO]->(art)

// --- 2. Vehicle / Category ---
// We treat the 'category' field as the Vehicle Type
MERGE (veh:VehicleType {name: $category})

// --- 3. The Violation (Central Node) ---
MERGE (vio:Violation {id: $vid})
SET vio.description = $desc,
    vio.severity = $severity,
    vio.embedding = $embedding  // <--- Vector stored here

MERGE (vio)-[:DEFINED_IN]->(clause)
MERGE (vio)-[:APPLIES_TO]->(veh)

// --- 4. The Fine ---
// We create a Fine node based on the values. 
// If multiple violations have the exact same fine range, they share this node.
MERGE (fine:Fine {min: $fine_min, max: $fine_max, currency: $currency})
MERGE (vio)-[:HAS_FINE]->(fine)

// --- 5. Additional Measures (Loop handling) ---
FOREACH (measure_text IN $additional_measures | 
    MERGE (sup:SupplementaryPenalty {text: measure_text})
    MERGE (vio)-[:HAS_ADDITIONAL_PENALTY]->(sup)
)
"""

class TrafficLawQADataLoader:
    def __init__(self, uri, auth, embedding_model="minhquan6203/paraphrase-vietnamese-law"):
        self.driver = GraphDatabase.driver(uri, auth=auth)
        self.model = SentenceTransformer(embedding_model)
        self.embedding_dimension = self.model.get_sentence_embedding_dimension()
        self.URI = uri
        self.AUTH = auth

    # 3. Create the Index
    def create_vector_index(self):
        query = """
        CREATE VECTOR INDEX violation_index IF NOT EXISTS
        FOR (v:Violation)
        ON (v.embedding)
        OPTIONS {indexConfig: {
        `vector.dimensions`: $dim,
        `vector.similarity_function`: 'cosine'
        }}
        """
        
        try:
            with self.driver.session() as session:
                session.run(query, dim=self.embedding_dimension)
                print("Success: Vector Index 'violation_index' created.")
        except Exception as e:
            print(f"Error: {e}")

    def import_data(self, tx, item):
        # Generate Vector Embedding for the description
        # This converts text meaning into numbers for the AI search
        vector = self.model.encode(item['description']).tolist()
        
        tx.run(IMPORT_QUERY, 
            # Mapping JSON fields to Cypher parameters
            vid=item['id'],
            desc=item['description'],
            severity=item.get('severity', 'Unknown'),
            embedding=vector,
            
            doc_name=item['legal_basis']['document'],
            art_name=item['legal_basis']['article'],
            clause_name=item['legal_basis']['section'],
            full_ref=item['legal_basis']['full_reference'],
            
            category=item['category'],
            
            fine_min=item['penalty']['fine_min'],
            fine_max=item['penalty']['fine_max'],
            currency=item['penalty']['currency'],
            
            additional_measures=item['additional_measures']
        )
    
        print(f"Data imported!!!!!!!!")
    
    def clear_database(self):
        with self.driver.session() as session:
            print("Deleting all nodes and relationships...")
            session.run("MATCH (n) DETACH DELETE n")
            print("Dropping old Vector Index...")
            session.run("DROP INDEX violation_index IF EXISTS")
            print("Database is completely empty and ready for new Schema.")