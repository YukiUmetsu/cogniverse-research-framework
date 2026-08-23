from cogniverse_framework.contracts.audit_contract import AuditContract


class ExperimentRunner:

    def __init__(self, manifest, lifecycle):
        self.manifest = manifest
        self.lifecycle = lifecycle

    def run(self):
        contract = AuditContract()

        phases = {}

        phases["preflight"] = self.lifecycle.preflight()
        phases["execute"] = self.lifecycle.execute()
        phases["analyze"] = self.lifecycle.analyze()
        phases["settle"] = self.lifecycle.settle()

        return {
            "experiment_id": self.manifest.experiment_id,
            "status": "COMPLETE",
            "contract": contract.validate(),
            "phases": phases,
        }
