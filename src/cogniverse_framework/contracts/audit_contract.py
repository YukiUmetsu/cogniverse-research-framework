from dataclasses import dataclass


@dataclass
class AuditContract:
    fresh_seed_block_opened: bool = False
    heldout_seed_block_opened: bool = False
    environment_reset_called: bool = False

    def validate(self):
        failures = []

        if self.fresh_seed_block_opened:
            failures.append("fresh_seed_block_opened")

        if self.heldout_seed_block_opened:
            failures.append("heldout_seed_block_opened")

        if self.environment_reset_called:
            failures.append("environment_reset_called")

        return {
            "validated": not failures,
            "failures": failures,
        }
