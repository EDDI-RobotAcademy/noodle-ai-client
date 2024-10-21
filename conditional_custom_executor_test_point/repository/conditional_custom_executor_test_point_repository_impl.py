import asyncio

from conditional_custom_executor_test_point.repository.conditional_custom_executor_test_point_repository import \
    ConditionalCustomExecutorTestPointRepository
from template.utility.color_print import ColorPrinter


class ConditionalCustomExecutorTestPointRepositoryImpl(ConditionalCustomExecutorTestPointRepository):
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

    async def operate(self, *args, **kwargs):
        userToken = args[0]

        ColorPrinter.print_important_data("Start with userToken", userToken)

        for i in range(7):


        ColorPrinter.print_important_data("Finish with userToken", userToken)

        return userToken
