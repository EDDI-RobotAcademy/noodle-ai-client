import asyncio
import json

from generate_backlog.repository.generate_backlog_repository_impl import GenerateBacklogRepositoryImpl
from generate_backlog.service.generate_backlog_service import GenerateBacklogService
from github_processing.repository.github_processing_repository_impl import GithubProcessingRepositoryImpl
from template.utility.color_print import ColorPrinter
from text_processing.repository.text_processing_repository_impl import TextProcessingRepositoryImpl


class GenerateBacklogServiceImpl(GenerateBacklogService):
    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
            cls.__instance.__generateBacklogRepository = GenerateBacklogRepositoryImpl.getInstance()
            cls.__instance.__githubProcessingRepository = GithubProcessingRepositoryImpl.getInstance()
            cls.__instance.__textProcessingRepository = TextProcessingRepositoryImpl.getInstance()

        return cls.__instance

    @classmethod
    def getInstance(cls):
        if cls.__instance is None:
            cls.__instance = cls()

        return cls.__instance

    async def generate(self, *args):
        loop = asyncio.get_running_loop()

        ColorPrinter.print_important_message(f"service -> arg: {args[0]}")
        # ColorPrinter.print_important_message(f"service -> kwargs: {kwargs}")

        data = args[0].split()
        userName = data[0]
        githubRepositoryName = data[1]
        githubBranchName = data[2]

        ColorPrinter.print_important_message(f"service -> generate() userName: {userName}")
        ColorPrinter.print_important_message(f"service -> generate() githubRepositoryName: {githubRepositoryName}")
        ColorPrinter.print_important_message(f"service -> generate() githubBranchName: {githubBranchName}")

        ColorPrinter.print_important_message("Before clone a repository.")
        await self.__githubProcessingRepository.cloneRepository(userName, githubRepositoryName)
        ColorPrinter.print_important_message("After clone a repository.")

        githubRepositoryPath = f"./github_repositories/{githubRepositoryName}"

        ColorPrinter.print_important_message("Before create loader")
        loader = await self.__generateBacklogRepository.createLoader(githubRepositoryPath)
        ColorPrinter.print_important_message("After create loader")
        ColorPrinter.print_important_message("Before load document")
        document = self.__generateBacklogRepository.loadDocument(loader)
        ColorPrinter.print_important_message("After load document")
        ColorPrinter.print_important_message("Before join document")
        docs = self.__generateBacklogRepository.joinDocumentToDocs(document)
        ColorPrinter.print_important_message("After load document")

        ColorPrinter.print_important_message("Before generate text")
        generatedBacklogsText = await self.__generateBacklogRepository.generateBacklogsText(docs)
        ColorPrinter.print_important_message("After generate text")
        ColorPrinter.print_important_message(f"GeneratedBacklogText: {generatedBacklogsText}")
        ColorPrinter.print_important_message("Before postprocessing text")
        parsedBacklogText = await self.__textProcessingRepository.postprocessingTextToBacklogs(generatedBacklogsText)
        ColorPrinter.print_important_message("After postprocessing text")

        backlogList = []

        for backlogInfo in parsedBacklogText:
            backlogList.append([backlogInfo["backlogName"],backlogInfo["domainName"], backlogInfo["successCriteria"], backlogInfo["todo"]])
        ColorPrinter.print_important_message(f"backlogList: {backlogList}")
        return {"message": backlogList}

    async def example(self, *arg, **kwargs):
        print(f"service -> example()")

        text = ""
        with open("/Users/j213h/Jh/SK-Networks-AI-Camp/Projects/Noodle/noodle-ai-client/code_analysis/gpt.txt", "r") as f:
            text += f.read()

        parsedBacklogText = self.__textProcessingRepository.postprocessingTextToBacklogs(text)
        backlogList = []

        for backlogInfo in parsedBacklogText:
            backlogList.append([backlogInfo["backlogName"], backlogInfo["domainName"], backlogInfo["successCriteria"],
                                backlogInfo["todo"]])

        return {"message": backlogList}

    async def generateBacklogByOpenAI(self, *args):
        ColorPrinter.print_important_message(f"service -> arg: {args[0]}")

        data = args[0].split()
        userName = data[0]
        githubRepositoryName = data[1]
        githubBranchName = data[2]

        await self.__githubProcessingRepository.cloneRepository(userName, githubRepositoryName)
        githubRepositoryPath = f"./github_repositories/{githubRepositoryName}"
        textFromSourceCode = await self.__textProcessingRepository.getTextFromSourceCode(githubRepositoryPath)

        generatedBacklog = await self.__generateBacklogRepository.generateBacklogByOpenAI(textFromSourceCode)

        backlogToJson = json.dumps({
            "backlogList": generatedBacklog
        })

        return backlogToJson
