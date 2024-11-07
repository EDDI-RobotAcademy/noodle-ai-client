from multiple_user_test_point.repository.multiple_user_test_point_repository_impl import \
    MultipleUserTestPointRepositoryImpl
from multiple_user_test_point.service.multiple_user_test_point_service import MultipleUserTestPointService
from template.utility.color_print import ColorPrinter


class MultipleUserTestPointServiceImpl(MultipleUserTestPointService):
    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
            cls.__instance.__multipleUserTestPointRepository = MultipleUserTestPointRepositoryImpl.getInstance()

        return cls.__instance

    @classmethod
    def getInstance(cls):
        if cls.__instance is None:
            cls.__instance = cls()

        return cls.__instance

    async def operateUserTestPoint(self, *args, **kwargs):
        ColorPrinter.print_important_data("args", args)
        userToken = args[0]

        await self.__multipleUserTestPointRepository.operate(*args, **kwargs)

        return {
            "userToken": userToken
        }
