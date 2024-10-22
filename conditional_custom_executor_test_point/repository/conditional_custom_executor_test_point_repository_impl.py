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

    async def operate(self, *args, ipcExecutorConditionalCustomExecutorChannel=None, **kwargs):
        ipcExecutorConditionalCustomExecutorChannel = args[0]
        userToken = args[1]
        ColorPrinter.print_important_message(f"Start Conditional Custom Executor operate() -> userToken: {userToken}")

        intermediate_data_list = [{"intermediateData": i} for i in range(7)]

        ipcExecutorConditionalCustomExecutorChannel.put(
            (
                12322,
                {
                    "userToken": "test",
                    "intermediateData": intermediate_data_list,
                    "tag": "conditional-custom-executor"
                }
            )
        )

        ColorPrinter.print_important_message("Finish Conditional Custom Executor operate()")

        return userToken
