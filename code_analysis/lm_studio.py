import os
from typing import List

from langchain_core.embeddings import Embeddings
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI
from openai import OpenAI
from git import Repo
from langchain_community.document_loaders.generic import GenericLoader
from langchain_community.document_loaders.parsers import LanguageParser
from langchain_text_splitters import Language


# Clone
repo_path = "./github_repositories"
# repo = Repo.clone_from("https://github.com/SKNETWORKS-FAMILY-AICAMP/SKN02-4th-3Team", to_path=repo_path)
 
# Load
loader = GenericLoader.from_filesystem(
    repo_path,
    glob="**/*",
    suffixes=[".py"],
    exclude=["**/non-utf8-encoding.py", "**/__init__.py", "**/asgi.py", "**/settings.py", "**/wsgi.py", "**/migrations/*", "**/admin.py", "**/apps.py", "**/tests.py", "**/urls.py", "**/manage.py"],
    parser=LanguageParser(language=Language.PYTHON, parser_threshold=100)
)
documents = loader.load()
print(len(documents))

docs = "\n".join([documents[i].page_content for i in range(len(documents))])


# Splitting
# python_splitter = RecursiveCharacterTextSplitter.from_language(
#     language=Language.PYTHON, chunk_size=1000, chunk_overlap=150
# )
#
# texts = python_splitter.split_documents(documents)
# print(len(texts))

# Custom Embedding
# Embeddings을 상속해야하고,
# 내부에 embed_documents와 embed_query가 정의되어야 한다.
# class LMStudioEmbeddings(Embeddings):
#     def __init__(self, base_url, api_key="lm_studio"):
#         self.client = OpenAI(base_url=base_url, api_key=api_key)
#
#     def embed_documents(self, textList: List[str], model="nomic-ai/nomic-embed-text-v1.5-GGUF") -> List[List[float]]:
#         # textList = list(map(lambda text: text.replace("\n", " "), textList))
#         # print(textList)
#         datas = self.client.embeddings.create(input=textList, model=model).data
#         return list(map(lambda data: data.embedding, datas))
#
#     def embed_query(self, text: str) -> List[float]:
#         return self.embed_documents([text])[0]


# embed = LMStudioEmbeddings(base_url="http://localhost:1234/v1")
#
#
# RAG
# vectorstore = FAISS.from_documents(texts, embedding=embed, distance_strategy=DistanceStrategy.COSINE)
# retriever = vectorstore.as_retriever(search_kwargs={"k": 150})

# template = """
# Please analyze the following source code and extract the individual functionalities implemented in the code.
# source code: {context}
#
# Present the analysis in a structured format that makes it easy to preprocess the data and extract the functionalities. Follow these guidelines:
#
# 1. If there are classes in the code, provide the information in the following structured format:
#    - **Class Name:**
#      - **Method:**
#        - Method Name: Detailed explanation of the method's functionality
#
# 2. If there are no classes but only functions, provide the information in the following structured format:
#    - **Function:**
#      - Function Name: Detailed explanation of the function's functionality
#
# 3. If there are neither classes nor functions, provide an overview of the entire code and break down the functionalities into separate items in the following structured format:
#    - **Code Segment:**
#      - Segment Description: Detailed explanation of the functionality
#
# User: {question}
# """

# template = """프로젝트에 대해 프로젝트 맥락에 맞게 주요 함수 및 메서드 단위 기능 중심으로 백로그들을 만드십시오.
# 주요 언어는 Python 입니다.
#
# context: {docs}
#
# 백로그 작성 전략은 다음과 같습니다.
# 1. 각 함수 및 메서드들에 대해 `Success Criteria`와 이에 따른 `To Do`로 나눌 것.
# 2. getInstance() 메서드는 백로그에서 제외할 것.
# 3. 필요한 것 이외에는 말하지 않을 것.
#
# user: {question}
# """

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

# user_input = "Tell me in Korean. Ensure to clearly outline the role and purpose of each functionality, as this information will be used to create backlog items for an Agile development process."
user_input = """
코드를 기반으로 직접 백로그 제목과 성공 기준, 해야 할 일을 생성해 주세요.
백로그 항목을 작성할 때, 기능에 맞는 백로그 제목, 성공 여부를 판단할 Success Criteria, 그리고 해결해야 할 To-do 목록을 포함해 주세요.
To-do 목록은 더 이상 세부 사항으로 나눠질 수 없어야 합니다.
"""

for chunk in chain.stream(input=""):
    print(chunk, end="")
