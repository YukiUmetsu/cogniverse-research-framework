from dataclasses import dataclass


@dataclass
class ReplaySession:

    seed: int
    events: list

    def validate_replay_only(self):

        violations = []

        for event in self.events:
            if event.get("reset_called"):
                violations.append(
                    "environment_reset"
                )

            if event.get("step_called"):
                violations.append(
                    "environment_step"
                )

        return {
            "valid": len(violations) == 0,
            "violations": violations,
        }

    def event_count(self):
        return len(self.events)
