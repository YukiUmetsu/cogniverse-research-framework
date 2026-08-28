"""In-memory active cognition runtime with deterministic stepping."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .activation import (
    ActivationPolicy,
    ActivationReason,
    ActivationRecord,
    ActivationSource,
    apply_boost,
    apply_decay,
)
from .graph import ActiveCognitiveEdge, ActiveCognitiveGraph, ActiveCognitiveNode, EdgeRelation, NodeCategory
from .memory import (
    MemoryEvictionRecord,
    PrimedMemory,
    PrimedMemoryItem,
    WorkingMemory,
    WorkingMemoryItem,
)
from .snapshot import ActiveCognitionSnapshot


@dataclass
class _RuntimeState:
    graph: ActiveCognitiveGraph
    working_memory: WorkingMemory
    primed_memory: PrimedMemory
    activation_records: tuple[ActivationRecord, ...]
    eviction_records: tuple[MemoryEvictionRecord, ...]
    record_counter: int


class InMemoryActiveCognitionRuntime:
    """Reference runtime for active graph, activation, and bounded working memory."""

    def __init__(
        self,
        policy: ActivationPolicy,
        *,
        working_capacity: int,
        logical_step: int = 0,
    ) -> None:
        if (
            isinstance(working_capacity, bool)
            or not isinstance(working_capacity, int)
            or working_capacity < 1
        ):
            raise ValueError("working_capacity must be a positive integer")
        self._policy = policy
        self._working_capacity = working_capacity
        self._state = _RuntimeState(
            graph=ActiveCognitiveGraph.empty(logical_step=logical_step),
            working_memory=WorkingMemory(capacity=working_capacity),
            primed_memory=PrimedMemory(),
            activation_records=(),
            eviction_records=(),
            record_counter=0,
        )

    @property
    def policy(self) -> ActivationPolicy:
        return self._policy

    @property
    def graph(self) -> ActiveCognitiveGraph:
        return self._state.graph

    @property
    def working_memory(self) -> WorkingMemory:
        return self._state.working_memory

    @property
    def primed_memory(self) -> PrimedMemory:
        return self._state.primed_memory

    @property
    def activation_records(self) -> tuple[ActivationRecord, ...]:
        return self._state.activation_records

    @property
    def eviction_records(self) -> tuple[MemoryEvictionRecord, ...]:
        return self._state.eviction_records

    def add_perceived_node(self, node: ActiveCognitiveNode) -> ActiveCognitiveNode:
        """Admit a perceived node and apply perception plus associative boosts."""

        existing = self._state.graph.get_node(node.node_id)
        previous_activation = existing.activation_ppm if existing is not None else 0
        activated = node.with_activation(
            apply_boost(previous_activation, boost_ppm=self._policy.perception_boost_ppm),
            logical_step=node.logical_step,
        )
        self._state.graph = self._state.graph.with_node(activated)
        self._append_activation_record(
            node_id=activated.node_id,
            logical_step=activated.logical_step,
            previous_activation_ppm=previous_activation,
            new_activation_ppm=activated.activation_ppm,
            source=ActivationSource.PERCEPTION,
            reason=ActivationReason.PERCEPT_RECEIVED,
        )
        self._spread_activation(
            from_node_id=activated.node_id,
            logical_step=activated.logical_step,
        )
        self._refresh_memory_layers(logical_step=activated.logical_step)
        return activated

    def add_edge(self, edge: ActiveCognitiveEdge) -> ActiveCognitiveEdge:
        """Add a typed relation between existing graph nodes."""

        self._state.graph = self._state.graph.with_edge(edge)
        return edge

    def advance(self, logical_step: int) -> None:
        """Apply decay and refresh working/primed membership at a new logical time."""

        if (
            isinstance(logical_step, bool)
            or not isinstance(logical_step, int)
            or logical_step < 0
        ):
            raise ValueError("logical_step must be a non-negative integer")
        if logical_step < self._state.graph.logical_step:
            raise ValueError("logical_step cannot move backward")

        updated_nodes: list[ActiveCognitiveNode] = []
        for node in self._state.graph.nodes:
            decayed = apply_decay(node.activation_ppm, decay_ppm=self._policy.decay_ppm)
            updated = node.with_activation(decayed, logical_step=logical_step)
            updated_nodes.append(updated)
            if decayed != node.activation_ppm:
                self._append_activation_record(
                    node_id=node.node_id,
                    logical_step=logical_step,
                    previous_activation_ppm=node.activation_ppm,
                    new_activation_ppm=decayed,
                    source=ActivationSource.DECAY,
                    reason=ActivationReason.LOGICAL_TICK_DECAY,
                )

        self._state.graph = ActiveCognitiveGraph(
            logical_step=logical_step,
            nodes=tuple(updated_nodes),
            edges=self._state.graph.edges,
        )
        self._refresh_memory_layers(logical_step=logical_step)

    def snapshot(self) -> ActiveCognitionSnapshot:
        """Capture the current runtime as an immutable auditable snapshot."""

        return ActiveCognitionSnapshot(
            logical_step=self._state.graph.logical_step,
            policy=self._policy,
            graph=self._state.graph,
            working_memory=self._state.working_memory,
            primed_memory=self._state.primed_memory,
            activation_records=self._state.activation_records,
            eviction_records=self._state.eviction_records,
        )

    @classmethod
    def replay(
        cls,
        policy: ActivationPolicy,
        *,
        working_capacity: int,
        operations: tuple[dict[str, Any], ...],
    ) -> ActiveCognitionSnapshot:
        """Reconstruct a snapshot from an ordered operation log."""

        runtime = cls(policy, working_capacity=working_capacity)
        for operation in operations:
            op_type = operation["op"]
            if op_type == "add_perceived_node":
                runtime.add_perceived_node(_node_from_dict(operation["node"]))
            elif op_type == "add_edge":
                runtime.add_edge(_edge_from_dict(operation["edge"]))
            elif op_type == "advance":
                runtime.advance(operation["logical_step"])
            else:
                raise ValueError(f"unsupported replay operation: {op_type}")
        return runtime.snapshot()

    def spread_from_node(self, node_id: str, *, logical_step: int) -> None:
        """Spread activation from an existing node to its graph neighbors."""

        if self._state.graph.get_node(node_id) is None:
            raise ValueError("cannot spread activation from unknown node_id")
        self._spread_activation(from_node_id=node_id, logical_step=logical_step)
        self._refresh_memory_layers(logical_step=logical_step)

    def _spread_activation(self, *, from_node_id: str, logical_step: int) -> None:
        for neighbor_id in self._state.graph.neighbor_ids(from_node_id):
            neighbor = self._state.graph.get_node(neighbor_id)
            if neighbor is None:
                continue
            previous_activation = neighbor.activation_ppm
            boosted = neighbor.with_activation(
                apply_boost(previous_activation, boost_ppm=self._policy.spreading_boost_ppm),
                logical_step=logical_step,
            )
            self._state.graph = self._state.graph.with_node(boosted)
            self._append_activation_record(
                node_id=neighbor_id,
                logical_step=logical_step,
                previous_activation_ppm=previous_activation,
                new_activation_ppm=boosted.activation_ppm,
                source=ActivationSource.SPREADING,
                reason=ActivationReason.ASSOCIATIVE_SPREAD,
            )

    def _refresh_memory_layers(self, *, logical_step: int) -> None:
        previous_working_ids = set(self._state.working_memory.node_ids())
        candidates = sorted(
            self._state.graph.nodes,
            key=lambda node: (-node.activation_ppm, node.node_id),
        )
        working_items: list[WorkingMemoryItem] = []
        for node in candidates:
            if node.activation_ppm < self._policy.working_threshold_ppm:
                continue
            if len(working_items) >= self._working_capacity:
                break
            working_items.append(
                WorkingMemoryItem(
                    node_id=node.node_id,
                    admitted_at_step=logical_step,
                    admission_reason=ActivationReason.WORKING_THRESHOLD_MET,
                    activation_ppm_at_admission=node.activation_ppm,
                )
            )

        working_ids = {item.node_id for item in working_items}
        evictions = list(self._state.eviction_records)
        for node_id in sorted(previous_working_ids - working_ids):
            node = self._state.graph.get_node(node_id)
            if node is None:
                continue
            if node.activation_ppm < self._policy.working_threshold_ppm:
                reason = ActivationReason.BELOW_WORKING_THRESHOLD
            else:
                reason = ActivationReason.CAPACITY_EVICTION
            evictions.append(
                MemoryEvictionRecord(
                    node_id=node_id,
                    logical_step=logical_step,
                    reason=reason,
                    activation_ppm=node.activation_ppm,
                )
            )

        primed_items: list[PrimedMemoryItem] = []
        for node in self._state.graph.nodes:
            if node.node_id in working_ids:
                continue
            if node.activation_ppm < self._policy.primed_threshold_ppm:
                continue
            primed_items.append(
                PrimedMemoryItem(
                    node_id=node.node_id,
                    primed_at_step=logical_step,
                    activation_ppm=node.activation_ppm,
                    admission_reason=ActivationReason.PRIMED_THRESHOLD_MET,
                )
            )

        self._state.working_memory = WorkingMemory(
            capacity=self._working_capacity,
            items=tuple(working_items),
        )
        self._state.primed_memory = PrimedMemory(items=tuple(primed_items))
        self._state.eviction_records = tuple(evictions)

    def _append_activation_record(
        self,
        *,
        node_id: str,
        logical_step: int,
        previous_activation_ppm: int,
        new_activation_ppm: int,
        source: ActivationSource,
        reason: ActivationReason,
    ) -> None:
        if previous_activation_ppm == new_activation_ppm:
            return
        self._state.record_counter += 1
        record = ActivationRecord(
            record_id=f"activation-{self._state.record_counter:06d}",
            node_id=node_id,
            logical_step=logical_step,
            previous_activation_ppm=previous_activation_ppm,
            new_activation_ppm=new_activation_ppm,
            source=source,
            reason=reason,
        )
        self._state.activation_records = self._state.activation_records + (record,)


def _node_from_dict(payload: dict[str, Any]) -> ActiveCognitiveNode:
    category = payload["category"]
    if not isinstance(category, NodeCategory):
        category = NodeCategory(category)
    return ActiveCognitiveNode(
        node_id=payload["node_id"],
        category=category,
        source_system=payload["source_system"],
        logical_step=payload["logical_step"],
        activation_ppm=payload.get("activation_ppm", 0),
        confidence_ppm=payload.get("confidence_ppm"),
        evidence_ids=tuple(payload.get("evidence_ids", ())),
        external_ref_id=payload.get("external_ref_id"),
    )


def _edge_from_dict(payload: dict[str, Any]) -> ActiveCognitiveEdge:
    relation = payload["relation"]
    if not isinstance(relation, EdgeRelation):
        relation = EdgeRelation(relation)
    return ActiveCognitiveEdge(
        edge_id=payload["edge_id"],
        source_id=payload["source_id"],
        target_id=payload["target_id"],
        relation=relation,
        source_system=payload["source_system"],
        logical_step=payload["logical_step"],
        confidence_ppm=payload.get("confidence_ppm"),
        evidence_ids=tuple(payload.get("evidence_ids", ())),
    )
