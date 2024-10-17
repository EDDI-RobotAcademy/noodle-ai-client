import concurrent.futures
import asyncio
import random
import time
import os
import aiofiles
from queue import Queue


class ColorPrinter:
    @staticmethod
    def print_important_message(message):
        print(f"IMPORTANT: {message}")

    @staticmethod
    def print_important_data(message, data):
        print(f"IMPORTANT: {message} -> {data}")


class TextProcessingRepository:
    async def process_file(self, filePath):
        async with aiofiles.open(filePath, mode='r', encoding='utf-8') as f:
            content = await f.read()
            if len(content) < 512:
                return ""
        return f"File: {filePath}\n{content}\n"

    async def async_os_walk(self, path):
        ColorPrinter.print_important_message("async_os_walk()")
        try:
            files = await asyncio.to_thread(lambda: list(os.walk(path)))
            return files
        except Exception as e:
            ColorPrinter.print_important_message(f"Error during os.walk: {e}")
            return []

    async def getTextFromSourceCode(self, githubRepositoryPath):
        ColorPrinter.print_important_data("getTextFromSourceCode()", githubRepositoryPath)
        text = ""

        tasks = []
        osPath = await self.async_os_walk(githubRepositoryPath)
        ColorPrinter.print_important_data("getTextFromSourceCode() osPath", osPath)
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


class GroupBService:
    def __init__(self):
        self.__textProcessingRepository = TextProcessingRepository()

    async def generateResultReport(self, userName, githubRepositoryName, githubBranchName):
        ColorPrinter.print_important_message(f"service -> generate() userName: {userName}")
        ColorPrinter.print_important_message(f"service -> generate() githubRepositoryName: {githubRepositoryName}")
        ColorPrinter.print_important_message(f"service -> generate() githubBranchName: {githubBranchName}")

        # Simulate clone repository process
        githubRepositoryPath = f"./github_repositories/{githubRepositoryName}"
        ColorPrinter.print_important_message("After clone the repository.")

        # Get text from the source code
        textFromSourceCode = await self.__textProcessingRepository.getTextFromSourceCode(githubRepositoryPath)
        ColorPrinter.print_important_message("After get text from the source code.")
        return textFromSourceCode


def group_a_receiver(queue_a_to_b, thread_id):
    for _ in range(3):
        number = random.choice([1])  # Only task 1 is defined
        data = (number, f"user{thread_id}", "sample_repo", "main_branch")  # Dummy data
        print(f"Group A (Thread {thread_id}) received task number: {number} with data: {data}")
        queue_a_to_b.put(data)  # Send task number and data to Group B
        time.sleep(random.uniform(0.1, 1))


class GroupBServiceWrapper:
    def __init__(self, customProtocolRepository):
        self.__customProtocolRepository = customProtocolRepository
        self.__textProcessingRepository = TextProcessingRepository()

    async def execute(self, number):
        userDefinedFunction, parameterList = self.getFunctionByNumber(number)
        result = await self.__executeAsyncFunction(userDefinedFunction, parameterList)
        return result

    async def __executeAsyncFunction(self, userDefinedFunction, parameterList):
        return await userDefinedFunction(*parameterList)

    def getFunctionByNumber(self, number):
        if number == 1:
            userName = "EDDI-RobotAcademy"
            githubRepo = "noodle-backend"
            branch = "develop"
            return self.generateResultReport, [userName, githubRepo, branch]

    async def generateResultReport(self, *args):
        userName = args[0]
        githubRepositoryName = args[1]
        githubBranchName = args[2]

        ColorPrinter.print_important_message(f"service -> generate() userName: {userName}")
        ColorPrinter.print_important_message(f"service -> generate() githubRepositoryName: {githubRepositoryName}")
        ColorPrinter.print_important_message(f"service -> generate() githubBranchName: {githubBranchName}")

        githubRepositoryPath = f"./github_repositories/{githubRepositoryName}"
        textFromSourceCode = await self.__textProcessingRepository.getTextFromSourceCode(githubRepositoryPath)
        return textFromSourceCode


async def group_b_executor(queue_a_to_b, queue_b_to_c, thread_id, customProtocolRepository):
    service = GroupBServiceWrapper(customProtocolRepository)

    while True:
        if not queue_a_to_b.empty():
            number, *data = queue_a_to_b.get()
            print(f"Group B (Thread {thread_id}) received task number: {number}, data: {data}")
            try:
                result = await service.execute(number)
                print(f"Group B (Thread {thread_id}) executed")
                queue_b_to_c.put(result)
            except Exception as e:
                print(f"Group B (Thread {thread_id}) encountered an error: {e}")

        await asyncio.sleep(random.uniform(0.1, 1))


def group_c_transmitter(queue_b_to_c, thread_id):
    while True:
        if not queue_b_to_c.empty():
            data = queue_b_to_c.get()
            print(f"Group C (Thread {thread_id}) transmitting")
        time.sleep(random.uniform(0.1, 1))


async def main():
    queue_a_to_b = Queue()
    queue_b_to_c = Queue()

    customProtocolRepository = 1

    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor_a, \
            concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor_b, \
            concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor_c:

        # Group A (Receiver)
        for i in range(3):
            executor_a.submit(group_a_receiver, queue_a_to_b, i)

        # Group B (Executor with async tasks)
        loop = asyncio.get_running_loop()
        for i in range(3):
            asyncio.create_task(group_b_executor(queue_a_to_b, queue_b_to_c, i, customProtocolRepository))

        # Group C (Transmitter)
        for i in range(3):
            executor_c.submit(group_c_transmitter, queue_b_to_c, i)

        try:
            while True:
                await asyncio.sleep(0.1)
        except KeyboardInterrupt:
            print("Shutting down...")

if __name__ == "__main__":
    asyncio.run(main())
