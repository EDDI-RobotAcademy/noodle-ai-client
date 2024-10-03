from langchain_community.document_loaders.generic import GenericLoader
from langchain_community.document_loaders.parsers import LanguageParser
from langchain_text_splitters import Language

from generate_backlog.repository.generate_backlog_repository import GenerateBacklogRepository


class GenerateBacklogRepositoryImpl(GenerateBacklogRepository):
    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)

        return cls.__instance

    @classmethod
    def getInstance(cls):
        if cls.__instance is None:
            cls.__instance = cls()

        return cls.__instance

    def createLoader(self, githubRepositoryPath):
        loader = GenericLoader.from_filesystem(
            githubRepositoryPath,
            glob="**/*",
            suffixes=[".py"],
            exclude=["**/non-utf8-encoding.py", "**/__init__.py", "**/asgi.py", "**/settings.py", "**/wsgi.py",
                     "**/migrations/*", "**/admin.py", "**/apps.py", "**/tests.py", "**/urls.py", "**/manage.py"],
            parser=LanguageParser(language=Language.PYTHON, parser_threshold=100)
        )

        return loader

