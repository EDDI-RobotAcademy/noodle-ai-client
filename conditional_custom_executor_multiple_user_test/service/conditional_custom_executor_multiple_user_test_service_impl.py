from conditional_custom_executor_multiple_user_test.repository.conditional_custom_executor_multiple_user_test_repository_impl import \
    ConditionalCustomExecutorMultipleUserTestRepositoryImpl
from conditional_custom_executor_multiple_user_test.service.conditional_custom_executor_multiple_user_test_service import \
    ConditionalCustomExecutorMultipleUserTestService


from template.utility.color_print import ColorPrinter


class ConditionalCustomExecutorMultipleUserTestServiceImpl(ConditionalCustomExecutorMultipleUserTestService):
    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
            cls.__instance.__conditionalCustomExecutorMultipleUserTestRepository = ConditionalCustomExecutorMultipleUserTestRepositoryImpl.getInstance()

        return cls.__instance

    @classmethod
    def getInstance(cls):
        if cls.__instance is None:
            cls.__instance = cls()

        return cls.__instance

    async def operateConditionalCustomExecutorMultipleUserTest(self, *args, ipcExecutorConditionalCustomExecutorChannel=None, **kwargs):
        ColorPrinter.print_important_data("operateConditionalCustomExecutorTestPoint", args)

        sendSuccess = await self.__conditionalCustomExecutorMultipleUserTestRepository.operate(
            *args,
            ipcExecutorConditionalCustomExecutorChannel,
            **kwargs)

        return {
            "isComplete": sendSuccess
        }
