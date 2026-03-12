"""Data models for traffic violations and penalties."""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from enum import Enum


class ViolationType(Enum):
    """Types of traffic violations."""
    SPEED = "speed"
    PARKING = "parking"
    ALCOHOL = "alcohol"
    DOCUMENT = "document"
    VEHICLE = "vehicle"
    TRAFFIC_SIGNAL = "traffic_signal"
    LANE = "lane"
    OTHER = "other"


class PenaltyType(Enum):
    """Types of penalties."""
    FINE = "fine"
    LICENSE_SUSPENSION = "license_suspension"
    VEHICLE_IMPOUND = "vehicle_impound"
    WARNING = "warning"


@dataclass
class Penalty:
    """Penalty information for a violation."""
    fine_amount_min: int
    fine_amount_max: int
    additional_measures: List[str]
    additional_penalties: Optional[List[str]] = None
    legal_basis: str
    penalty_type: PenaltyType = PenaltyType.FINE


@dataclass
class TrafficViolation:
    """Traffic violation data model."""
    id: str
    description: str
    violation_type: ViolationType
    penalty: Penalty
    keywords: List[str]
    legal_reference: str
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


@dataclass
class SearchResult:
    """Search result for a violation query."""
    violation: TrafficViolation
    similarity_score: float
    matched_keywords: List[str]


@dataclass
class QueryRequest:
    """Request model for violation queries."""
    query: str
    max_results: int = 10
    similarity_threshold: float = 0.7
    violation_types: Optional[List[ViolationType]] = None


@dataclass
class QueryResponse:
    """Response model for violation queries."""
    query: str
    results: List[SearchResult]
    total_results: int
    processing_time: float