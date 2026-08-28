"""In-memory reference stores for long-term memory ports."""

from __future__ import annotations

from ..state import MemoryKind
from .records import LongTermMemoryRecord
from .requests import RetrievalRequest


class InMemoryMemoryStore:
    """Simple deterministic store backing one memory role."""

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

    def query(self, request: RetrievalRequest) -> tuple[LongTermMemoryRecord, ...]:
        if self._memory_kind not in request.memory_roles:
            return ()
        return tuple(
            sorted(self._records.values(), key=lambda item: item.memory_id)
        )

    def records(self) -> tuple[LongTermMemoryRecord, ...]:
        return tuple(sorted(self._records.values(), key=lambda item: item.memory_id))


class InMemoryMemoryStoreSet:
    """Convenience bundle of role-specific in-memory stores."""

    def __init__(self) -> None:
        self.episodic = InMemoryMemoryStore(MemoryKind.EPISODIC)
        self.semantic = InMemoryMemoryStore(MemoryKind.SEMANTIC)
        self.procedural = InMemoryMemoryStore(MemoryKind.PROCEDURAL)

    def store(self, record: LongTermMemoryRecord) -> LongTermMemoryRecord:
        return self.for_kind(record.memory_kind).store(record)

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
