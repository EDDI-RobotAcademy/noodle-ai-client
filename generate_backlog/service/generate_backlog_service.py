from abc import abstractmethod, ABC


class GenerateBacklogService(ABC):
    @abstractmethod
    def generate(self, *args):
        pass

    @abstractmethod
    def generateBacklogByOpenAI(self, *args):
        pass
