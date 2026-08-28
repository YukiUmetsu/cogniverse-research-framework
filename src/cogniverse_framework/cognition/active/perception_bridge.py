"""Bridge PublicPercept records into the active cognition runtime."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from ..perception import PublicPercept
from ..state import CognitiveState
from .activation import ActivationPolicy
from .graph import ActiveCognitiveEdge, ActiveCognitiveNode, EdgeRelation, NodeCategory
from .runtime import InMemoryActiveCognitionRuntime
from .snapshot import ActiveCognitionSnapshot


def default_percept_node_id(percept: PublicPercept) -> str:
    """Derive a stable active-graph node id from a public percept identity."""

    return f"percept.{percept.percept_id}"


@dataclass(frozen=True, slots=True)
class ActivePerceptionStepResult:
    """Outcome of admitting one percept into the active cognition runtime."""

    percept: PublicPercept
    node: ActiveCognitiveNode
    snapshot: ActiveCognitionSnapshot
    cognitive_state: CognitiveState

    def to_dict(self) -> dict[str, Any]:
        return {
            "percept_digest": self.percept.digest(),
            "node_id": self.node.node_id,
            "snapshot_digest": self.snapshot.digest(),
            "cognitive_state_digest": self.cognitive_state.digest(),
        }


@dataclass(frozen=True, slots=True)
class ActivePerceptionPipelineResult:
    """Deterministic end state after processing an ordered percept sequence."""

    percepts: tuple[PublicPercept, ...]
    snapshot: ActiveCognitionSnapshot
    cognitive_state: CognitiveState

    def to_dict(self) -> dict[str, Any]:
        return {
            "percept_digests": [percept.digest() for percept in self.percepts],
            "snapshot_digest": self.snapshot.digest(),
            "cognitive_state_digest": self.cognitive_state.digest(),
        }


class ActivePerceptionConsumer:
    """Thin framework consumer: PublicPercept -> active runtime -> CognitiveState.

    Environment decoding stays outside this class. Callers pass already-built
  ``PublicPercept`` envelopes from lab or fixture adapters.
    """

    def __init__(
        self,
        policy: ActivationPolicy,
        *,
        working_capacity: int,
        node_category: NodeCategory = NodeCategory.ENTITY,
        node_id_from_percept: Callable[[PublicPercept], str] | None = None,
        source_system: str = "active-perception-consumer",
    ) -> None:
        self._policy = policy
        self._node_category = node_category
        self._node_id_from_percept = node_id_from_percept or default_percept_node_id
        self._source_system = source_system
        self._runtime = InMemoryActiveCognitionRuntime(
            policy,
            working_capacity=working_capacity,
        )

    @property
    def runtime(self) -> InMemoryActiveCognitionRuntime:
        return self._runtime

    @property
    def policy(self) -> ActivationPolicy:
        return self._policy

    def percept_to_node(self, percept: PublicPercept) -> ActiveCognitiveNode:
        """Map one percept envelope to an active graph node without mutating runtime."""

        return ActiveCognitiveNode(
            node_id=self._node_id_from_percept(percept),
            category=self._node_category,
            source_system=percept.source_system,
            logical_step=percept.logical_step,
            confidence_ppm=percept.confidence_ppm,
            evidence_ids=_percept_evidence_ids(percept),
            external_ref_id=percept.percept_id,
        )

    def receive(self, percept: PublicPercept) -> ActivePerceptionStepResult:
        """Admit one percept, update activation, and project a CognitiveState snapshot."""

        node = self.percept_to_node(percept)
        activated = self._runtime.add_perceived_node(node)
        snapshot = self._runtime.snapshot()
        state = snapshot.to_cognitive_state(
            state_id=_state_id_for_step(percept.logical_step),
            source_system=self._source_system,
        )
        return ActivePerceptionStepResult(
            percept=percept,
            node=activated,
            snapshot=snapshot,
            cognitive_state=state,
        )

    def link_percepts(
        self,
        source: PublicPercept,
        target: PublicPercept,
        *,
        relation: EdgeRelation = EdgeRelation.ASSOCIATED_WITH,
        edge_id: str | None = None,
    ) -> ActiveCognitiveEdge:
        """Add a typed association between two previously admissible percepts."""

        source_id = self._node_id_from_percept(source)
        target_id = self._node_id_from_percept(target)
        if self._runtime.graph.get_node(source_id) is None:
            raise ValueError("source percept must be received before linking")
        if self._runtime.graph.get_node(target_id) is None:
            raise ValueError("target percept must be received before linking")

        logical_step = max(source.logical_step, target.logical_step)
        edge = ActiveCognitiveEdge(
            edge_id=edge_id or _default_edge_id(source_id, target_id, relation),
            source_id=source_id,
            target_id=target_id,
            relation=relation,
            source_system=self._source_system,
            logical_step=logical_step,
            evidence_ids=_paired_percept_evidence(source, target),
        )
        self._runtime.add_edge(edge)
        return edge

    def advance(self, logical_step: int) -> ActiveCognitionSnapshot:
        """Apply logical-time decay and refresh working/primed membership."""

        self._runtime.advance(logical_step)
        return self._runtime.snapshot()

    def snapshot(self) -> ActiveCognitionSnapshot:
        return self._runtime.snapshot()

    def to_cognitive_state(self, *, state_id: str | None = None) -> CognitiveState:
        return self.snapshot().to_cognitive_state(
            state_id=state_id or _state_id_for_step(self._runtime.graph.logical_step),
            source_system=self._source_system,
        )

    @classmethod
    def process_percepts(
        cls,
        percepts: tuple[PublicPercept, ...],
        policy: ActivationPolicy,
        *,
        working_capacity: int,
        node_category: NodeCategory = NodeCategory.ENTITY,
        node_id_from_percept: Callable[[PublicPercept], str] | None = None,
        source_system: str = "active-perception-consumer",
        state_id: str | None = None,
    ) -> ActivePerceptionPipelineResult:
        """Process an ordered percept sequence deterministically."""

        consumer = cls(
            policy,
            working_capacity=working_capacity,
            node_category=node_category,
            node_id_from_percept=node_id_from_percept,
            source_system=source_system,
        )
        for percept in percepts:
            consumer.receive(percept)
        snapshot = consumer.snapshot()
        final_step = snapshot.logical_step
        return ActivePerceptionPipelineResult(
            percepts=percepts,
            snapshot=snapshot,
            cognitive_state=snapshot.to_cognitive_state(
                state_id=state_id or _state_id_for_step(final_step),
                source_system=source_system,
            ),
        )


def _percept_evidence_ids(percept: PublicPercept) -> tuple[str, ...]:
    digest_ref = f"percept-digest:{percept.digest()[:16]}"
    return tuple(sorted({*percept.evidence_ids, digest_ref}))


def _paired_percept_evidence(
    source: PublicPercept,
    target: PublicPercept,
) -> tuple[str, ...]:
    return tuple(
        sorted(
            {
                *_percept_evidence_ids(source),
                *_percept_evidence_ids(target),
            }
        )
    )


def _default_edge_id(
    source_id: str,
    target_id: str,
    relation: EdgeRelation,
) -> str:
    return f"edge.{source_id}.{relation.value}.{target_id}"[:128]


def _state_id_for_step(logical_step: int) -> str:
    return f"state-{logical_step:06d}"
