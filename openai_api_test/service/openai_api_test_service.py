from abc import ABC, abstractmethod


class OpenAIAPIService(ABC):
    @abstractmethod
    def generateBacklog(self, *args, **kwargs):
        pass
