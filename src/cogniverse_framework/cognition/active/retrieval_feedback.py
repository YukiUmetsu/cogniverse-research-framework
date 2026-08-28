"""Apply retrieval results back into the active cognition runtime."""

from __future__ import annotations

from ..state import MemoryKind
from ..retrieval.records import LongTermMemoryRecord
from ..retrieval.requests import RetrievalCandidate, RetrievalResult
from .graph import ActiveCognitiveNode, NodeCategory
from .runtime import InMemoryActiveCognitionRuntime


_MEMORY_NODE_CATEGORY: dict[MemoryKind, NodeCategory] = {
    MemoryKind.EPISODIC: NodeCategory.EVENT,
    MemoryKind.SEMANTIC: NodeCategory.CONCEPT,
    MemoryKind.PROCEDURAL: NodeCategory.PLAN,
}


def memory_node_id(memory_id: str) -> str:
    return f"memory.{memory_id}"


def apply_retrieval_candidate(
    runtime: InMemoryActiveCognitionRuntime,
    candidate: RetrievalCandidate,
    record: LongTermMemoryRecord,
    *,
    logical_step: int,
    source_system: str = "retrieval-feedback",
) -> ActiveCognitiveNode:
    """Boost a retrieved memory into the active graph."""

    node = ActiveCognitiveNode(
        node_id=memory_node_id(candidate.memory_id),
        category=_MEMORY_NODE_CATEGORY.get(candidate.memory_kind, NodeCategory.CONCEPT),
        source_system=source_system,
        logical_step=logical_step,
        confidence_ppm=candidate.score_ppm,
        evidence_ids=candidate.evidence_ids,
        external_ref_id=record.memory_id,
    )
    boost = runtime.policy.retrieval_boost_ppm
    if boost <= 0:
        boost = max(candidate.score_ppm // 2, 0)
    return runtime.admit_retrieved_node(node, retrieval_boost_ppm=boost)


def apply_retrieval_result(
    runtime: InMemoryActiveCognitionRuntime,
    result: RetrievalResult,
    records_by_id: dict[str, LongTermMemoryRecord],
    *,
    source_system: str = "retrieval-feedback",
) -> tuple[ActiveCognitiveNode, ...]:
    """Materialize all candidates from one retrieval result into the active graph."""

    nodes: list[ActiveCognitiveNode] = []
    for candidate in result.candidates:
        record = records_by_id.get(candidate.memory_id)
        if record is None:
            continue
        nodes.append(
            apply_retrieval_candidate(
                runtime,
                candidate,
                record,
                logical_step=result.logical_step,
                source_system=source_system,
            )
        )
    return tuple(nodes)
