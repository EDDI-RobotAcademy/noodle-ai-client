from abc import ABC, abstractmethod


class OpenAIAPIRepository(ABC):
    @abstractmethod
    def generateBacklogText(self, codeText):
        pass