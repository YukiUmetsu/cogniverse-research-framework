#!/usr/bin/env bash
set -euo pipefail

mkdir -p \
  src/cogniverse_framework/learning \
  src/cogniverse_framework/analysis \
  tests \
  scripts

cat > src/cogniverse_framework/learning/__init__.py <<'PY'
from .behavior import BehaviorTrace
from .knowledge_state import KnowledgeState
from .strategy_trace import StrategyTrace

__all__ = [
    "BehaviorTrace",
    "KnowledgeState",
    "StrategyTrace",
]
PY

cat > src/cogniverse_framework/learning/behavior.py <<'PY'
from dataclasses import dataclass, asdict


@dataclass
class BehaviorTrace:

    state: str
    decision: str
    action: str
    result: str

    def to_dict(self):
        return asdict(self)
PY

cat > src/cogniverse_framework/learning/knowledge_state.py <<'PY'
from dataclasses import dataclass, field


@dataclass
class KnowledgeState:

    concepts: list = field(default_factory=list)
    strategies: list = field(default_factory=list)

    def add_concept(self, concept):
        if concept not in self.concepts:
            self.concepts.append(concept)

    def add_strategy(self, strategy):
        if strategy not in self.strategies:
            self.strategies.append(strategy)

    def snapshot(self):
        return {
            "concepts": sorted(self.concepts),
            "strategies": sorted(self.strategies),
        }
PY

cat > src/cogniverse_framework/learning/strategy_trace.py <<'PY'
from dataclasses import dataclass, asdict


@dataclass
class StrategyTrace:

    strategy: str
    reason: str
    confidence: float

    def to_dict(self):
        return asdict(self)
PY

cat > src/cogniverse_framework/analysis/__init__.py <<'PY'
from .learning_delta import compare_knowledge

__all__ = [
    "compare_knowledge",
]
PY

cat > src/cogniverse_framework/analysis/learning_delta.py <<'PY'
def compare_knowledge(before, after):

    before_concepts = set(
        before.get("concepts", [])
    )

    after_concepts = set(
        after.get("concepts", [])
    )

    before_strategies = set(
        before.get("strategies", [])
    )

    after_strategies = set(
        after.get("strategies", [])
    )

    return {
        "new_concepts": sorted(
            after_concepts - before_concepts
        ),
        "removed_concepts": sorted(
            before_concepts - after_concepts
        ),
        "new_strategies": sorted(
            after_strategies - before_strategies
        ),
        "removed_strategies": sorted(
            before_strategies - after_strategies
        ),
    }
PY

cat > tests/test_bundle_11_learning.py <<'PY'
import unittest

from cogniverse_framework.learning import (
    BehaviorTrace,
    KnowledgeState,
    StrategyTrace,
)

from cogniverse_framework.analysis import (
    compare_knowledge,
)


class TestBundle11(unittest.TestCase):

    def test_behavior_trace(self):

        trace = BehaviorTrace(
            "state-a",
            "continue",
            "move",
            "success",
        )

        self.assertEqual(
            trace.to_dict()["state"],
            "state-a",
        )

    def test_knowledge_delta(self):

        before = KnowledgeState()

        before.add_strategy(
            "random_exploration"
        )

        after = KnowledgeState()

        after.add_strategy(
            "information_guided_exploration"
        )

        result = compare_knowledge(
            before.snapshot(),
            after.snapshot(),
        )

        self.assertIn(
            "information_guided_exploration",
            result["new_strategies"],
        )


if __name__ == "__main__":
    unittest.main()
PY

cat > scripts/run_bundle_11.sh <<'SH'
#!/usr/bin/env bash
set -euo pipefail

echo "BUNDLE 11: LEARNER BEHAVIOR EVIDENCE"

PYTHONPATH=src python -m compileall src

PYTHONPATH=src python -m unittest discover -s tests -v

PYTHONPATH=src python - <<'PY'
import json

from cogniverse_framework.learning import (
    KnowledgeState,
    StrategyTrace,
)

from cogniverse_framework.analysis import (
    compare_knowledge,
)

before = KnowledgeState(
    strategies=[
        "random_exploration"
    ]
)

after = KnowledgeState(
    concepts=[
        "frontier_value"
    ],
    strategies=[
        "information_guided_exploration"
    ]
)

delta = compare_knowledge(
    before.snapshot(),
    after.snapshot(),
)

trace = StrategyTrace(
    "information_guided_exploration",
    "higher_expected_information_gain",
    0.8,
)

print(json.dumps({
    "bundle": "11",
    "learning_evidence": "PASS",
    "new_strategies": delta["new_strategies"],
    "trace": trace.to_dict(),
}, indent=2))
PY
SH

chmod +x scripts/run_bundle_11.sh

git add .
git commit -m "Implement Bundle 11 learner behavior evidence layer"

echo "Bundle 11 created"
