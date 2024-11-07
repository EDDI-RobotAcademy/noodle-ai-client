import asyncio

from multiple_user_test_point.repository.multiple_user_test_point_repository import MultipleUserTestPointRepository
from template.utility.color_print import ColorPrinter


class MultipleUserTestPointRepositoryImpl(MultipleUserTestPointRepository):
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

        # 120초 동안 대기 (asyncio.sleep)
        await asyncio.sleep(120)

        ColorPrinter.print_important_data("Finish with userToken", userToken)
