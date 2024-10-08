import json
import os
from typing import List, Dict, Any
import re

import openai
from dotenv import load_dotenv

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
