"""Memory store ports for pluggable long-term memory backends."""

from __future__ import annotations

from typing import Protocol

from ..state import MemoryKind
from .records import LongTermMemoryRecord
from .requests import RetrievalRequest


class MemoryStorePort(Protocol):
    """Generic query surface for one long-term memory role."""

    @property
    def memory_kind(self) -> MemoryKind:
        ...

    def store(self, record: LongTermMemoryRecord) -> LongTermMemoryRecord:
        ...

    def query(self, request: RetrievalRequest) -> tuple[LongTermMemoryRecord, ...]:
        ...


class EpisodicMemoryPort(MemoryStorePort, Protocol):
    """Port for experienced-event memory."""

    memory_kind: MemoryKind


class SemanticMemoryPort(MemoryStorePort, Protocol):
    """Port for generalized knowledge memory."""

    memory_kind: MemoryKind


class ProceduralMemoryPort(MemoryStorePort, Protocol):
    """Port for reusable skill/procedure memory."""

    memory_kind: MemoryKind
