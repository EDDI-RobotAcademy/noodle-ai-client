import asyncio
import json

from conditional_custom_executor_multiple_user_test.repository.conditional_custom_executor_multiple_user_test_repository import \
    ConditionalCustomExecutorMultipleUserTestRepository

from template.utility.color_print import ColorPrinter
from user_defined_protocol.protocol import UserDefinedProtocolNumber


class ConditionalCustomExecutorMultipleUserTestRepositoryImpl(ConditionalCustomExecutorMultipleUserTestRepository):
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
        ColorPrinter.print_important_message(f"Start Conditional Custom Executor operate() -> args: {args}, kwargs: {kwargs}")

        userToken = args[1]
        ipcExecutorConditionalCustomExecutorChannel = args[0]
        
        willBeSendToBackend = json.dumps([1, 2, 3])

        await asyncio.sleep(10)

        try:
            ipcExecutorConditionalCustomExecutorChannel.put(
                (
                    UserDefinedProtocolNumber.CONDITIONAL_CUSTOM_EXECUTOR_MULTIPLE_USER_TEST,
                    {
                        "userToken": userToken,
                        "willBeSendToBackend": willBeSendToBackend,
                        "tag": "conditional-custom-executor-test"
                    }
                )
            )

            ColorPrinter.print_important_message("Finish Conditional Custom Executor operate()")

        except Exception as e:
            ColorPrinter.print_important_message(f"Error occur while sending data to Django: {e}!")

        return userToken
