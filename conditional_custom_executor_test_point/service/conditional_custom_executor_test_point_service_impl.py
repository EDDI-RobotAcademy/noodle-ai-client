from conditional_custom_executor_test_point.repository.conditional_custom_executor_test_point_repository_impl import \
    ConditionalCustomExecutorTestPointRepositoryImpl
from multiple_user_test_point.service.multiple_user_test_point_service import MultipleUserTestPointService
from template.utility.color_print import ColorPrinter


class ConditionalCustomExecutorTestPointServiceImpl(MultipleUserTestPointService):
    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
            cls.__instance.__conditionalCustomExecutorTestPointRepository = ConditionalCustomExecutorTestPointRepositoryImpl.getInstance()

        return cls.__instance

    @classmethod
    def getInstance(cls):
        if cls.__instance is None:
            cls.__instance = cls()

        return cls.__instance

    async def operateConditionalCustomExecutorTestPoint(self, *args, **kwargs):
        ColorPrinter.print_important_data("operateConditionalCustomExecutorTestPoint", args)

        userToken = await self.__conditionalCustomExecutorTestPointRepository.operate(*args, **kwargs)

        return {
            "userToken": userToken
        }
