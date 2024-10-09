from abc import ABC, abstractmethod


class MultipleUserTestPointRepository(ABC):
    @abstractmethod
    def operate(self, *args, **kwargs):
        pass
