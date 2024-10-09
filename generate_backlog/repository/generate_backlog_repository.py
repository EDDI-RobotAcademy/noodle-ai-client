from abc import abstractmethod, ABC


class GenerateBacklogRepository(ABC):
    @abstractmethod
    def createLoader(self, githubRepositoryPath):
        pass

    @abstractmethod
    def loadDocument(self, loader):
        pass

    @abstractmethod
    def joinDocumentToDocs(self, document):
        pass

    @abstractmethod
    def generateBacklogsText(self, docs):
        pass

    @abstractmethod
    def generateBacklogByOpenAI(self, textFromSourceCode):
        pass