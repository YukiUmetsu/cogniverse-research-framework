from abc import ABC, abstractmethod


class EnvironmentAdapter(ABC):

    environment_id = None

    @abstractmethod
    def reset(self):
        pass

    @abstractmethod
    def step(self, action):
        pass
