from abc import abstractmethod, ABC


class GenerateResultReportService(ABC):
    @abstractmethod
    def generateResultReport(self, *args):
        pass