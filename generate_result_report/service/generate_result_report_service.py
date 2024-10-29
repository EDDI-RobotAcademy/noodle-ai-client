from abc import abstractmethod, ABC


class GenerateResultReportService(ABC):
    @abstractmethod
    def generateResultReport(self, userToken, *args, ipcExecutorConditionalCustomExecutorChannel=None, **kwargs):
        pass
