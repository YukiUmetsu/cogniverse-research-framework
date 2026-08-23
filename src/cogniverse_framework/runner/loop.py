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
