from abc import ABC, abstractmethod


class MultipleUserTestPointService(ABC):
    @abstractmethod
    def operateUserTestPoint(self, *args, **kwargs):
        pass
