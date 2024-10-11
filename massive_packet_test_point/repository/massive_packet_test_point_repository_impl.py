import asyncio

from massive_packet_test_point.repository.massive_packet_test_point_repository import MassivePacketTestPointRepository
from template.utility.color_print import ColorPrinter


class MassivePacketTestPointRepositoryImpl(MassivePacketTestPointRepository):
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
        data = args[1]

        ColorPrinter.print_important_data("massive packet test start", userToken)

        if not all(char in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ' for char in data):
            ColorPrinter.print_important_data("Error: Data contains invalid characters", userToken)
            return

        expected_length = 26 * 628
        if len(data) != expected_length:
            ColorPrinter.print_important_data(f"Error: Data length is {len(data)}, expected {expected_length}",
                                              userToken)
            return

        for i in range(628):
            segment = data[i * 26:(i + 1) * 26]
            if segment != 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
                ColorPrinter.print_important_data(f"Error: Segment {i + 1} is not valid: {segment}", userToken)
                return

        ColorPrinter.print_important_data("massive packet test finish", userToken)
