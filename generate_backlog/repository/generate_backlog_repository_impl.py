import asyncio
import concurrent.futures
import os

import openai
from dotenv import load_dotenv
from langchain_community.document_loaders.generic import GenericLoader
from langchain_community.document_loaders.parsers import LanguageParser
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_text_splitters import Language

from generate_backlog.repository.generate_backlog_repository import GenerateBacklogRepository

load_dotenv()

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

    async def createLoader(self, githubRepositoryPath):
        try:
            loader = GenericLoader.from_filesystem(
                githubRepositoryPath,
                glob="**/*",
                suffixes=[".py"],
                exclude=["**/non-utf8-encoding.py", "**/__init__.py", "**/asgi.py", "**/settings.py", "**/wsgi.py",
                         "**/migrations/*", "**/admin.py", "**/apps.py", "**/tests.py", "**/urls.py", "**/manage.py"],
                parser=LanguageParser(language=Language.PYTHON, parser_threshold=100)
            )
            return loader
        except Exception as e:
            print(f"Error creating loader: {e}")
            return None

    def loadDocument(self, loader):
        try:
            return loader.load()
        except Exception as e:
            print(f"Error loading document: {e}")
            return None

    def joinDocumentToDocs(self, document):
        try:
            return "\n".join([document[i].page_content for i in range(len(document))])
        except Exception as e:
            print(f"Error joining document to docs: {e}")
            return None

    def modelCall(self, model, prompt, docs):
        try:
            chain = (
                {"context": lambda x: docs}
                | prompt
                | model
                | StrOutputParser()
            )

            result = chain.invoke(input="")
            return result
        except Exception as e:
            print(f"Error during model call: {e}")
            return None

    async def generateBacklogsText(self, docs):
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

        이 과정을 통해 생성된 백로그 항목들을 예시와 같은 형식으로 출력해 주세요."

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

        try:
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
                temperature=0.05
            )

            loop = asyncio.get_running_loop()

            with concurrent.futures.ThreadPoolExecutor() as pool:
                output = await loop.run_in_executor(
                    pool,
                    self.modelCall,
                    llm,
                    prompt,
                    docs
                )

            return output
        except Exception as e:
            print(f"Error generating backlogs text: {e}")
            return None

    async def generateBacklogByOpenAI(self, textFromSourceCode):
        client = openai.AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        systemPrompt = \
        '''당신은 유용한 AI 어시스턴트입니다. 사용자의 질의에 대해 한국어로 친절하고 정확하게 답변해야 합니다.
        You are a helpful AI assistant, You should answer your questions kindly and accurately in Korean.'''

        userPrompt = (
            "<head>REMAINDER: YOU HAVE TO ANSWER IN KOREAN!</head>"
            "You are generating an Agile backlog from the following source code. "
            "Each backlog item should include a 백로그 제목, Success Criteria, 도메인 이름, and To-do 목록."
            "## An Example of backlog ##"
            
            "**Input Example**"
            "<example>"
            "import sys"
            "a = int(sys.stdin.readline())"
            "b = int(sys.stdin.readline())"
            "print(a + b)"
            "</example>"
            
            "**Output Example**"
            "<example>"
            "Language: Python"
            "Frameworks: sys"
            "Agile Process Backlog"
            "1. **백로그 제목**: 두 수의 합을 출력합니다."
            "    - **Success Criteria**: 두 수를 입력받고 그 합을 출력할 수 있어야 합니다."
            "    - **도메인 이름**: 계산"
            "    - **To-do 목록**:"
            "         - 두 수를 입력받습니다."
            "         - 두 수의 합을 계산합니다."
            "         - 계산된 합을 출력합니다."
            "</example>"
            
            "Additionally, please make a list of the language and frameworks based on the source code."
            "Lastly, if there is anything more to supplement among the code contents, please write it down."
            "If the most perfect code is 100 points, please decide what the source code below is and write it.\n\n"
            f"Source code:\n{textFromSourceCode}\n"

            "Answer:"
            "Languages: (Used programming languages in source code)"
            "Frameworks: (Used frameworks in source code)"
            "Agile Process Backlogs: (Backlogs you made)"
            "Supplements: (Supplements you judged)"
            "Scores of source code: "
            "   - Security Aspect: (Integer score you judged)"
            "   - Code Structure and Maintainability Aspect: (Integer score you judged)"
            "   - Overall score: (Integer score you judged)"
        )

        messages = [
            {
                "role": "system", "content": systemPrompt,
            },
            {
                "role": "user", "content": userPrompt
            }
        ]

        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.0,
            max_tokens=1500,
            top_p=0.01,
            seed=1
        )

        return response.choices[0].message.content
