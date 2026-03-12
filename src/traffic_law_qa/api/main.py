"""FastAPI application for Traffic Law Q&A system."""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional

from ..core.config import get_settings, Settings
from ..data.models import QueryRequest, QueryResponse, TrafficViolation, ViolationType
from ..search.semantic_search import get_search_engine, SemanticSearchEngine

app = FastAPI(
    title="Vietnamese Traffic Law Q&A API",
    description="Semantic search API for Vietnamese traffic law violations and penalties",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize the application on startup."""
    settings = get_settings()
    search_engine = get_search_engine()
    
    # Load violations data
    search_engine.load_violations(settings.violations_data_path)
    
    # Generate embeddings if not already done
    if search_engine.embeddings is None:
        search_engine.generate_embeddings()


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Vietnamese Traffic Law Q&A API", "version": "0.1.0"}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.post("/search", response_model=QueryResponse)
async def search_violations(
    request: QueryRequest,
    search_engine: SemanticSearchEngine = Depends(get_search_engine)
) -> QueryResponse:
    """Search for traffic violations based on natural language query."""
    try:
        response = search_engine.process_query(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@app.get("/violations/{violation_id}", response_model=TrafficViolation)
async def get_violation(
    violation_id: str,
    search_engine: SemanticSearchEngine = Depends(get_search_engine)
) -> TrafficViolation:
    """Get a specific violation by ID."""
    violation = search_engine.get_violation_by_id(violation_id)
    if not violation:
        raise HTTPException(status_code=404, detail="Violation not found")
    return violation


@app.get("/violations/{violation_id}/similar")
async def get_similar_violations(
    violation_id: str,
    max_results: int = 5,
    search_engine: SemanticSearchEngine = Depends(get_search_engine)
):
    """Get violations similar to a specific violation."""
    similar = search_engine.get_similar_violations(violation_id, max_results)
    return {"violation_id": violation_id, "similar_violations": similar}


@app.get("/violations", response_model=List[TrafficViolation])
async def list_violations(
    violation_type: Optional[ViolationType] = None,
    limit: int = 50,
    offset: int = 0,
    search_engine: SemanticSearchEngine = Depends(get_search_engine)
) -> List[TrafficViolation]:
    """List all violations with optional filtering."""
    violations = search_engine.violations[offset:offset + limit]
    
    if violation_type:
        violations = [v for v in violations if v.violation_type == violation_type]
    
    return violations


@app.get("/stats")
async def get_statistics(
    search_engine: SemanticSearchEngine = Depends(get_search_engine)
):
    """Get system statistics."""
    total_violations = len(search_engine.violations)
    violation_types = {}
    
    for violation in search_engine.violations:
        vtype = violation.violation_type.value
        violation_types[vtype] = violation_types.get(vtype, 0) + 1
    
    return {
        "total_violations": total_violations,
        "violation_types": violation_types,
        "embeddings_generated": search_engine.embeddings is not None
    }


if __name__ == "__main__":
    import uvicorn
    settings = get_settings()
    uvicorn.run(app, host=settings.api_host, port=settings.api_port)