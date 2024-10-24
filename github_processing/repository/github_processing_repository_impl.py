import asyncio
import os.path
import shutil

from git import Repo

from github_processing.repository.github_processing_repository import GithubProcessingRepository
from template.utility.color_print import ColorPrinter


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

    async def cloneRepository(self, userName, githubRepositoryName, githubBranchName):
        ColorPrinter.print_important_message(f"github_processing_repository_impl -> cloneRepository()")
        GITHUB_REPOSITORY_URL = f"{self.GITHUB_URL}/{userName}/{githubRepositoryName}"
        ColorPrinter.print_important_message(f"GITHUB_REPOSITORY_URL: {GITHUB_REPOSITORY_URL}")

        repositoryPath = f"./github_repositories/{githubRepositoryName}"
        ColorPrinter.print_important_message(f"repositoryPath: {repositoryPath}")

        try:
            Repo.clone_from(GITHUB_REPOSITORY_URL, to_path=repositoryPath, branch=githubBranchName)
        except Exception as e:
            ColorPrinter.print_important_message(f"Error while cloning Repository: {e}!")

    async def deleteRepository(self, githubRepositoryPath):
        shutil.rmtree(githubRepositoryPath)
        await asyncio.sleep(0.5)
