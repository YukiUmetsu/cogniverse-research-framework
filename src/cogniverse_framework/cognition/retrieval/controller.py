"""Reference retrieval controller with transparent ranking."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ..active.snapshot import ActiveCognitionSnapshot
from ..state import MemoryKind
from .gap_detection import detect_cognitive_gaps
from .gaps import CognitiveGap, GapKind, InformationNeed
from .records import LongTermMemoryRecord
from .requests import RetrievalRequest, RetrievalResult
from .scoring import RetrievalRankingPolicy, score_memory_record
from ..backends.inmemory import InMemoryMemoryStoreSet


_DEFAULT_ROLES_BY_GAP: dict[GapKind, tuple[MemoryKind, ...]] = {
    GapKind.UNKNOWN_CAUSE: (MemoryKind.EPISODIC, MemoryKind.SEMANTIC),
    GapKind.UNKNOWN_DESTINATION: (MemoryKind.SEMANTIC, MemoryKind.EPISODIC),
    GapKind.UNKNOWN_GOAL_PRECONDITION: (MemoryKind.PROCEDURAL, MemoryKind.SEMANTIC),
    GapKind.LOW_PREDICTION_CONFIDENCE: (MemoryKind.SEMANTIC, MemoryKind.EPISODIC),
    GapKind.UNRESOLVED_BELIEF_CONFLICT: (MemoryKind.SEMANTIC, MemoryKind.EPISODIC),
    GapKind.MISSING_ASSOCIATION: (MemoryKind.SEMANTIC, MemoryKind.EPISODIC),
}


@dataclass(frozen=True, slots=True)
class RetrievalSessionResult:
    """Gaps, needs, requests, and ranked results for one snapshot."""

    snapshot_digest: str
    gaps: tuple[CognitiveGap, ...] = field(default_factory=tuple)
    needs: tuple[InformationNeed, ...] = field(default_factory=tuple)
    requests: tuple[RetrievalRequest, ...] = field(default_factory=tuple)
    results: tuple[RetrievalResult, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, Any]:
        return {
            "snapshot_digest": self.snapshot_digest,
            "gaps": [gap.to_dict() for gap in self.gaps],
            "needs": [need.to_dict() for need in self.needs],
            "requests": [request.to_dict() for request in self.requests],
            "results": [result.to_dict() for result in self.results],
        }


class RetrievalController:
    """Goal/gap-driven retrieval over pluggable memory store backends."""

    def __init__(
        self,
        policy: RetrievalRankingPolicy,
        stores: MemoryStoreSetPort | None = None,
        *,
        source_system: str = "retrieval-controller",
        low_confidence_threshold_ppm: int = 400_000,
    ) -> None:
        self._policy = policy
        self._stores = stores or InMemoryMemoryStoreSet()
        self._source_system = source_system
        self._low_confidence_threshold_ppm = low_confidence_threshold_ppm
        self._request_counter = 0

    @property
    def policy(self) -> RetrievalRankingPolicy:
        return self._policy

    @property
    def stores(self) -> MemoryStoreSetPort:
        return self._stores

    def store(self, record: LongTermMemoryRecord) -> LongTermMemoryRecord:
        return self._stores.store(record)

    def build_request(
        self,
        gap: CognitiveGap,
        snapshot: ActiveCognitionSnapshot,
        *,
        budget: int | None = None,
        memory_roles: tuple[MemoryKind, ...] | None = None,
        goal_node_ids: tuple[str, ...] = (),
    ) -> RetrievalRequest:
        self._request_counter += 1
        roles = memory_roles or _DEFAULT_ROLES_BY_GAP.get(
            gap.kind, (MemoryKind.EPISODIC, MemoryKind.SEMANTIC)
        )
        return RetrievalRequest(
            request_id=f"retrieval-{self._request_counter:04d}",
            logical_step=snapshot.logical_step,
            source_system=self._source_system,
            gap=gap,
            memory_roles=roles,
            budget=budget or self._policy.default_budget,
            active_graph_digest=snapshot.graph.digest(),
            goal_node_ids=goal_node_ids,
            primed_node_ids=snapshot.primed_memory.node_ids(),
            working_node_ids=snapshot.working_memory.node_ids(),
        )

    def retrieve(self, request: RetrievalRequest) -> RetrievalResult:
        candidates = []
        for record in self._stores.query_all(request):
            candidate = score_memory_record(request, record, self._policy)
            if candidate is not None:
                candidates.append(candidate)

        ranked = tuple(
            sorted(
                candidates,
                key=lambda item: (-item.score_ppm, item.memory_id, item.memory_kind.value),
            )[: request.budget]
        )
        return RetrievalResult(
            request_id=request.request_id,
            logical_step=request.logical_step,
            source_system=self._source_system,
            gap_id=request.gap.gap_id,
            candidates=ranked,
        )

    def run_for_snapshot(
        self,
        snapshot: ActiveCognitionSnapshot,
        *,
        gaps: tuple[CognitiveGap, ...] | None = None,
        goal_node_ids: tuple[str, ...] = (),
    ) -> RetrievalSessionResult:
        """Detect gaps (unless supplied), build needs/requests, and retrieve."""

        detected = gaps or detect_cognitive_gaps(
            snapshot,
            source_system=self._source_system,
            low_confidence_threshold_ppm=self._low_confidence_threshold_ppm,
        )
        needs = tuple(InformationNeed.from_gap(gap) for gap in detected)
        requests = tuple(
            self.build_request(gap, snapshot, goal_node_ids=goal_node_ids)
            for gap in detected
        )
        results = tuple(self.retrieve(request) for request in requests)
        return RetrievalSessionResult(
            snapshot_digest=snapshot.digest(),
            gaps=detected,
            needs=needs,
            requests=requests,
            results=results,
        )


InMemoryRetrievalController = RetrievalController
