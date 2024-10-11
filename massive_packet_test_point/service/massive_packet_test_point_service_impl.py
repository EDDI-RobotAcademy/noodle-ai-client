from massive_packet_test_point.repository.massive_packet_test_point_repository_impl import \
    MassivePacketTestPointRepositoryImpl
from massive_packet_test_point.service.massive_packet_test_point_service import MassivePacketTestPointService
from template.utility.color_print import ColorPrinter


class MassivePacketTestPointServiceImpl(MassivePacketTestPointService):
    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
            cls.__instance.__massivePacketTestPointRepository = MassivePacketTestPointRepositoryImpl.getInstance()

        return cls.__instance

    @classmethod
    def getInstance(cls):
        if cls.__instance is None:
            cls.__instance = cls()

        return cls.__instance

    async def operateMassivePacketTestPoint(self, *args, **kwargs):
        ColorPrinter.print_important_data("args", args)
        userToken = args[0]

        await self.__massivePacketTestPointRepository.operate(*args, **kwargs)

        return {
            "userToken": userToken
        }
