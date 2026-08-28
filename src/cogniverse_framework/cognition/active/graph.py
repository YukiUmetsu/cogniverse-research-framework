"""Active cognitive graph contracts for the live runtime workspace."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
import hashlib
import json
from typing import Any, ClassVar

from .._validation import normalize_identifiers, validate_identifier, validate_ppm


class NodeCategory(str, Enum):
    """Runtime node roles in the active relational workspace."""

    ENTITY = "entity"
    CONCEPT = "concept"
    EVENT = "event"
    BELIEF = "belief"
    GOAL = "goal"
    PREDICTION = "prediction"
    HYPOTHESIS = "hypothesis"
    NEED = "need"
    ACTION = "action"
    PLAN = "plan"
    CONSTRAINT = "constraint"


class EdgeRelation(str, Enum):
    """Typed relations between active graph nodes."""

    AGENT_OF = "agent_of"
    TARGET_OF = "target_of"
    IS_A = "is_a"
    PART_OF = "part_of"
    BEFORE = "before"
    AFTER = "after"
    POSSIBLE_CAUSE = "possible_cause"
    SUPPORTS = "supports"
    CONTRADICTS = "contradicts"
    PREDICTS = "predicts"
    REQUIRES = "requires"
    ASSOCIATED_WITH = "associated_with"


def clamp_activation_ppm(value: int) -> int:
    """Keep activation in the shared ppm range."""

    return max(0, min(1_000_000, value))


@dataclass(frozen=True, slots=True)
class ActiveCognitiveNode:
    """One actively represented cognitive element with activation state."""

    SCHEMA_VERSION: ClassVar[str] = "active_cognitive_node.v1"

    node_id: str
    category: NodeCategory
    source_system: str
    logical_step: int
    activation_ppm: int = 0
    confidence_ppm: int | None = None
    evidence_ids: tuple[str, ...] = field(default_factory=tuple)
    external_ref_id: str | None = None

    def __post_init__(self) -> None:
        validate_identifier("node_id", self.node_id)
        validate_identifier("source_system", self.source_system)
        if (
            isinstance(self.logical_step, bool)
            or not isinstance(self.logical_step, int)
            or self.logical_step < 0
        ):
            raise ValueError("logical_step must be a non-negative integer")
        validate_ppm("activation_ppm", self.activation_ppm)
        validate_ppm("confidence_ppm", self.confidence_ppm)
        if self.external_ref_id is not None:
            validate_identifier("external_ref_id", self.external_ref_id)
        object.__setattr__(
            self,
            "evidence_ids",
            normalize_identifiers("evidence_ids", tuple(self.evidence_ids)),
        )

    def with_activation(self, activation_ppm: int, *, logical_step: int) -> ActiveCognitiveNode:
        return ActiveCognitiveNode(
            node_id=self.node_id,
            category=self.category,
            source_system=self.source_system,
            logical_step=logical_step,
            activation_ppm=clamp_activation_ppm(activation_ppm),
            confidence_ppm=self.confidence_ppm,
            evidence_ids=self.evidence_ids,
            external_ref_id=self.external_ref_id,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.SCHEMA_VERSION,
            "node_id": self.node_id,
            "category": self.category.value,
            "source_system": self.source_system,
            "logical_step": self.logical_step,
            "activation_ppm": self.activation_ppm,
            "confidence_ppm": self.confidence_ppm,
            "evidence_ids": list(self.evidence_ids),
            "external_ref_id": self.external_ref_id,
        }


@dataclass(frozen=True, slots=True)
class ActiveCognitiveEdge:
    """A typed relation between two active graph nodes."""

    SCHEMA_VERSION: ClassVar[str] = "active_cognitive_edge.v1"

    edge_id: str
    source_id: str
    target_id: str
    relation: EdgeRelation
    source_system: str
    logical_step: int
    confidence_ppm: int | None = None
    evidence_ids: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        validate_identifier("edge_id", self.edge_id)
        validate_identifier("source_id", self.source_id)
        validate_identifier("target_id", self.target_id)
        validate_identifier("source_system", self.source_system)
        if self.source_id == self.target_id:
            raise ValueError("source_id and target_id must differ")
        if (
            isinstance(self.logical_step, bool)
            or not isinstance(self.logical_step, int)
            or self.logical_step < 0
        ):
            raise ValueError("logical_step must be a non-negative integer")
        validate_ppm("confidence_ppm", self.confidence_ppm)
        object.__setattr__(
            self,
            "evidence_ids",
            normalize_identifiers("evidence_ids", tuple(self.evidence_ids)),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.SCHEMA_VERSION,
            "edge_id": self.edge_id,
            "source_id": self.source_id,
            "target_id": self.target_id,
            "relation": self.relation.value,
            "source_system": self.source_system,
            "logical_step": self.logical_step,
            "confidence_ppm": self.confidence_ppm,
            "evidence_ids": list(self.evidence_ids),
        }


@dataclass(frozen=True, slots=True)
class ActiveCognitiveGraph:
    """Small runtime-oriented relational graph with deterministic ordering."""

    SCHEMA_VERSION: ClassVar[str] = "active_cognitive_graph.v1"

    logical_step: int
    nodes: tuple[ActiveCognitiveNode, ...] = field(default_factory=tuple)
    edges: tuple[ActiveCognitiveEdge, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if (
            isinstance(self.logical_step, bool)
            or not isinstance(self.logical_step, int)
            or self.logical_step < 0
        ):
            raise ValueError("logical_step must be a non-negative integer")

        sorted_nodes = tuple(sorted(self.nodes, key=lambda item: item.node_id))
        sorted_edges = tuple(sorted(self.edges, key=lambda item: item.edge_id))
        object.__setattr__(self, "nodes", sorted_nodes)
        object.__setattr__(self, "edges", sorted_edges)

        node_ids = [item.node_id for item in sorted_nodes]
        if len(node_ids) != len(set(node_ids)):
            raise ValueError("node_id values must be unique in ActiveCognitiveGraph")

        edge_ids = [item.edge_id for item in sorted_edges]
        if len(edge_ids) != len(set(edge_ids)):
            raise ValueError("edge_id values must be unique in ActiveCognitiveGraph")

        known_nodes = set(node_ids)
        for edge in sorted_edges:
            if edge.source_id not in known_nodes or edge.target_id not in known_nodes:
                raise ValueError("edges must reference existing node_id values")

    @classmethod
    def empty(cls, *, logical_step: int = 0) -> ActiveCognitiveGraph:
        return cls(logical_step=logical_step)

    def get_node(self, node_id: str) -> ActiveCognitiveNode | None:
        for node in self.nodes:
            if node.node_id == node_id:
                return node
        return None

    def neighbor_ids(self, node_id: str) -> tuple[str, ...]:
        neighbors: set[str] = set()
        for edge in self.edges:
            if edge.source_id == node_id:
                neighbors.add(edge.target_id)
            elif edge.target_id == node_id:
                neighbors.add(edge.source_id)
        return tuple(sorted(neighbors))

    def with_node(self, node: ActiveCognitiveNode) -> ActiveCognitiveGraph:
        remaining = tuple(item for item in self.nodes if item.node_id != node.node_id)
        return ActiveCognitiveGraph(
            logical_step=max(self.logical_step, node.logical_step),
            nodes=remaining + (node,),
            edges=self.edges,
        )

    def with_edge(self, edge: ActiveCognitiveEdge) -> ActiveCognitiveGraph:
        if self.get_node(edge.source_id) is None or self.get_node(edge.target_id) is None:
            raise ValueError("cannot add edge before its endpoint nodes exist")
        remaining = tuple(item for item in self.edges if item.edge_id != edge.edge_id)
        return ActiveCognitiveGraph(
            logical_step=max(self.logical_step, edge.logical_step),
            nodes=self.nodes,
            edges=remaining + (edge,),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.SCHEMA_VERSION,
            "logical_step": self.logical_step,
            "nodes": [item.to_dict() for item in self.nodes],
            "edges": [item.to_dict() for item in self.edges],
        }

    def canonical_json(self) -> str:
        return json.dumps(
            self.to_dict(),
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        )

    def digest(self) -> str:
        return hashlib.sha256(self.canonical_json().encode("utf-8")).hexdigest()
