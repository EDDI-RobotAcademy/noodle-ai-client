import asyncio
import concurrent.futures
import os
import re
from asyncio import as_completed
from concurrent.futures.thread import ThreadPoolExecutor

import aiofiles
from PIL.ImageEnhance import Color

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
        ColorPrinter.print_important_message("1")
        lines = text.split('\n')

        sections = {}
        currentTitle = None
        currentContent = []
        ColorPrinter.print_important_message("2")
        for line in lines:
            title_match = re.match(r'^#\s+([^#].+)$', line)

            if title_match:
                if currentTitle:
                    sections[currentTitle] = '\n'.join(currentContent).strip()

                currentTitle = title_match.group(1)
                currentContent = []
            else:
                if currentTitle and line.strip():
                    currentContent.append(line)
        ColorPrinter.print_important_message("3")
        if currentTitle:
            sections[currentTitle] = '\n'.join(currentContent).strip()
        ColorPrinter.print_important_message("4")
        return sections

    async def extractSubsections(self, text):
        lines = await text.split('\n')

        sections = {}
        currentTitle = None
        currentContent = []

        for line in lines:
            title_match = re.match(r'^##\s+(.+)$', line)

            if title_match:
                if currentTitle:
                    sections[currentTitle] = '\n'.join(currentContent).strip()

                currentTitle = await title_match.group(1)
                currentContent = []
            else:
                if currentTitle:
                    currentContent.append(line)

        if currentTitle:
            sections[currentTitle] = '\n'.join(currentContent).strip()

        return sections

    async def extractScore(self, score):
        pattern = r'-\s*([^:]+):\s*(\d+)점'
        match = re.search(pattern, score)

        category = match.group(1).strip()
        intScore = int(match.group(2))

        details = []
        for line in await score.split("\n"):
            detailsMatch = re.match(r'\s*-\s*(.+)', line)
            if detailsMatch and not await line.strip().endswith('점'):
                details.append(detailsMatch.group(1).strip())

        return category, intScore, details
