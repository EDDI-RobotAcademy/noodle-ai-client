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
You are a helpful AI assistant, you'll need to answer users' queries in a friendly and accurate manner.'''

def create_backlog_with_openai(source_code):
    prompt = (
        "You are generating an Agile backlog from the following source code. "
        "Each backlog item should include a title, success criteria, domain separation, and task list.\n\n"
        f"Source code:\n{source_code}\n"
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
        temperature=0.2,
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
                        text += file_text + "\n"

    if text:
        backlog = create_backlog_with_openai(text)
        complete_backlog += f"Backlogs for project: {backlog}\n"

    return complete_backlog

repository_path = "./github_repositories/noodle-backend"
backlogs = process_repository_for_backlog(repository_path)
print(backlogs)


def extract_backlog_items(backlogs) -> List[Dict[str, Any]]:
    # 각 백로그 항목을 분리
    backlog_sections = re.split(r'###\s+백로그\s+항목\s+\d+:', backlogs)[1:]

    backlog_items = []
    for section in backlog_sections:
        item = parse_backlog_section(section)
        if item:
            backlog_items.append(item)

    return backlog_items

def parse_backlog_section(section: str) -> Dict[str, Any]:
    # 제목 추출
    title_match = re.search(r'-\s+\*\*제목\*\*:\s+(.+?)(?=\n|$)', section)

    # 성공 기준 추출
    success_criteria_start = section.find('- **성공 기준**:')
    success_criteria_end = section.find('- **도메인 분리**:')

    if success_criteria_start == -1 or title_match is None:
        return {'title': None, 'success_criteria': None}

    if success_criteria_end == -1:
        success_criteria_text = section[success_criteria_start:]
    else:
        success_criteria_text = section[success_criteria_start:success_criteria_end]

    # 성공 기준 항목들을 리스트로 추출
    success_criteria = re.findall(r'-\s+(.+?)(?=\n|$)',
                                  success_criteria_text.split('- **성공 기준**:')[1].strip())

    return {
        'title': title_match.group(1).strip(),
        'success_criteria': [criterion.strip() for criterion in success_criteria if criterion.strip()]
    }

extracted_items = extract_backlog_items(backlogs)
print(extracted_items)

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
            "temperature": 0.2,
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

# 입력 정보
**프로젝트 기본 정보**

**프로젝트명**: [프로젝트 이름(전체 프로젝트 내용을 포괄하는 하나의 주제를 작성해주세요.)]

**백로그 항목**
{backlogs}
# 요청 사항\n
**다음 구조로 프로젝트 결과 보고서를 작성해주세요**:

**프로젝트 개요**

    - 목적 및 목표
    - 주요 이해관계자
    - 전반적인 접근 방식

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