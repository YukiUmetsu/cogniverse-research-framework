"""Optional Redis-backed cognitive backends.

Redis is an implementation detail, not a cognitive theory requirement.
Install ``redis`` separately when selecting these backends.
"""

from __future__ import annotations

import json
from typing import Any

from ..state import MemoryKind
from ..retrieval.records import LongTermMemoryRecord
from ..retrieval.requests import RetrievalRequest
from .events import CognitiveEvent, CognitiveEventKind
from .inmemory import InMemoryMemoryStore, InMemoryMemoryStoreSet


def _require_redis():
    try:
        import redis
    except ImportError as exc:
        raise ImportError(
            "Redis backends require the optional 'redis' package. "
            "Install it in the consumer environment before selecting backend='redis'."
        ) from exc
    return redis


class RedisMemoryStore:
    """Redis hash-backed store for one long-term memory role."""

    def __init__(
        self,
        client: Any,
        *,
        memory_kind: MemoryKind,
        key_prefix: str = "cogniverse:memory",
    ) -> None:
        self._client = client
        self._memory_kind = memory_kind
        self._key_prefix = key_prefix.rstrip(":")

    @property
    def memory_kind(self) -> MemoryKind:
        return self._memory_kind

    def _hash_key(self) -> str:
        return f"{self._key_prefix}:{self._memory_kind.value}"

    def store(self, record: LongTermMemoryRecord) -> LongTermMemoryRecord:
        if record.memory_kind is not self._memory_kind:
            raise ValueError(
                f"record memory_kind {record.memory_kind.value} does not match store role"
            )
        self._client.hset(
            self._hash_key(),
            record.memory_id,
            record.canonical_json(),
        )
        return record

    def get(self, memory_id: str) -> LongTermMemoryRecord | None:
        raw = self._client.hget(self._hash_key(), memory_id)
        if raw is None:
            return None
        if isinstance(raw, bytes):
            raw = raw.decode("utf-8")
        payload = json.loads(raw)
        return _record_from_dict(payload)

    def query(self, request: RetrievalRequest) -> tuple[LongTermMemoryRecord, ...]:
        if self._memory_kind not in request.memory_roles:
            return ()
        raw_items = self._client.hgetall(self._hash_key())
        records = []
        for raw in raw_items.values():
            if isinstance(raw, bytes):
                raw = raw.decode("utf-8")
            records.append(_record_from_dict(json.loads(raw)))
        return tuple(sorted(records, key=lambda item: item.memory_id))


class RedisMemoryStoreSet:
    """Redis bundle matching MemoryStoreSetPort."""

    def __init__(self, client: Any, *, key_prefix: str = "cogniverse:memory") -> None:
        self.episodic = RedisMemoryStore(
            client, memory_kind=MemoryKind.EPISODIC, key_prefix=key_prefix
        )
        self.semantic = RedisMemoryStore(
            client, memory_kind=MemoryKind.SEMANTIC, key_prefix=key_prefix
        )
        self.procedural = RedisMemoryStore(
            client, memory_kind=MemoryKind.PROCEDURAL, key_prefix=key_prefix
        )

    def store(self, record: LongTermMemoryRecord) -> LongTermMemoryRecord:
        return self.for_kind(record.memory_kind).store(record)

    def get(self, memory_id: str, *, memory_kind: MemoryKind) -> LongTermMemoryRecord | None:
        return self.for_kind(memory_kind).get(memory_id)

    def for_kind(self, memory_kind: MemoryKind) -> RedisMemoryStore:
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


class RedisEventBus:
    """Redis Streams-backed cognitive event bus."""

    def __init__(self, client: Any, *, stream_key: str = "cogniverse:cognitive-events") -> None:
        self._client = client
        self._stream_key = stream_key

    def publish(self, event: CognitiveEvent) -> CognitiveEvent:
        self._client.xadd(
            self._stream_key,
            {"payload": event.canonical_json()},
            id=f"{event.logical_step * 1_000_000}-*",
        )
        return event

    def read(
        self,
        *,
        after_event_id: str | None = None,
        limit: int = 1000,
    ) -> tuple[CognitiveEvent, ...]:
        start = "-" if after_event_id is None else f"({after_event_id}"
        entries = self._client.xrange(self._stream_key, min=start, max="+", count=limit)
        return tuple(_event_from_stream_entry(entry_id, fields) for entry_id, fields in entries)

    def replay(self) -> tuple[CognitiveEvent, ...]:
        return self.read(limit=100_000)


class RedisActivationStore:
    """Redis hash-backed activation store keyed by node and logical step."""

    def __init__(self, client: Any, *, key_prefix: str = "cogniverse:activation") -> None:
        self._client = client
        self._key_prefix = key_prefix.rstrip(":")

    def _field(self, node_id: str, logical_step: int) -> str:
        return f"{node_id}:{logical_step:09d}"

    def write_activation(
        self,
        *,
        node_id: str,
        logical_step: int,
        activation_ppm: int,
    ) -> None:
        self._client.hset(
            self._key_prefix,
            self._field(node_id, logical_step),
            str(activation_ppm),
        )

    def read_activation(self, *, node_id: str, logical_step: int) -> int | None:
        raw = self._client.hget(self._key_prefix, self._field(node_id, logical_step))
        if raw is None:
            return None
        if isinstance(raw, bytes):
            raw = raw.decode("utf-8")
        return int(raw)

    def latest_activation(self, *, node_id: str) -> tuple[int, int] | None:
        prefix = f"{node_id}:"
        raw_items = self._client.hgetall(self._key_prefix)
        matches: list[tuple[int, int]] = []
        for field, value in raw_items.items():
            if isinstance(field, bytes):
                field = field.decode("utf-8")
            if isinstance(value, bytes):
                value = value.decode("utf-8")
            if not field.startswith(prefix):
                continue
            step = int(field.removeprefix(prefix))
            matches.append((step, int(value)))
        if not matches:
            return None
        return max(matches, key=lambda item: item[0])


def _record_from_dict(payload: dict[str, Any]) -> LongTermMemoryRecord:
    kind = MemoryKind(payload["memory_kind"])
    return LongTermMemoryRecord(
        memory_id=payload["memory_id"],
        memory_kind=kind,
        source_system=payload["source_system"],
        logical_step=payload["logical_step"],
        content_sha256=payload["content_sha256"],
        evidence_ids=tuple(payload.get("evidence_ids", ())),
        related_node_ids=tuple(payload.get("related_node_ids", ())),
    )


def _event_from_stream_entry(entry_id: str | bytes, fields: dict[Any, Any]) -> CognitiveEvent:
    if isinstance(entry_id, bytes):
        entry_id = entry_id.decode("utf-8")
    payload_raw = fields.get(b"payload") or fields.get("payload")
    if isinstance(payload_raw, bytes):
        payload_raw = payload_raw.decode("utf-8")
    event = CognitiveEvent.from_dict(json.loads(payload_raw))
    if event.event_id != entry_id and not event.event_id:
        pass
    return event
