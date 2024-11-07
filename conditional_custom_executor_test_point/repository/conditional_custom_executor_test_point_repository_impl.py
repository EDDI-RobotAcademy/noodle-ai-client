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
        ColorPrinter.print_important_message(f"operate() -> args: {args}, kwargs: {kwargs}")

        userToken = args[0]
        ipcExecutorConditionalCustomExecutorChannel = args[1]

        intermediate_data_list = kwargs['intermediateData']

        ColorPrinter.print_important_message(f"Start Conditional Custom Executor operate() -> userToken: {userToken}")
        ColorPrinter.print_important_message(f"Start Conditional Custom Executor operate() -> intermediate_data_list: {intermediate_data_list}")

        try:
            ipcExecutorConditionalCustomExecutorChannel.put(
                (
                    30,
                    {
                        "userToken": "test",
                        "intermediateData": intermediate_data_list,
                        "tag": "conditional-custom-executor"
                    }
                )
            )

            ColorPrinter.print_important_message("Finish Conditional Custom Executor operate()")

        except Exception as e:
            ColorPrinter.print_important_message(f"Error occur while sending data to Django: {e}!")

        return userToken
