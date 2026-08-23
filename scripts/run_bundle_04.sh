#!/usr/bin/env bash
set -euo pipefail

echo "BUNDLE 04: EXP-042 MIGRATION ADAPTER"

PYTHONPATH=src python -m unittest discover -s tests -v

PYTHONPATH=src python - <<'PY'
from cogniverse_framework.adapters.exp042 import Exp042Replay
from cogniverse_framework.replay.ancestry import shared_ancestry

print({
    "adapter": Exp042Replay().name,
    "classification": Exp042Replay().classify({
        "minigrid_reset_or_step_called": False
    }),
    "ancestry": shared_ancestry(
        ["a", "b", "c"],
        ["a", "b", "d"],
    ),
})
PY
