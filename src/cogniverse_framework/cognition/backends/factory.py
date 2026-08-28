"""Factory helpers for swapping cognitive backend implementations."""

from __future__ import annotations

from typing import Any, Literal

from .inmemory import (
    InMemoryActivationStore,
    InMemoryEventBus,
    InMemoryMemoryStoreSet,
)
from .ports import ActivationStorePort, CognitiveEventBusPort, MemoryStoreSetPort

BackendKind = Literal["inmemory", "redis"]


def create_memory_store_set(
    backend: BackendKind = "inmemory",
    *,
    redis_client: Any | None = None,
    key_prefix: str = "cogniverse:memory",
) -> MemoryStoreSetPort:
    if backend == "inmemory":
        return InMemoryMemoryStoreSet()
    if backend == "redis":
        from .redis_backend import RedisMemoryStoreSet

        client = redis_client or _default_redis_client()
        return RedisMemoryStoreSet(client, key_prefix=key_prefix)
    raise ValueError(f"unsupported memory backend: {backend}")


def create_event_bus(
    backend: BackendKind = "inmemory",
    *,
    redis_client: Any | None = None,
    stream_key: str = "cogniverse:cognitive-events",
) -> CognitiveEventBusPort:
    if backend == "inmemory":
        return InMemoryEventBus()
    if backend == "redis":
        from .redis_backend import RedisEventBus

        client = redis_client or _default_redis_client()
        return RedisEventBus(client, stream_key=stream_key)
    raise ValueError(f"unsupported event bus backend: {backend}")


def create_activation_store(
    backend: BackendKind = "inmemory",
    *,
    redis_client: Any | None = None,
    key_prefix: str = "cogniverse:activation",
) -> ActivationStorePort:
    if backend == "inmemory":
        return InMemoryActivationStore()
    if backend == "redis":
        from .redis_backend import RedisActivationStore

        client = redis_client or _default_redis_client()
        return RedisActivationStore(client, key_prefix=key_prefix)
    raise ValueError(f"unsupported activation backend: {backend}")


def _default_redis_client() -> Any:
    from .redis_backend import _require_redis

    redis = _require_redis()
    return redis.Redis()
