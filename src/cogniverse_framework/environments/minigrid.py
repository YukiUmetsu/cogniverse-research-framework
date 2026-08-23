from .base import EnvironmentAdapter


class MiniGridAdapter(EnvironmentAdapter):

    environment_id = "minigrid"

    def reset(self):
        return {
            "state": "initial"
        }

    def step(self, action):

        return {
            "action": action
        }
