import os
import re
import shutil

from git import Repo
from langchain_community.document_loaders.generic import GenericLoader
from langchain_community.document_loaders.parsers import LanguageParser
from langchain_text_splitters import Language
from mlx_lm import load, generate, stream_generate
from mlx_lm.utils import generate_step
import mlx.core as mx

model, tokenizer = load("mlx-community/Llama-3.2-3B-Instruct-4bit")


def cloneRespoitory(userName, githubRepositoryName):
    GITHUB_REPOSITORY_URL = f"https://www.github.com/{userName}/{githubRepositoryName}"
    repositoryPath = f"./github_repositories/{githubRepositoryName}"

    if os.path.exists(repositoryPath):
        shutil.rmtree(repositoryPath)

    Repo.clone_from(GITHUB_REPOSITORY_URL, to_path=repositoryPath)


def createLoader(githubRepositoryPath):
    loader = GenericLoader.from_filesystem(
        githubRepositoryPath,
        glob="**/*",
        suffixes=[".py"],
        exclude=["**/non-utf8-encoding.py", "**/__init__.py", "**/asgi.py", "**/settings.py", "**/wsgi.py",
                 "**/migrations/*", "**/admin.py", "**/apps.py", "**/tests.py", "**/urls.py", "**/manage.py"],
        parser=LanguageParser(language=Language.PYTHON, parser_threshold=100)
    )

    return loader


def loadDocument(loader):
    return loader.load()


def joinDocumentToDocs(document):
    return "\n".join([document[i].page_content for i in range(len(document))])


userName = "EDDI-RobotAcademy"
githubRepositoryName = "noodle-backend"
githubRepositoryPath = f"./github_repositories/{githubRepositoryName}"

cloneRespoitory(userName, githubRepositoryName)

loader = createLoader(githubRepositoryPath)

document = loadDocument(loader)

docs = joinDocumentToDocs(document)

template = f"""
        1. **도메인 및 기능 분석 요청**
           - "다음은 여러 파이썬 파일의 내용을 합친 텍스트입니다. 
           이 텍스트에서 도메인과 기능을 분석하고, 
           각 도메인 내에서 확인한 기능들에 대해 애자일 프로세스의 백로그를 생성해 주세요. 
           단, 하나의 도메인 내의 repository와 service가 같이 존재할 경우 하나의 백로그로 작성해주세요.
           예시) generate_backlog_repository | generate_backlog_service -> 도메인 이름: generate_backlog
           필요할 경우 여러 도메인의 백로그 항목으로 나누어 주세요:

        텍스트: {docs}

        2. **애자일 프로세스 백로그 생성**
           - "도메인별로 구분된 각 기능에 대해 백로그 항목을 작성해 주세요. 각 항목은 다음 정보를 포함해야 합니다:
             - 백로그 제목: 기능이나 작업의 요약
             - 도메인 이름: 관련된 도메인 식별
             - Success Criteria: 기능의 성공을 평가할 수 있는 기준
             - To-do 목록: 해당 기능을 구현하기 위해 필요한 단계별 작업



        Assistant:
        """

messages = [
    {"role": "user", "content": template}
]

prompt = tokenizer.apply_chat_template(
    messages, tokenize=False, add_generation_prompt=True
)

print(mx.default_stream(mx.default_device()))
# generate_step()
response = stream_generate(model, tokenizer, prompt=prompt,
                           max_tokens=2048, temp=0.00, repetition_penalty=1.25,
                           repetition_context_size=12, top_p=0.95, min_p=0.1)

text = ""
for chunk in response:
    text += chunk

print(text)
# pattern = re.compile(
#     r"\*\*백로그 제목:\*\* (.+?)\n\s*\+ 도메인 이름: (.+?)\n\s* \*\*Success Criteria:\*\* (.+?)\n\s*- \*\*To-do 목록:\*\*(.+?)(?=\n\d|\Z)", re.S)

def extract_backlog_info(text):
    # 각 백로그 항목을 분리하여 반복 처리
    backlogs = re.split(r'(?=\*\*백로그 제목:\*\*)', text)

    # 첫 번째 백로그가 빈 값일 수 있으므로 필터링
    backlogs = [backlog for backlog in backlogs if backlog.strip()]

    # 각 항목에서 정보를 추출하여 리스트에 저장
    backlog_list = []
    for backlog in backlogs:
        backlog_title = re.search(r'\*\*백로그 제목:\*\*\s*(.*)', backlog)
        domain_name = re.search(r'\+ 도메인 이름:\s*`(.*)`', backlog)
        success_criteria = re.search(r'\*\*Success Criteria:\*\*\s*(.*)', backlog)

        # To-do 목록에서 "도메인"이나 "Success Criteria"로 시작하는 문장을 제외하고, 앞에 붙은 \t나 공백 제거
        todo_list = re.findall(r'^\s*\d+\.\s*(?!도메인|Success Criteria)(.*)', backlog, re.MULTILINE)

        # 앞에 붙은 탭이나 공백 제거
        todo_list = [todo.strip() for todo in todo_list]

        backlog_data = {
            '백로그 제목': backlog_title.group(1) if backlog_title else None,
            '도메인 이름': domain_name.group(1) if domain_name else None,
            'Success Criteria': success_criteria.group(1) if success_criteria else None,
            'To-do 목록': todo_list if todo_list else None
        }
        backlog_list.append(backlog_data)

    return backlog_list

backlogList = extract_backlog_info(text)
print(backlogList)

# # 추출된 결과 저장
# backlogs = pattern.findall(text)
#
# print(backlogs)