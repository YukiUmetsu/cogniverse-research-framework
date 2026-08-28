"""Pluggable backend ports for memory, activation, and cognitive events."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from ..retrieval.records import LongTermMemoryRecord
from ..retrieval.requests import RetrievalRequest
from ..state import MemoryKind
from .events import CognitiveEvent


@runtime_checkable
class MemoryStorePort(Protocol):
    """One long-term memory role backed by any storage technology."""

    @property
    def memory_kind(self) -> MemoryKind:
        ...

    def store(self, record: LongTermMemoryRecord) -> LongTermMemoryRecord:
        ...

    def get(self, memory_id: str) -> LongTermMemoryRecord | None:
        ...

    def query(self, request: RetrievalRequest) -> tuple[LongTermMemoryRecord, ...]:
        ...


@runtime_checkable
class MemoryStoreSetPort(Protocol):
    """Bundle of episodic, semantic, and procedural stores."""

    def store(self, record: LongTermMemoryRecord) -> LongTermMemoryRecord:
        ...

    def get(self, memory_id: str, *, memory_kind: MemoryKind) -> LongTermMemoryRecord | None:
        ...

    def query_all(self, request: RetrievalRequest) -> tuple[LongTermMemoryRecord, ...]:
        ...

    def for_kind(self, memory_kind: MemoryKind) -> MemoryStorePort:
        ...


@runtime_checkable
class ActivationStorePort(Protocol):
    """Optional persistence for node activation levels by logical step."""

    def write_activation(
        self,
        *,
        node_id: str,
        logical_step: int,
        activation_ppm: int,
    ) -> None:
        ...

    def read_activation(self, *, node_id: str, logical_step: int) -> int | None:
        ...

    def latest_activation(self, *, node_id: str) -> tuple[int, int] | None:
        """Return (logical_step, activation_ppm) or None."""


@runtime_checkable
class CognitiveEventBusPort(Protocol):
    """Transport for typed cognitive runtime events."""

    def publish(self, event: CognitiveEvent) -> CognitiveEvent:
        ...

    def read(
        self,
        *,
        after_event_id: str | None = None,
        limit: int = 1000,
    ) -> tuple[CognitiveEvent, ...]:
        ...

    def replay(self) -> tuple[CognitiveEvent, ...]:
        ...
