from dataclasses import dataclass


@dataclass
class MutationAnalysis:

    baseline: dict
    candidate: dict

    def compare(self):

        changed = []

        for seed in sorted(
            set(self.baseline)
            | set(self.candidate)
        ):
            if (
                self.baseline.get(seed)
                != self.candidate.get(seed)
            ):
                changed.append(seed)

        return {
            "changed_seeds": changed,
            "changed_count": len(changed),
        }
