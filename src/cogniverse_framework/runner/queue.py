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
