"""Immutable snapshots projecting active cognition into CognitiveState."""

from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import json
from typing import Any, ClassVar

from ..state import CognitiveReference, CognitiveState, MemoryKind, ReferenceKind
from .activation import ActivationPolicy, ActivationRecord
from .graph import ActiveCognitiveGraph
from .memory import MemoryEvictionRecord, PrimedMemory, WorkingMemory


@dataclass(frozen=True, slots=True)
class ActiveCognitionSnapshot:
    """Immutable bundle of live active cognition at one logical time."""

    SCHEMA_VERSION: ClassVar[str] = "active_cognition_snapshot.v1"

    logical_step: int
    policy: ActivationPolicy
    graph: ActiveCognitiveGraph
    working_memory: WorkingMemory
    primed_memory: PrimedMemory
    activation_records: tuple[ActivationRecord, ...] = field(default_factory=tuple)
    eviction_records: tuple[MemoryEvictionRecord, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if (
            isinstance(self.logical_step, bool)
            or not isinstance(self.logical_step, int)
            or self.logical_step < 0
        ):
            raise ValueError("logical_step must be a non-negative integer")
        if self.graph.logical_step != self.logical_step:
            raise ValueError("graph.logical_step must match snapshot logical_step")

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.SCHEMA_VERSION,
            "logical_step": self.logical_step,
            "policy": self.policy.to_dict(),
            "graph": self.graph.to_dict(),
            "working_memory": self.working_memory.to_dict(),
            "primed_memory": self.primed_memory.to_dict(),
            "activation_records": [record.to_dict() for record in self.activation_records],
            "eviction_records": [record.to_dict() for record in self.eviction_records],
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

    def to_cognitive_state(
        self,
        *,
        state_id: str | None = None,
        source_system: str = "active_cognition",
    ) -> CognitiveState:
        """Project working-memory items into a v1 CognitiveState without mutating schemas."""

        memory_refs = tuple(
            CognitiveReference(
                ref_id=f"wm:{item.node_id}",
                kind=ReferenceKind.MEMORY,
                source_system=source_system,
                logical_step=self.logical_step,
                confidence_ppm=item.activation_ppm_at_admission,
                evidence_ids=(f"active-graph:{self.graph.digest()[:16]}",),
                memory_kind=MemoryKind.EPISODIC,
            )
            for item in self.working_memory.items
        )
        return CognitiveState(
            state_id=state_id or f"active-{self.digest()[:16]}",
            logical_step=self.logical_step,
            memories=memory_refs,
        )
