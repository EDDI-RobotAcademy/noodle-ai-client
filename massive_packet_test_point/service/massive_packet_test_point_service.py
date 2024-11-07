from abc import ABC, abstractmethod


class MassivePacketTestPointService(ABC):
    @abstractmethod
    def operateMassivePacketTestPoint(self, *args, **kwargs):
        pass
