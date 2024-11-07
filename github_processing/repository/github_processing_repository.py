from abc import abstractmethod, ABC


class GithubProcessingRepository(ABC):
    @abstractmethod
    def cloneRepository(self, userName, githubRepositoryName, githubBranchName):
        pass

    @abstractmethod
    def deleteRepository(self, githubRepositoryPath):
        pass
