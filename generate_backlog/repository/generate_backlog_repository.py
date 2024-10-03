from abc import abstractmethod, ABC


class GenerateBacklogRepository(ABC):
    @abstractmethod
    def createLoader(self, githubRepositoryPath):
        pass

