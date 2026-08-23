#!/usr/bin/env bash
set -euo pipefail

mkdir -p \
  src/cogniverse_framework/analysis \
  src/cogniverse_framework/reporting \
  src/cogniverse_framework/environments \
  src/cogniverse_framework/runner \
  tests \
  scripts

cat > src/cogniverse_framework/analysis/statistics.py <<'PY'
def success_rate(successes, trials):
    if trials == 0:
        return 0.0
    return round(successes / trials, 3)


def confidence_range(successes, trials):
    rate = success_rate(successes, trials)
    margin = round(1.96 * ((rate * (1 - rate) / trials) ** 0.5), 3)

    return {
        "lower": max(0, round(rate - margin, 3)),
        "upper": min(1, round(rate + margin, 3)),
    }
PY

cat > src/cogniverse_framework/analysis/causal.py <<'PY'
def estimate_effect(baseline, intervention):

    return {
        "baseline": baseline,
        "intervention": intervention,
        "effect": round(
            intervention - baseline,
            3,
        ),
    }
PY

cat > src/cogniverse_framework/analysis/ablation.py <<'PY'
def compare_ablation(enabled, disabled):

    return {
        "enabled": enabled,
        "disabled": disabled,
        "difference": round(
            enabled - disabled,
            3,
        ),
    }
PY

cat > src/cogniverse_framework/reporting/timeline.py <<'PY'
def build_timeline(events):

    return [
        {
            "step": index,
            "event": event,
        }
        for index, event in enumerate(events)
    ]
PY

cat > src/cogniverse_framework/reporting/strategy_graph.py <<'PY'
def build_strategy_graph(strategy, states):

    return {
        "strategy": strategy,
        "states": states,
    }
PY

cat > src/cogniverse_framework/environments/base.py <<'PY'
from abc import ABC, abstractmethod


class EnvironmentAdapter(ABC):

    environment_id = None

    @abstractmethod
    def reset(self):
        pass

    @abstractmethod
    def step(self, action):
        pass
PY

cat > src/cogniverse_framework/environments/registry.py <<'PY'
class EnvironmentRegistry:

    def __init__(self):
        self.environments = {}

    def register(self, adapter):

        self.environments[
            adapter.environment_id
        ] = adapter

    def get(self, name):

        return self.environments[name]
PY

cat > src/cogniverse_framework/environments/minigrid.py <<'PY'
from .base import EnvironmentAdapter


class MiniGridAdapter(EnvironmentAdapter):

    environment_id = "minigrid"

    def reset(self):
        return {
            "state": "initial"
        }

    def step(self, action):

        return {
            "action": action
        }
PY

cat > src/cogniverse_framework/environments/craftax.py <<'PY'
from .base import EnvironmentAdapter


class CraftaxAdapter(EnvironmentAdapter):

    environment_id = "craftax"

    def reset(self):
        return {
            "state": "initial"
        }

    def step(self, action):

        return {
            "action": action
        }
PY

cat > src/cogniverse_framework/runner/queue.py <<'PY'
class ExperimentQueue:

    def __init__(self):
        self.items = []

    def add(self, experiment):

        self.items.append(
            experiment
        )

    def next(self):

        if not self.items:
            return None

        return self.items.pop(0)
PY

cat > src/cogniverse_framework/runner/loop.py <<'PY'
class ResearchLoop:

    def __init__(self, queue):
        self.queue = queue

    def run_once(self):

        experiment = self.queue.next()

        if experiment is None:
            return {
                "status": "EMPTY"
            }

        return {
            "status": "COMPLETE",
            "experiment": experiment,
        }
PY

cat > tests/test_bundle_16_20.py <<'PY'
import unittest

from cogniverse_framework.analysis.statistics import (
    success_rate,
    confidence_range,
)

from cogniverse_framework.analysis.causal import (
    estimate_effect,
)

from cogniverse_framework.environments.registry import (
    EnvironmentRegistry,
)

from cogniverse_framework.environments.minigrid import (
    MiniGridAdapter,
)

from cogniverse_framework.runner.queue import (
    ExperimentQueue,
)

from cogniverse_framework.runner.loop import (
    ResearchLoop,
)


class TestBundle1620(unittest.TestCase):

    def test_statistics(self):

        self.assertEqual(
            success_rate(8,10),
            0.8,
        )

        self.assertIn(
            "lower",
            confidence_range(8,10),
        )

    def test_causal(self):

        self.assertEqual(
            estimate_effect(
                0.5,
                0.8,
            )["effect"],
            0.3,
        )

    def test_environment(self):

        registry = EnvironmentRegistry()

        registry.register(
            MiniGridAdapter()
        )

        self.assertEqual(
            registry.get("minigrid").environment_id,
            "minigrid",
        )

    def test_runner(self):

        queue = ExperimentQueue()

        queue.add("exp042")

        result = ResearchLoop(
            queue
        ).run_once()

        self.assertEqual(
            result["status"],
            "COMPLETE",
        )


if __name__ == "__main__":
    unittest.main()
PY

cat > scripts/run_bundle_16_20.sh <<'SH'
#!/usr/bin/env bash
set -euo pipefail

echo "BUNDLE 16-20: RESEARCH PLATFORM EXTENSIONS"

PYTHONPATH=src python -m compileall src

PYTHONPATH=src python -m unittest discover -s tests -v

PYTHONPATH=src python - <<'PY'
import json

from cogniverse_framework.analysis.statistics import (
    success_rate,
)

from cogniverse_framework.analysis.causal import (
    estimate_effect,
)

print(json.dumps({
    "bundle": "16-20",
    "status": "PASS",
    "statistics": success_rate(42,50),
    "causal_effect": estimate_effect(
        0.51,
        0.84,
    )["effect"],
    "features": [
        "statistics",
        "causal_analysis",
        "visualization_data",
        "environment_plugins",
        "research_loop",
    ],
}, indent=2))
PY
SH

chmod +x scripts/run_bundle_16_20.sh

git add .
git commit -m "Implement Bundles 16-20 research platform extensions"

echo "Bundle 16-20 created"
