import os
import asyncio
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import patch, AsyncMock

import pytest

from text_processing.repository.text_processing_repository_impl import TextProcessingRepositoryImpl


class YourClass:
    def __init__(self, max_workers=6):
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=self.max_workers)

    async def getTextFromSourceCode(self, githubRepositoryPath):
        # Implementation of your async function
        # This is just a placeholder; replace it with your actual logic
        await asyncio.sleep(1)  # Simulating async work
        return f"Text from {githubRepositoryPath}"

    async def __executeAsyncFunction(self, userDefinedFunction, parameterList):
        return await userDefinedFunction(*parameterList)

    def generalThreadExecutionFunction(self, userDefinedFunction, parameterList):
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        if loop.is_running():
            print("loop is running")
            future = asyncio.ensure_future(self.__executeAsyncFunction(userDefinedFunction, parameterList))
            result = asyncio.get_event_loop().run_until_complete(future)
        else:
            print("loop isn't running")
            result = asyncio.run(self.__executeAsyncFunction(userDefinedFunction, parameterList))

        return result

    def executeInThreadPool(self, githubRepositoryPath):
        # Wrap your asynchronous function call in the executor
        futures = []
        repository = TextProcessingRepositoryImpl.getInstance()

        for _ in range(self.max_workers):
            # getTextFromSourceCode 메서드를 호출
            future = self.executor.submit(
                self.generalThreadExecutionFunction,
                repository.getTextFromSourceCode,
                [githubRepositoryPath]
            )
            futures.append(future)

            # Gather results
        results = [future.result() for future in futures]
        return results

# Usage example
@pytest.fixture
def your_class_instance():
    return YourClass(max_workers=6)

# @pytest.mark.asyncio
# async def test_execute_in_thread_pool(your_class_instance):
#     # Mock the getTextFromSourceCode method
#     with patch.object(your_class_instance, 'getTextFromSourceCode', new_callable=AsyncMock) as mock_get_text:
#         mock_get_text.side_effect = lambda path: f"Mocked text from {path}"
#
#         # Call the executeInThreadPool method
#         github_repo_path = '/mock/path/to/repo'
#         results = your_class_instance.executeInThreadPool(github_repo_path)
#
#         # Validate that the mocked method was called the expected number of times
#         assert mock_get_text.call_count == your_class_instance.max_workers
#
#         # Validate that the results are as expected
#         expected_results = [f"Mocked text from {github_repo_path}"] * your_class_instance.max_workers
#         assert results == expected_results
#
#         # Optionally, check if the function was called with the correct arguments
#         mock_get_text.assert_called_with(github_repo_path)


GITHUB_REPO_PATH = '/home/eddi/dlls/noodle-ai-client/github_repositories/noodle-backend'

@pytest.mark.asyncio
async def test_real_execute_in_thread_pool(your_class_instance):
    # Call the executeInThreadPool method with the real GitHub repository path
    results = your_class_instance.executeInThreadPool(GITHUB_REPO_PATH)

    # Validate that the results are as expected
    # Here you need to check the actual content extracted from the repository.
    # Adjust the expected_results based on the real content you expect.
    expected_substring = "def checkUserNameDuplication"  # Example expected content
    print(f"results: {results}")

    assert all(expected_substring in result for result in results), "Expected content not found in results"

    # Optionally, check that the number of results matches the number of workers
    assert len(results) == your_class_instance.max_workers, "Number of results does not match max workers"

# Run the tests using pytest
if __name__ == "__main__":
    pytest.main()
