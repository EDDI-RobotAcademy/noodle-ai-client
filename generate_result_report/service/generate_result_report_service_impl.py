import asyncio
import json

from generate_backlog.repository.generate_backlog_repository_impl import GenerateBacklogRepositoryImpl
from generate_result_report.repository.generate_result_report_repository_impl import GenerateResultReportRepositoryImpl
from generate_result_report.service.generate_result_report_service import GenerateResultReportService
from github_processing.repository.github_processing_repository_impl import GithubProcessingRepositoryImpl
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

        return cls.__instance

    @classmethod
    def getInstance(cls):
        if cls.__instance is None:
            cls.__instance = cls()

        return cls.__instance

    async def generateResultReport(self, *args):
        loop = asyncio.get_running_loop()

        data = args[0].split()
        userName = data[0]
        githubRepositoryName = data[1]
        githubBranchName = data[2]

        ColorPrinter.print_important_message(f"service -> generate() userName: {userName}")
        ColorPrinter.print_important_message(f"service -> generate() githubRepositoryName: {githubRepositoryName}")
        ColorPrinter.print_important_message(f"service -> generate() githubBranchName: {githubBranchName}")

        ColorPrinter.print_important_message("Before clone the repository.")
        await self.__githubProcessingRepository.cloneRepository(userName, githubRepositoryName)
        githubRepositoryPath = f"./github_repositories/{githubRepositoryName}"
        ColorPrinter.print_important_message("After clone the repository.")

        ColorPrinter.print_important_message("Before get text from the source code.")
        textFromSourceCode = await self.__textProcessingRepository.getTextFromSourceCode(githubRepositoryPath)
        ColorPrinter.print_important_message("After get text from the source code.")

        ColorPrinter.print_important_message("Before generate backlog by openai.")
        generatedBacklog = await self.__generateBacklogRepository.generateBacklogByOpenAI(textFromSourceCode)
        ColorPrinter.print_important_message("After generate backlog by openai.")

        ColorPrinter.print_important_message("Before postprocessing text to backlog.")
        backlogList = await self.__textProcessingRepository.postprocessingTextToBacklogs(generatedBacklog)
        ColorPrinter.print_important_message("After postprocessing text to backlog.")

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