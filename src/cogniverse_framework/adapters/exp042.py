from dataclasses import dataclass


@dataclass
class Exp042Replay:
    name: str = "exp042"

    def classify(self, runtime):
        return {
            "experiment": self.name,
            "classification": (
                "REPLAY_ONLY"
                if runtime.get("minigrid_reset_or_step_called") is False
                else "ENVIRONMENT_EXECUTION"
            ),
        }

    def compare(self, baseline, candidate):
        changed = []

        seeds = set(baseline) | set(candidate)

        for seed in sorted(seeds):
            if baseline.get(seed) != candidate.get(seed):
                changed.append(seed)

        return {
            "changed_seeds": changed,
            "baseline_count": len(baseline),
            "candidate_count": len(candidate),
        }
