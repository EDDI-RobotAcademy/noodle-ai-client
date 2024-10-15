import os
import asyncio

from text_processing.repository.text_processing_repository_impl import TextProcessingRepositoryImpl

# 실제 경로 설정
GITHUB_REPO_PATH = '/home/eddi/dlls/noodle-ai-client/github_repositories/noodle-backend'

async def test_process_file():
    """process_file 메서드 테스트"""
    repo = TextProcessingRepositoryImpl.getInstance()

    # github repo 내의 실제 파일을 지정 (존재하는 파일이어야 함)
    file_path = os.path.join(GITHUB_REPO_PATH, 'account', 'controller', 'views.py')
    result = await repo.process_file(file_path)

    # 파일 내용이 예상되는 텍스트를 포함하는지 확인
    assert "checkUserNameDuplication" in result  # Method name
    assert "username" in result  # Variable used in the method
    assert "self.accountService.checkUsernameDuplication" in result  # Service call
    assert "Response" in result


async def test_async_os_walk():
    """async_os_walk 메서드 테스트"""
    repo = TextProcessingRepositoryImpl.getInstance()

    # 실제 GitHub 리포지토리 경로에서 os.walk가 정상 작동하는지 확인
    os_walk_result = await repo.async_os_walk(GITHUB_REPO_PATH)

    # 디렉토리 내 파일 또는 서브 디렉토리가 존재하는지 확인
    assert len(os_walk_result) > 0
    print("test_async_os_walk passed")


async def test_getTextFromSourceCode():
    """getTextFromSourceCode 메서드 테스트"""
    repo = TextProcessingRepositoryImpl.getInstance()

    # github repo 내에서 .py 파일들로부터 텍스트를 추출
    result = await repo.getTextFromSourceCode(GITHUB_REPO_PATH)

    # Check for specific content in views.py
    assert "def checkUserNameDuplication" in result
    assert "self.accountService.checkUsernameDuplication(username)" in result
    assert "Response" in result
    assert "isDuplicate" in result


async def main():
    """직접 실행하는 테스트 함수"""
    try:
        await test_process_file()
        await test_async_os_walk()
        await test_getTextFromSourceCode()
    except AssertionError as e:
        print(f"Test failed: {e}")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
