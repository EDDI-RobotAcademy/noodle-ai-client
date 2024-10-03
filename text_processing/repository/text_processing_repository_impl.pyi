import re

from text_processing.repository.text_processing_repository import TextProcessingRepository


class TextProcessingRepositoryImpl(TextProcessingRepository):
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

    def postprocessingTextToBacklogs(self, generatedBacklogsText):
        # 정규표현식으로 매칭
        titlePattern = re.compile(r"백로그 제목:\s*(.+)")
        domainPattern = re.compile(r"도메인 이름:\s*(.+)")
        successCriteriaPattern = re.compile(r"Success Criteria:\s*(.+)")
        todoPattern = re.compile(r"To-do:\s*(- .+)", re.DOTALL)

        # 각 백로그는 \n\n으로 구분됨
        backlogItems = generatedBacklogsText.strip().split("\n\n")

        parsedItems = []

        for item in backlogItems:
            titleMatch = titlePattern.search(item)
            domainMatch = domainPattern.search(item)
            successCriteriaMatch = successCriteriaPattern.search(item)
            todoMatch = todoPattern.search(item)

            if titleMatch and domainMatch and successCriteriaMatch and todoMatch:
                title = titleMatch.group(1).strip()
                domain = domainMatch.group(1).strip()
                successCriteria = successCriteriaMatch.group(1).strip()
                # To-do 는 '- ' 으로 시작함
                todos = re.findall(r"- [^\n]+", todoMatch.group(1))

                parsedItems.append({
                    "backlogName": title,
                    "domainName": domain,
                    "successCriteria": successCriteria,
                    "todo": todos
                })

        return parsedItems
