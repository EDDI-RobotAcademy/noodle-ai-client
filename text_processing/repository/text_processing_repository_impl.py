import asyncio
import os
import re
from concurrent.futures.thread import ThreadPoolExecutor

import aiofiles

from template.utility.color_print import ColorPrinter
from text_processing.repository.text_processing_repository import TextProcessingRepository


class TextProcessingRepositoryImpl(TextProcessingRepository):
    __instance = None
    executor = ThreadPoolExecutor()

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)

        return cls.__instance

    @classmethod
    def getInstance(cls):
        if cls.__instance is None:
            cls.__instance = cls()

        return cls.__instance

    async def postprocessingTextToBacklogs(self, generatedBacklogsText):
        pattern = r'#### \d+\. (.*?)\n- \*\*제목\*\*: (.*?)\n- \*\*성공 기준\*\*: (.*?)\n- \*\*도메인 분리\*\*: (.*?)\n- \*\*작업 목록\*\*:(.*?)(?=\n\n|$)'

        backlogItems = re.findall(pattern, generatedBacklogsText, re.DOTALL)

        backlogList = []
        for item in backlogItems:
            backlog = {
                '기능': item[0].strip(),
                '제목': item[1].strip(),
                '성공 기준': item[2].strip(),
                '도메인 분리': item[3].strip(),
                '작업 목록': [f"1. {task.strip()}" for task in re.findall(r'\d+\. (.*?)(?=\n\d+\.|\n\n|$)', item[4], re.DOTALL)]
            }
            backlogList.append(backlog)

        return backlogList

    async def process_file(self, filePath):
        async with aiofiles.open(filePath, mode='r', encoding='utf-8') as f:
            content = await f.read()
            if len(content) < 512:
                return ""
        return f"File: {filePath}\n{content}\n"


    async def async_os_walk(self, path):
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(self.executor, list, os.walk(path))

    async def getTextFromSourceCode(self, githubRepositoryPath):
        text = ""

        tasks = []
        osPath = await self.async_os_walk(githubRepositoryPath)
        for root, dirs, files in osPath:
            for file in files:
                name, ext = os.path.splitext(file)
                if ext == ".py":
                    filePath = os.path.join(root, file)
                    tasks.append(self.process_file(filePath))

        results = await asyncio.gather(*tasks)

        for result in results:
            text += result

        return text

    async def extractSections(self, text: str):
        pattern_map = {
            'title': r'## 프로젝트 제목\n(.*?)\n',
            'overview': r'## 프로젝트 개요\n(.*?)\n## 기술 스택',
            'tech_stack': r'## #기술 스택\n(.*?)\n## 주요 기능',
            'features': r'## 주요 기능\n(.*?)\n## 활용 방안',
            'usage': r'## 활용 방안\n(.*?)\n## 보완할 점',
            'improvement': r'## 보완할 점\n(.*?)\n## 완성도',
            'completion': r'## 완성도\n(.*?)$'
        }

        # 추출 결과를 저장할 딕셔너리 생성
        sections = {}

        for key, pattern in pattern_map.items():
            result = re.search(pattern, text, re.DOTALL)
            if result:
                sections[key] = result.group(1).strip()
            else:
                sections[key] = None

        return sections

    async def extractFeatures(self, text):
        pattern = r'### (.*?)\n(.*?)(?=\n\n|\Z)'

        matches = re.findall(pattern, text, re.DOTALL)

        extractedFeatures = []

        for match in matches:
            title, content = match
            combinedFeatures = f"{title.strip()}: \n{content.strip()}"
            extractedFeatures.append(combinedFeatures)

        return extractedFeatures

    async def extractScore(self, score):
        extractedScores = []  # 점수와 상세 정보를 담을 리스트

        # 모든 섹션을 한 번에 추출
        pattern = r'### (?:보안|유지보수|전체):\n- \*\*점수\*\*: (\d+)점\n- \*\*상세 정보\*\*: (.*?)\n\n'
        matches = re.findall(pattern, score + '\n\n', re.DOTALL)

        for match in matches:
            extractedScores.append([int(match[0]), match[1].strip()])

        return extractedScores
