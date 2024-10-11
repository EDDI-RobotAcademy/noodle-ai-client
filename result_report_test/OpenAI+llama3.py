import json
import os
from typing import List, Dict, Any
import re

import openai
from dotenv import load_dotenv
from llama_cpp import Llama
from transformers import AutoTokenizer

load_dotenv()
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


PROMPT = \
'''당신은 유용한 AI 어시스턴트입니다. 사용자의 질의에 대해 한국어로 친절하고 정확하게 답변해야 합니다.
You are a useful AI assistant. You should answer your questions kindly and accurately in Korean.'''

def create_backlog_with_openai(source_code):
    prompt = (
        "You are generating an Agile backlog from the following source code. "
        "Each backlog item should include a title, success criteria, domain separation, and task list."
        "You have to write so that only one domain exists in one backlog."
        "Additionally, please make a list of the language and frameworks based on the source code."
        "Lastly, if there is anything more to supplement among the code contents, please write it down."
        "If the most perfect code is 100 points, please write down the score and the reason for the source code below in detail.\n\n"
        "You should answer in Korean."
        f"Source code:\n{source_code}\n"
        
        "Answer:"
        "Languages: (Used programming languages in source code)"
        "Frameworks: (Used frameworks in source code)"
        "Supplements: (Supplements you judged)"
        "Scores of source code: "
        "   - Security Aspect: (Score you judged)"
        "   - Code Structure and Maintainability Aspect: (Score you judged)"
        "   - Overall score: (Score you judged)"
    )

    messages = [
        {
            "role": "system", "content": PROMPT,
        },
        {
            "role": "user", "content": prompt
        }
    ]

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.0,
        max_tokens=1500
    )

    return response.choices[0].message.content


def process_repository_for_backlog(repo_path):
    complete_backlog = ""
    text = ""
    for root, _, files in os.walk(repo_path):
        for file in files:
            if file.endswith('.py'):  # 필요한 확장자만 선택
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    file_text = f.read()
                    if len(file_text) >= 512:
                        text += f"File:{file_path}\n{file_text}\n"

    if text:
        backlog = create_backlog_with_openai(text)
        complete_backlog += f"Backlogs for project: {backlog}\n"

    return complete_backlog

repository_path = "./github_repositories/noodle-backend"
backlogs = process_repository_for_backlog(repository_path)
print(backlogs)


def extract_backlog_items(backlogs):
    # 각 백로그 항목을 분리
    title_pattern = r"- \*\*제목\*\*: (.+)"
    criteria_pattern = r"- \*\*성공 기준\*\*: (.+)"
    domain_pattern = r"- \*\*도메인 분리\*\*: (.+)"
    tasks_pattern = r"- \*\*작업 목록\*\*:(?:\n\s+\d+\.\s+.+)+"

    # 각 백로그 항목에서 제목, 성공 기준, 도메인 분리, 작업 목록 추출 함수
    titles = re.findall(title_pattern, backlogs)
    success_criteria = re.findall(criteria_pattern, backlogs)
    domains = re.findall(domain_pattern, backlogs)

    # 작업 목록 추출 및 개별 작업 항목으로 분리
    raw_tasks = re.findall(tasks_pattern, backlogs)
    tasks = [re.findall(r"\d+\.\s+(.+)", task_block) for task_block in raw_tasks]

    return titles, success_criteria, domains, tasks

titles, success_criteria, domains, tasks = extract_backlog_items(backlogs)
print(titles)
print(success_criteria)
print(domains)
print(tasks)

# json_items = json.dumps({
#     'backlog_items': extracted_items
# }, ensure_ascii=False, indent=2)

model_id = 'MLP-KTLim/llama-3-Korean-Bllossom-8B-gguf-Q4_K_M'
tokenizer = AutoTokenizer.from_pretrained(model_id)
llm = Llama.from_pretrained(
	repo_id=model_id,
	filename="llama-3-Korean-Bllossom-8B-Q4_K_M.gguf",
    n_gpu_layers=-1,
    n_ctx=3000,
    flash_attn=True
)

generation_kwargs = {
            "max_tokens": 512,
            "stop": ["<|eot_id|>"],
            "top_p": 0.9,
            "temperature": 0.0,
            "echo": False,  # Echo the prompt in the output
            # "stream": True
        }

# template = f""""You have an Agile backlog generated from the project. "
#         "Please generate a detailed project report based on this backlog. "
#         "Highlight the main tasks, success criteria, and overall project structure."
#         "Please print it out in Korean.\n\n"
#         f"Backlog:\n{backlogs}\n"
#         Answer:"""
template = f"""
당신은 애자일 프로젝트 관리자이자 기술 문서 작성 전문가입니다. 아래 제공되는 프로젝트 백로그 정보를 바탕으로 상세한 프로젝트 결과 보고서를 작성해주세요.

**백로그 항목**
{backlogs}
# 요청 사항\n
**다음 구조로 프로젝트 결과 보고서를 작성해주세요**:

**프로젝트 제목**
    - 빈 칸으로 남겨주세요.

**프로젝트 개요**
    - 빈 칸으로 남겨주세요.
    
**기술 스택**
    - 빈 칸으로 남겨주세요.


**주요 성과**

    - 각 백로그 항목별 구현 결과
    - 성공 기준 달성 여부
    - 주요 기술적 결정사항


**프로젝트 지표**

    - 계획 대비 실제 구현 비율
    - 품질 메트릭스 (테스트 커버리지, 버그 수 등)
    - 성능 지표


**도전 과제 및 해결 방안**

    - 직면한 주요 기술적 문제
    - 채택한 해결 방안
    - 학습된 교훈


**향후 개선사항**

    - 추가 개발이 필요한 영역
    - 확장 가능성
    - 유지보수 고려사항


**톤앤매너**

    - 전문적이고 객관적인 어조 유지
    - 기술적 내용과 비즈니스 가치를 균형있게 서술
    - 구체적인 예시와 데이터 포함

**특별 지침**

    - 각 백로그 항목의 성공 기준을 기반으로 구현 결과를 평가해주세요
    - 기술적 용어는 필요한 경우 간단한 설명을 덧붙여주세요"""

messages = [
            {"role": "system", "content": f"{PROMPT}"},
            {"role": "user", "content": f"{template}"}
]

prompt = tokenizer.apply_chat_template(
    messages,
    tokenize=False,
    add_generation_prompt=True
)

response_msg = llm(prompt, **generation_kwargs)

response_text = response_msg['choices'][0]['text']
print(response_text)

def extract_sections(text):
    # 텍스트를 줄 단위로 분할
    lines = text.split('\n')

    sections = {}
    current_title = None
    current_content = []

    for line in lines:
        # '#' 하나로 시작하는 메인 제목 찾기
        title_match = re.match(r'^#\s+([^#].+)$', line)

        if title_match:
            # 새로운 제목을 찾았을 때, 이전 섹션 저장
            if current_title:
                sections[current_title] = '\n'.join(current_content).strip()

            # 새로운 섹션 시작
            current_title = title_match.group(1)
            current_content = []
        else:
            # 제목이 아닌 경우 현재 섹션의 내용으로 추가
            if current_title and line.strip():  # 빈 줄 제외
                current_content.append(line)

    # 마지막 섹션 저장
    if current_title:
        sections[current_title] = '\n'.join(current_content).strip()

    return sections

print(extract_sections(response_text))