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
