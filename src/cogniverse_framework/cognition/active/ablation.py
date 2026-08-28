"""Deterministic ablation helpers for active cognition experiments."""

from __future__ import annotations

from dataclasses import dataclass

from ..perception import PublicPercept
from ..retrieval.scoring import RetrievalRankingPolicy
from .activation import ActivationPolicy
from .coordinator import ActiveCognitionCoordinator, ActiveCognitionCycleResult


@dataclass(frozen=True, slots=True)
class ActiveCognitionAblationConfig:
    """Framework-side ablation switches for controlled lab studies."""

    ablation_id: str
    spreading_enabled: bool = True
    retrieval_enabled: bool = True
    working_capacity: int | None = None

    def apply_activation_policy(self, base: ActivationPolicy) -> ActivationPolicy:
        if self.spreading_enabled:
            return base
        return ActivationPolicy(
            policy_id=f"{base.policy_id}:{self.ablation_id}:no-spread",
            decay_ppm=base.decay_ppm,
            perception_boost_ppm=base.perception_boost_ppm,
            spreading_boost_ppm=0,
            working_threshold_ppm=base.working_threshold_ppm,
            primed_threshold_ppm=base.primed_threshold_ppm,
            retrieval_boost_ppm=base.retrieval_boost_ppm,
        )


def run_ablated_cycle(
    coordinator: ActiveCognitionCoordinator,
    percept: PublicPercept,
    config: ActiveCognitionAblationConfig,
    *,
    goal_node_ids: tuple[str, ...] = (),
) -> ActiveCognitionCycleResult:
    """Run one coordinator cycle with ablation switches applied."""

    if not config.retrieval_enabled:
        return coordinator.receive_percept(percept)
    return coordinator.receive_and_retrieve(percept, goal_node_ids=goal_node_ids)


def build_ablation_coordinator(
    activation_policy: ActivationPolicy,
    retrieval_policy: RetrievalRankingPolicy,
    config: ActiveCognitionAblationConfig,
    *,
    working_capacity: int,
    **kwargs,
) -> ActiveCognitionCoordinator:
    capacity = (
        config.working_capacity
        if config.working_capacity is not None
        else working_capacity
    )
    return ActiveCognitionCoordinator(
        config.apply_activation_policy(activation_policy),
        retrieval_policy,
        working_capacity=capacity,
        **kwargs,
    )
