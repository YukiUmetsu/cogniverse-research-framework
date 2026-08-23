from dataclasses import dataclass, asdict
from datetime import datetime
import hashlib
import json


@dataclass
class RunRecord:

    experiment_id: str
    status: str

    def create(self):

        payload = {
            "experiment_id": self.experiment_id,
            "status": self.status,
            "timestamp": datetime.utcnow().isoformat(),
        }

        encoded = json.dumps(
            payload,
            sort_keys=True,
        ).encode()

        payload["run_id"] = hashlib.sha256(
            encoded
        ).hexdigest()[:16]

        return payload
