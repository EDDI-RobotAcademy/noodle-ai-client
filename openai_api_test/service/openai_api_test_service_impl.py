from starlette import status

from github_processing.repository.github_processing_repository_impl import GithubProcessingRepositoryImpl
from openai_api_test.repository.openai_api_test_repository_impl import OpenAIAPIRepositoryImpl
from openai_api_test.service.openai_api_test_service import OpenAIAPIService
from template.utility.color_print import ColorPrinter
from text_processing.repository.text_processing_repository_impl import TextProcessingRepositoryImpl
from fastapi.responses import JSONResponse

class OpenAIAPIServiceImpl(OpenAIAPIService):
    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
            cls.__instance.__openaiAPIRepository = OpenAIAPIRepositoryImpl.getInstance()
            cls.__instance.__githubProcessingRepository = GithubProcessingRepositoryImpl.getInstance()
            cls.__instance.__textProcessingRepository = TextProcessingRepositoryImpl.getInstance()

        return cls.__instance

    @classmethod
    def getInstance(cls):
        if cls.__instance is None:
            cls.__instance = cls()

        return cls.__instance

    async def generateBacklog(self, *args, **kwargs):
        argList = args[0].split()
        userName = argList[0]
        githubRepositoryName = argList[1]

        ColorPrinter.print_important_message(f"service -> generateBacklog() userName: {userName}")
        ColorPrinter.print_important_message(f"service -> generateBacklog() githubRepositoryName: {githubRepositoryName}")
        await self.__githubProcessingRepository.cloneRespoitory(userName, githubRepositoryName)
        ColorPrinter.print_important_message("After clone repository")
        githubRepositoryPath = f"./github_repositories/{githubRepositoryName}"

        codeText = self.__textProcessingRepository.getTextFromSourceCode(githubRepositoryPath)
        ColorPrinter.print_important_message("After get text from source code")

        generatedText = await self.__openaiAPIRepository.generateBacklogText(codeText)
        ColorPrinter.print_important_message("After generate Backlog Text")

        return generatedText
