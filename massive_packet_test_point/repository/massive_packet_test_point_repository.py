from abc import ABC, abstractmethod


class MassivePacketTestPointRepository(ABC):
    @abstractmethod
    def operate(self, *args, **kwargs):
        pass
