import asyncio
import json

from conditional_custom_executor_test_point.repository.conditional_custom_executor_test_point_repository_impl import \
    ConditionalCustomExecutorTestPointRepositoryImpl
from conditional_custom_executor_test_point.service.conditional_custom_executor_test_point_service_impl import \
    ConditionalCustomExecutorTestPointServiceImpl
from generate_backlog.repository.generate_backlog_repository_impl import GenerateBacklogRepositoryImpl
from generate_result_report.repository.generate_result_report_repository_impl import GenerateResultReportRepositoryImpl
from generate_result_report.service.generate_result_report_service import GenerateResultReportService
from github_processing.repository.github_processing_repository_impl import GithubProcessingRepositoryImpl
from send_to_django.repository.send_to_django_repository_impl import SendToDjangoRepositoryImpl
from template.utility.color_print import ColorPrinter
from text_processing.repository.text_processing_repository_impl import TextProcessingRepositoryImpl


class GenerateResultReportServiceImpl(GenerateResultReportService):
    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
            cls.__instance.__generateResultReportRepository = GenerateResultReportRepositoryImpl.getInstance()
            cls.__instance.__githubProcessingRepository = GithubProcessingRepositoryImpl.getInstance()
            cls.__instance.__generateBacklogRepository = GenerateBacklogRepositoryImpl.getInstance()
            cls.__instance.__textProcessingRepository = TextProcessingRepositoryImpl.getInstance()
            cls.__instance.__sendToDjangoRepository = SendToDjangoRepositoryImpl.getInstance()

        return cls.__instance

    @classmethod
    def getInstance(cls):
        if cls.__instance is None:
            cls.__instance = cls()

        return cls.__instance

    async def generateResultReport(self, *args, ipcExecutorConditionalCustomExecutorChannel=None, **kwargs):
        loop = asyncio.get_running_loop()
        ColorPrinter.print_important_message(f"args: {args}")
        ColorPrinter.print_important_message(f"args[0]: {args[0]}")
        ColorPrinter.print_important_message(f"args[1]: {args[1]}")
        ColorPrinter.print_important_message(f"args[2]: {args[2]}")
        ColorPrinter.print_important_message(f"args[3]: {args[3]}")
        # data = args[0][1:-1].split(", ")
        # ColorPrinter.print_important_message(f"service -> generate() data: {data}")
        # userName = data[0][1:-1]
        # githubRepositoryName = data[1][1:-1]
        # githubBranchName = data[2][1:-1]
        # ColorPrinter.print_important_message(f"service -> generate() data: {data}")

        userName = args[0]
        ColorPrinter.print_important_message(f"service -> generate() userName: {userName}, type: {type(userName)}")
        githubRepositoryName = args[1]
        ColorPrinter.print_important_message(f"service -> generate() githubRepositoryName: {githubRepositoryName}, type: {type(githubRepositoryName)}")
        githubBranchName = args[2]
        ColorPrinter.print_important_message(f"service -> generate() githubBranchName: {githubBranchName}, type: {type(githubBranchName)}")
        ipcExecutorConditionalCustomExecutorChannel = args[3]
        ColorPrinter.print_important_message(f"service -> generate() ipcExecutorConditionalCustomExecutorChannel: {ipcExecutorConditionalCustomExecutorChannel}")
        ColorPrinter.print_important_message("Before clone the repository.")
        try:
            await self.__githubProcessingRepository.cloneRepository(userName, githubRepositoryName, githubBranchName)
        except Exception as e:
            ColorPrinter.print_important_message("An error occurred while cloning the repository.")
        githubRepositoryPath = f"./github_repositories/{githubRepositoryName}"
        ColorPrinter.print_important_message("After clone the repository.")

        ColorPrinter.print_important_message("Before get text from the source code.")
        try:
            textFromSourceCode = await self.__textProcessingRepository.getTextFromSourceCode(githubRepositoryPath)
        except Exception as e:
            ColorPrinter.print_important_message("An error occurred while getting text from source code.")
        ColorPrinter.print_important_message("After get text from the source code.")

        ColorPrinter.print_important_message("Before remove github repository.")
        try:
            await self.__githubProcessingRepository.deleteRepository(githubRepositoryPath)
        except Exception as e:
            ColorPrinter.print_important_message("An error occurred while deleting the repository.")
        ColorPrinter.print_important_message("After remove github repository.")

        ColorPrinter.print_important_message("Before generate backlog by openai.")
        try:
            generatedBacklog = await self.__generateBacklogRepository.generateBacklogByOpenAI(textFromSourceCode)
        except Exception as e:
            ColorPrinter.print_important_message("An error occurred while generating backlog.")
        ColorPrinter.print_important_message("After generate backlog by openai.")

        ColorPrinter.print_important_message("Before postprocessing text to backlog.")
        try:
            backlogList = await self.__textProcessingRepository.postprocessingTextToBacklogs(generatedBacklog)
        except Exception as e:
            ColorPrinter.print_important_message("An error occurred while postprocessing text to backlog.")
        ColorPrinter.print_important_message("After postprocessing text to backlog.")

        # userName = await self.__conditionalCustomExecutorRepository.operate("test", intermediateData=backlogList)
        userToken = await self.__sendToDjangoRepository.sendBacklogToDjango(
            ipcExecutorConditionalCustomExecutorChannel, "test", backlogList)



        ColorPrinter.print_important_message("Before generate the report.")
        generatedResultReport = await self.__generateResultReportRepository.generate(generatedBacklog)
        ColorPrinter.print_important_message("After generate the report.")
        ColorPrinter.print_important_message(f"generatedResultReport: {generatedResultReport}")

        ColorPrinter.print_important_message("Before extract sections.")
        sections = await self.__textProcessingRepository.extractSections(generatedResultReport)
        ColorPrinter.print_important_message("After extract sections.")
        ColorPrinter.print_important_message(f"sections: {sections}")

        title = sections["title"]
        overview = sections["overview"]
        tech_stack = sections["tech_stack"]
        features = sections["features"]
        usage = sections["usage"]
        improvement = sections["improvement"]
        completion = sections["completion"]
        ColorPrinter.print_important_message(f"title: {title}")
        ColorPrinter.print_important_message(f"overview: {overview}")
        ColorPrinter.print_important_message(f"tech_stack: {tech_stack}")
        ColorPrinter.print_important_message(f"features: {features}")
        ColorPrinter.print_important_message(f"usage: {usage}")
        ColorPrinter.print_important_message(f"improvement: {improvement}")
        ColorPrinter.print_important_message(f"completion: {completion}")

        ColorPrinter.print_important_message("Before extract tech stack.")
        extractedTechStack = await self.__textProcessingRepository.extractTechStack(tech_stack)
        ColorPrinter.print_important_message("After extract tech stack.")

        ColorPrinter.print_important_message("Before extract subsections.")
        extractedFeatures = await self.__textProcessingRepository.extractFeatures(features)
        ColorPrinter.print_important_message("After extract subsections.")
        ColorPrinter.print_important_message(f"extractedFeatures: {extractedFeatures}")

        ColorPrinter.print_important_message("Before extract subsections.(score)")
        extractedScore = await self.__textProcessingRepository.extractScore(completion)
        ColorPrinter.print_important_message("After extract subsections.(score)")
        ColorPrinter.print_important_message(f"scores: {extractedScore}")
        # 마지막 출력 체크
        ColorPrinter.print_important_message(f"title: {title}")
        ColorPrinter.print_important_message(f"overview: {overview}")
        ColorPrinter.print_important_message(f"extractedTechStack: {extractedTechStack}")
        ColorPrinter.print_important_message(f"extractedFeatures: {extractedFeatures}")
        ColorPrinter.print_important_message(f"usage: {usage}")
        ColorPrinter.print_important_message(f"improvement: {improvement}")
        ColorPrinter.print_important_message(f"extractedScore: {extractedScore}")

        data = {
            "title": title,
            "overview": overview,
            "techStack": extractedTechStack,
            "featureList": extractedFeatures,
            "usage": usage,
            "improvement": improvement,
            "scoreList": extractedScore
        }
        ColorPrinter.print_important_message(f"data: {data}")

        dataToJson = json.dumps(data, indent=2)
        return {"message": dataToJson}
