from abc import abstractmethod, ABC


class TextProcessingRepository(ABC):
    @abstractmethod
    def postprocessingTextToBacklogs(self, generatedBacklogsText):
        pass

    @abstractmethod
    def getTextFromSourceCode(self, githubRepositoryPath):
        pass

    @abstractmethod
    def extractSections(self, text):
        pass

    @abstractmethod
    def extractFeatures(self, text):
        pass

    @abstractmethod
    def extractScore(self, score):
        pass