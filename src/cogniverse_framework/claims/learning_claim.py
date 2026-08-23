from dataclasses import dataclass, field


@dataclass
class LearningClaim:

    strategy: str
    confidence: float
    supporting_states: list = field(default_factory=list)
    counter_examples: list = field(default_factory=list)

    def validate(self):

        return {
            "valid": (
                bool(self.strategy)
                and 0 <= self.confidence <= 1
            ),
            "strategy": self.strategy,
            "confidence": self.confidence,
            "supporting_states": self.supporting_states,
            "counter_examples": self.counter_examples,
        }
