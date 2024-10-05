import os.path
import shutil

from git import Repo

from github_processing.repository.github_processing_repository import GithubProcessingRepository


class GithubProcessingRepositoryImpl(GithubProcessingRepository):
    __instance = None
    GITHUB_URL = "https://github.com"

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)

        return cls.__instance

    @classmethod
    def getInstance(cls):
        if cls.__instance is None:
            cls.__instance = cls()

        return cls.__instance

    async def cloneRespoitory(self, userName, githubRepositoryName):
        GITHUB_REPOSITORY_URL = f"{self.GITHUB_URL}/{userName}/{githubRepositoryName}"
        repositoryPath = f"./github_repositories/{githubRepositoryName}"

        if os.path.exists(repositoryPath):
            shutil.rmtree(repositoryPath)

        Repo.clone_from(GITHUB_REPOSITORY_URL, to_path=repositoryPath)

