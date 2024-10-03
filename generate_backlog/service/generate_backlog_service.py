from abc import abstractmethod, ABC


class GenerateBacklogService(ABC):
    @abstractmethod
    def generate(self, *arg, **kwargs):
        pass
