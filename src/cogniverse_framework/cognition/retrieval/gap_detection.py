"""Deterministic cognitive gap detection from active cognition snapshots."""

from __future__ import annotations

from ..active.graph import ActiveCognitiveGraph, EdgeRelation, NodeCategory
from ..active.snapshot import ActiveCognitionSnapshot
from .gaps import CognitiveGap, GapKind


def detect_cognitive_gaps(
    snapshot: ActiveCognitionSnapshot,
    *,
    source_system: str = "gap-detector",
    low_confidence_threshold_ppm: int = 400_000,
) -> tuple[CognitiveGap, ...]:
    """Detect missing-information gaps from the current active graph."""

    if (
        isinstance(low_confidence_threshold_ppm, bool)
        or not isinstance(low_confidence_threshold_ppm, int)
        or not 0 <= low_confidence_threshold_ppm <= 1_000_000
    ):
        raise ValueError("low_confidence_threshold_ppm must be an integer from 0 to 1000000")

    graph = snapshot.graph
    gaps: list[CognitiveGap] = []
    counter = 0

    for node in graph.nodes:
        if node.category is NodeCategory.EVENT and not _has_incoming_relation(
            graph, node.node_id, EdgeRelation.POSSIBLE_CAUSE
        ):
            counter += 1
            gaps.append(
                _gap(
                    counter,
                    GapKind.UNKNOWN_CAUSE,
                    node.node_id,
                    snapshot.logical_step,
                    source_system,
                    evidence_ids=(f"active-graph:{graph.digest()[:16]}",),
                )
            )

        if (
            node.confidence_ppm is not None
            and node.confidence_ppm < low_confidence_threshold_ppm
        ):
            counter += 1
            gaps.append(
                _gap(
                    counter,
                    GapKind.LOW_PREDICTION_CONFIDENCE,
                    node.node_id,
                    snapshot.logical_step,
                    source_system,
                    urgency_ppm=1_000_000 - node.confidence_ppm,
                    evidence_ids=(f"active-graph:{graph.digest()[:16]}",),
                )
            )

        if node.category is NodeCategory.GOAL and not _has_outgoing_relation(
            graph, node.node_id, EdgeRelation.REQUIRES
        ):
            counter += 1
            gaps.append(
                _gap(
                    counter,
                    GapKind.UNKNOWN_GOAL_PRECONDITION,
                    node.node_id,
                    snapshot.logical_step,
                    source_system,
                    evidence_ids=(f"active-graph:{graph.digest()[:16]}",),
                )
            )

    for left_id, right_id in _contradicting_belief_pairs(graph):
        counter += 1
        gaps.append(
            _gap(
                counter,
                GapKind.UNRESOLVED_BELIEF_CONFLICT,
                left_id,
                snapshot.logical_step,
                source_system,
                evidence_ids=(f"belief-conflict:{right_id}",),
            )
        )

    return tuple(sorted(gaps, key=lambda item: item.gap_id))


def _gap(
    counter: int,
    kind: GapKind,
    subject_node_id: str,
    logical_step: int,
    source_system: str,
    *,
    urgency_ppm: int | None = None,
    evidence_ids: tuple[str, ...] = (),
) -> CognitiveGap:
    return CognitiveGap(
        gap_id=f"gap-{counter:04d}",
        kind=kind,
        subject_node_id=subject_node_id,
        source_system=source_system,
        logical_step=logical_step,
        urgency_ppm=urgency_ppm,
        evidence_ids=evidence_ids,
    )


def _has_incoming_relation(
    graph: ActiveCognitiveGraph,
    node_id: str,
    relation: EdgeRelation,
) -> bool:
    for edge in graph.edges:
        if edge.target_id == node_id and edge.relation is relation:
            return True
    return False


def _has_outgoing_relation(
    graph: ActiveCognitiveGraph,
    node_id: str,
    relation: EdgeRelation,
) -> bool:
    for edge in graph.edges:
        if edge.source_id == node_id and edge.relation is relation:
            return True
    return False


def _contradicting_belief_pairs(graph: ActiveCognitiveGraph) -> tuple[tuple[str, str], ...]:
    beliefs = {
        node.node_id
        for node in graph.nodes
        if node.category is NodeCategory.BELIEF
    }
    pairs: set[tuple[str, str]] = set()
    for edge in graph.edges:
        if edge.relation is not EdgeRelation.CONTRADICTS:
            continue
        if edge.source_id in beliefs and edge.target_id in beliefs:
            pairs.add(tuple(sorted((edge.source_id, edge.target_id))))
    return tuple(sorted(pairs))
