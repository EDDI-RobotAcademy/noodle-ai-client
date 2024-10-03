from abc import abstractmethod, ABC


class GithubProcessingRepository(ABC):
    @abstractmethod
    def cloneRespoitory(self, userName, githubRepositoryName):
        pass