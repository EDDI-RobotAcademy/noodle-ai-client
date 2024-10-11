from abc import abstractmethod, ABC


class GenerateResultReportRepository(ABC):
    @abstractmethod
    def generate(self, generatedBacklog):
        pass