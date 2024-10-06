from abc import abstractmethod, ABC


class TextProcessingRepository(ABC):
    @abstractmethod
    def postprocessingTextToBacklogs(self, generatedBacklogsText):
        pass

    @abstractmethod
    def getTextFromSourceCode(self, githubRepositoryPath):
        pass
