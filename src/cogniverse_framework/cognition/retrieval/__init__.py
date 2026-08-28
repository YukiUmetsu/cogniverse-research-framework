"""Gap-driven memory retrieval contracts."""

from .controller import InMemoryRetrievalController, RetrievalSessionResult
from .gap_detection import detect_cognitive_gaps
from .gaps import CognitiveGap, GapKind, InformationNeed
from .ports import (
    EpisodicMemoryPort,
    MemoryStorePort,
    ProceduralMemoryPort,
    SemanticMemoryPort,
)
from .records import (
    EpisodicMemoryRecord,
    LongTermMemoryRecord,
    ProceduralMemoryRecord,
    SemanticMemoryRecord,
    episodic_memory_record,
    procedural_memory_record,
    semantic_memory_record,
)
from .requests import RetrievalCandidate, RetrievalRequest, RetrievalResult
from .scoring import RetrievalRankingPolicy, score_memory_record
from .signals import RetrievalScoreComponent, RetrievalSignal
from .stores import InMemoryMemoryStore, InMemoryMemoryStoreSet

__all__ = [
    "CognitiveGap",
    "EpisodicMemoryPort",
    "EpisodicMemoryRecord",
    "GapKind",
    "InformationNeed",
    "InMemoryMemoryStore",
    "InMemoryMemoryStoreSet",
    "InMemoryRetrievalController",
    "LongTermMemoryRecord",
    "MemoryStorePort",
    "ProceduralMemoryPort",
    "ProceduralMemoryRecord",
    "RetrievalCandidate",
    "RetrievalRankingPolicy",
    "RetrievalRequest",
    "RetrievalResult",
    "RetrievalScoreComponent",
    "RetrievalSessionResult",
    "RetrievalSignal",
    "SemanticMemoryPort",
    "SemanticMemoryRecord",
    "episodic_memory_record",
    "procedural_memory_record",
    "semantic_memory_record",
    "detect_cognitive_gaps",
    "score_memory_record",
]
