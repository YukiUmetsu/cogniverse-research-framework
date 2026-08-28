"""In-memory reference implementations of pluggable cognitive backends."""

from __future__ import annotations

from ..state import MemoryKind
from ..retrieval.records import LongTermMemoryRecord
from ..retrieval.requests import RetrievalRequest
from .events import CognitiveEvent
from .ports import (
    ActivationStorePort,
    CognitiveEventBusPort,
    MemoryStorePort,
    MemoryStoreSetPort,
)


class InMemoryMemoryStore:
    """Deterministic in-memory store for one memory role."""

    def __init__(self, memory_kind: MemoryKind) -> None:
        self._memory_kind = memory_kind
        self._records: dict[str, LongTermMemoryRecord] = {}

    @property
    def memory_kind(self) -> MemoryKind:
        return self._memory_kind

    def store(self, record: LongTermMemoryRecord) -> LongTermMemoryRecord:
        if record.memory_kind is not self._memory_kind:
            raise ValueError(
                f"record memory_kind {record.memory_kind.value} does not match store role"
            )
        self._records[record.memory_id] = record
        return record

    def get(self, memory_id: str) -> LongTermMemoryRecord | None:
        return self._records.get(memory_id)

    def query(self, request: RetrievalRequest) -> tuple[LongTermMemoryRecord, ...]:
        if self._memory_kind not in request.memory_roles:
            return ()
        return tuple(sorted(self._records.values(), key=lambda item: item.memory_id))

    def records(self) -> tuple[LongTermMemoryRecord, ...]:
        return tuple(sorted(self._records.values(), key=lambda item: item.memory_id))


class InMemoryMemoryStoreSet:
    """In-memory bundle of episodic, semantic, and procedural stores."""

    def __init__(self) -> None:
        self.episodic = InMemoryMemoryStore(MemoryKind.EPISODIC)
        self.semantic = InMemoryMemoryStore(MemoryKind.SEMANTIC)
        self.procedural = InMemoryMemoryStore(MemoryKind.PROCEDURAL)

    def store(self, record: LongTermMemoryRecord) -> LongTermMemoryRecord:
        return self.for_kind(record.memory_kind).store(record)

    def get(self, memory_id: str, *, memory_kind: MemoryKind) -> LongTermMemoryRecord | None:
        return self.for_kind(memory_kind).get(memory_id)

    def for_kind(self, memory_kind: MemoryKind) -> InMemoryMemoryStore:
        if memory_kind is MemoryKind.EPISODIC:
            return self.episodic
        if memory_kind is MemoryKind.SEMANTIC:
            return self.semantic
        if memory_kind is MemoryKind.PROCEDURAL:
            return self.procedural
        raise ValueError(f"unsupported memory kind: {memory_kind}")

    def query_all(self, request: RetrievalRequest) -> tuple[LongTermMemoryRecord, ...]:
        records: list[LongTermMemoryRecord] = []
        for role in request.memory_roles:
            records.extend(self.for_kind(role).query(request))
        return tuple(sorted(records, key=lambda item: (item.memory_kind.value, item.memory_id)))


class InMemoryActivationStore:
    """In-memory activation persistence keyed by node and logical step."""

    def __init__(self) -> None:
        self._values: dict[tuple[str, int], int] = {}

    def write_activation(
        self,
        *,
        node_id: str,
        logical_step: int,
        activation_ppm: int,
    ) -> None:
        self._values[(node_id, logical_step)] = activation_ppm

    def read_activation(self, *, node_id: str, logical_step: int) -> int | None:
        return self._values.get((node_id, logical_step))

    def latest_activation(self, *, node_id: str) -> tuple[int, int] | None:
        matches = [
            (step, ppm)
            for (nid, step), ppm in self._values.items()
            if nid == node_id
        ]
        if not matches:
            return None
        return max(matches, key=lambda item: item[0])


class InMemoryEventBus:
    """Append-only in-memory cognitive event bus."""

    def __init__(self) -> None:
        self._events: list[CognitiveEvent] = []
        self._index: dict[str, int] = {}

    def publish(self, event: CognitiveEvent) -> CognitiveEvent:
        if event.event_id in self._index:
            raise ValueError(f"duplicate event_id: {event.event_id}")
        self._index[event.event_id] = len(self._events)
        self._events.append(event)
        return event

    def read(
        self,
        *,
        after_event_id: str | None = None,
        limit: int = 1000,
    ) -> tuple[CognitiveEvent, ...]:
        start = 0
        if after_event_id is not None:
            if after_event_id not in self._index:
                raise ValueError(f"unknown after_event_id: {after_event_id}")
            start = self._index[after_event_id] + 1
        return tuple(self._events[start : start + limit])

    def replay(self) -> tuple[CognitiveEvent, ...]:
        return tuple(self._events)
