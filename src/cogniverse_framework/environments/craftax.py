from .base import EnvironmentAdapter


class CraftaxAdapter(EnvironmentAdapter):

    environment_id = "craftax"

    def reset(self):
        return {
            "state": "initial"
        }

    def step(self, action):

        return {
            "action": action
        }
