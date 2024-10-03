from generate_backlog.repository.generate_backlog_repository_impl import GenerateBacklogRepositoryImpl
from generate_backlog.service.generate_backlog_service import GenerateBacklogService
from github_processing.repository.github_processing_repository_impl import GithubProcessingRepositoryImpl
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

    def generate(self, *arg, **kwargs):
        userName = arg[0]
        githubRepositoryName = arg[1]
        githubBranchName = arg[2]

        print(f"service -> generate() userName: {userName}")
        print(f"service -> generate() githubRepositoryName: {githubRepositoryName}")
        print(f"service -> generate() githubBranchName: {githubBranchName}")

        self.__githubProcessingRepository.cloneRespoitory(userName, githubRepositoryName)

        githubRepositoryPath = f"./github_repositories/{githubRepositoryName}"

        loader = self.__generateBacklogRepository.createLoader(githubRepositoryPath)
        document = self.__generateBacklogRepository.loadDocument(loader)
        docs = self.__generateBacklogRepository.joinDocumentToDocs(document)

        generatedBacklogsText = self.__generateBacklogRepository.generateBacklogsText(docs)
