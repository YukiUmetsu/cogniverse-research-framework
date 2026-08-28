"""Coordinator wiring runtime, backends, retrieval, and event publication."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ..backends.events import CognitiveEvent, CognitiveEventKind
from ..backends.factory import BackendKind, create_activation_store, create_event_bus, create_memory_store_set
from ..backends.ports import ActivationStorePort, CognitiveEventBusPort, MemoryStoreSetPort
from ..retrieval.controller import RetrievalController, RetrievalSessionResult
from ..retrieval.records import LongTermMemoryRecord
from ..retrieval.scoring import RetrievalRankingPolicy
from ..state import CognitiveState
from .activation import ActivationPolicy
from .graph import NodeCategory
from ..perception import PublicPercept
from .perception_bridge import ActivePerceptionConsumer, ActivePerceptionStepResult
from .retrieval_feedback import apply_retrieval_result
from .runtime import InMemoryActiveCognitionRuntime
from .snapshot import ActiveCognitionSnapshot


@dataclass(frozen=True, slots=True)
class ActiveCognitionCycleResult:
    """Outcome of one perceive → retrieve → feedback cycle."""

    perception: ActivePerceptionStepResult | None = None
    retrieval: RetrievalSessionResult | None = None
    snapshot: ActiveCognitionSnapshot | None = None
    cognitive_state: CognitiveState | None = None
    events_published: tuple[CognitiveEvent, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, Any]:
        return {
            "perception_digest": (
                self.perception.percept.digest() if self.perception is not None else None
            ),
            "retrieval_gap_count": (
                len(self.retrieval.gaps) if self.retrieval is not None else 0
            ),
            "snapshot_digest": self.snapshot.digest() if self.snapshot is not None else None,
            "cognitive_state_digest": (
                self.cognitive_state.digest() if self.cognitive_state is not None else None
            ),
            "events_published": [event.event_id for event in self.events_published],
        }


class ActiveCognitionCoordinator:
    """Plug-and-play coordinator for active cognition with swappable backends."""

    def __init__(
        self,
        activation_policy: ActivationPolicy,
        retrieval_policy: RetrievalRankingPolicy,
        *,
        working_capacity: int,
        memory_stores: MemoryStoreSetPort | None = None,
        event_bus: CognitiveEventBusPort | None = None,
        activation_store: ActivationStorePort | None = None,
        memory_backend: BackendKind = "inmemory",
        event_backend: BackendKind = "inmemory",
        activation_backend: BackendKind = "inmemory",
        redis_client: Any | None = None,
        node_category: NodeCategory = NodeCategory.ENTITY,
        source_system: str = "active-cognition-coordinator",
    ) -> None:
        self._activation_policy = activation_policy
        self._retrieval_policy = retrieval_policy
        self._source_system = source_system
        self._memory_stores = memory_stores or create_memory_store_set(
            memory_backend, redis_client=redis_client
        )
        self._event_bus = event_bus or create_event_bus(
            event_backend, redis_client=redis_client
        )
        self._activation_store = activation_store or create_activation_store(
            activation_backend, redis_client=redis_client
        )
        self._perception = ActivePerceptionConsumer(
            activation_policy,
            working_capacity=working_capacity,
            node_category=node_category,
            source_system=source_system,
        )
        self._retrieval = RetrievalController(
            retrieval_policy,
            stores=self._memory_stores,
            source_system=source_system,
        )
        self._event_counter = 0

    @property
    def runtime(self) -> InMemoryActiveCognitionRuntime:
        return self._perception.runtime

    @property
    def memory_stores(self) -> MemoryStoreSetPort:
        return self._memory_stores

    @property
    def event_bus(self) -> CognitiveEventBusPort:
        return self._event_bus

    @property
    def activation_store(self) -> ActivationStorePort:
        return self._activation_store

    @property
    def retrieval(self) -> RetrievalController:
        return self._retrieval

    def store_memory(self, record: LongTermMemoryRecord) -> LongTermMemoryRecord:
        return self._memory_stores.store(record)

    def receive_percept(self, percept: PublicPercept) -> ActiveCognitionCycleResult:
        step = self._perception.receive(percept)
        self._persist_activation(step.node.node_id, step.node.logical_step, step.node.activation_ppm)
        events = (
            self._publish(
                CognitiveEventKind.PERCEPT_RECEIVED,
                subject_id=step.node.node_id,
                logical_step=step.node.logical_step,
                evidence_ids=step.node.evidence_ids,
                payload_sha256=percept.digest(),
            ),
            self._publish(
                CognitiveEventKind.NODE_ACTIVATED,
                subject_id=step.node.node_id,
                logical_step=step.node.logical_step,
                evidence_ids=step.node.evidence_ids,
            ),
        )
        return ActiveCognitionCycleResult(
            perception=step,
            snapshot=step.snapshot,
            cognitive_state=step.cognitive_state,
            events_published=events,
        )

    def run_retrieval_cycle(
        self,
        *,
        goal_node_ids: tuple[str, ...] = (),
    ) -> ActiveCognitionCycleResult:
        snapshot = self.runtime.snapshot()
        session = self._retrieval.run_for_snapshot(snapshot, goal_node_ids=goal_node_ids)
        events: list[CognitiveEvent] = []
        for gap in session.gaps:
            events.append(
                self._publish(
                    CognitiveEventKind.COGNITIVE_GAP_CREATED,
                    subject_id=gap.subject_node_id,
                    logical_step=gap.logical_step,
                    evidence_ids=gap.evidence_ids,
                )
            )
        records_by_id = {
            record.memory_id: record
            for result in session.results
            for candidate in result.candidates
            for record in [
                self._memory_stores.get(
                    candidate.memory_id, memory_kind=candidate.memory_kind
                )
            ]
            if record is not None
        }
        for result in session.results:
            nodes = apply_retrieval_result(
                self.runtime,
                result,
                records_by_id,
                source_system=self._source_system,
            )
            for node in nodes:
                self._persist_activation(node.node_id, node.logical_step, node.activation_ppm)
                events.append(
                    self._publish(
                        CognitiveEventKind.MEMORY_RETRIEVED,
                        subject_id=node.node_id,
                        logical_step=node.logical_step,
                        evidence_ids=node.evidence_ids,
                    )
                )
        final_snapshot = self.runtime.snapshot()
        state = final_snapshot.to_cognitive_state(source_system=self._source_system)
        return ActiveCognitionCycleResult(
            retrieval=session,
            snapshot=final_snapshot,
            cognitive_state=state,
            events_published=tuple(events),
        )

    def receive_and_retrieve(
        self,
        percept: PublicPercept,
        *,
        goal_node_ids: tuple[str, ...] = (),
    ) -> ActiveCognitionCycleResult:
        perception_result = self.receive_percept(percept)
        retrieval_result = self.run_retrieval_cycle(goal_node_ids=goal_node_ids)
        return ActiveCognitionCycleResult(
            perception=perception_result.perception,
            retrieval=retrieval_result.retrieval,
            snapshot=retrieval_result.snapshot,
            cognitive_state=retrieval_result.cognitive_state,
            events_published=perception_result.events_published + retrieval_result.events_published,
        )

    def replay_events(self) -> tuple[CognitiveEvent, ...]:
        return self._event_bus.replay()

    def _persist_activation(
        self,
        node_id: str,
        logical_step: int,
        activation_ppm: int,
    ) -> None:
        self._activation_store.write_activation(
            node_id=node_id,
            logical_step=logical_step,
            activation_ppm=activation_ppm,
        )

    def _publish(
        self,
        kind: CognitiveEventKind,
        *,
        subject_id: str,
        logical_step: int,
        evidence_ids: tuple[str, ...] = (),
        payload_sha256: str | None = None,
    ) -> CognitiveEvent:
        self._event_counter += 1
        event = CognitiveEvent(
            event_id=f"event-{self._event_counter:06d}",
            kind=kind,
            logical_step=logical_step,
            source_system=self._source_system,
            subject_id=subject_id,
            evidence_ids=evidence_ids,
            payload_sha256=payload_sha256,
        )
        return self._event_bus.publish(event)
