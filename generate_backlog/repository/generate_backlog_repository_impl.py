from langchain_community.document_loaders.generic import GenericLoader
from langchain_community.document_loaders.parsers import LanguageParser
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
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

    def loadDocument(self, loader):
        return loader.load()

    def joinDocumentToDocs(self, document):
        return "\n".join([document[i].page_content for i in range(len(document))])

    def generateBacklogsText(self, docs):
        template = """
        1. **도메인 및 기능 분석 요청**
           - "다음은 여러 파이썬 파일의 내용을 합친 텍스트입니다. 
           이 텍스트에서 도메인과 기능을 분석하고, 
           각 도메인 내에서 확인한 기능들에 대해 애자일 프로세스의 백로그를 생성해 주세요. 
           필요할 경우 여러 도메인의 백로그 항목으로 나누어 주세요:

        텍스트: {context}

        2. **애자일 프로세스 백로그 생성**
           - "도메인별로 구분된 각 기능에 대해 백로그 항목을 작성해 주세요. 각 항목은 다음 정보를 포함해야 합니다:
             - **백로그 제목:** 기능이나 작업의 요약
             - **도메인 이름:** 관련된 도메인 식별
             - **Success Criteria:** 기능의 성공을 평가할 수 있는 기준
             - **To-do 목록:** 해당 기능을 구현하기 위해 필요한 단계별 작업

        이 과정을 통해 생성된 백로그 항목들만 출력해 주세요."

        ### 최종 출력 예시

        생성된 애자일 프로세스 백로그 항목은 아래와 같이 출력될 수 있습니다:

        ```
        백로그 제목: 사용자 인증 관리 기능 구현
        도메인 이름: 사용자 관리
        Success Criteria: 사용자 로그인 및 인증 토큰 발급이 성공적으로 수행된다.
        To-do:
        - 사용자 로그인 기능 개발
        - 인증 토큰 발급 로직 구현
        - 오류 처리 및 예외 상황 테스트

        백로그 제목: 데이터 분석 모듈 개발
        도메인 이름: 데이터 분석
        Success Criteria: 다양한 입력 데이터를 처리하고 분석 결과를 올바르게 출력한다.
        To-do:
        - 데이터 수집 기능 구현
        - 데이터 필터링 및 가공 로직 개발
        - 분석 결과 시각화 기능 추가
        ```

        Assistant:
        """

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "당신은 사용자를 도와서 애자일 프로세스 백로그를 작성해주는 어시스턴트입니다.",
                ),
                (
                    "human",
                    template
                )
            ]
        )

        llm = ChatOpenAI(
            base_url="http://localhost:1234/v1",
            api_key="lm_studio",
            model="hugging-quants/Llama-3.2-3B-Instruct-Q4_K_M-GGUF",
            temperature=0.1
        )

        chain = (
                {"context": lambda x: docs}
                | prompt
                | llm
                | StrOutputParser()
        )

        generatedText = chain.invoke(input="")

        return generatedText
