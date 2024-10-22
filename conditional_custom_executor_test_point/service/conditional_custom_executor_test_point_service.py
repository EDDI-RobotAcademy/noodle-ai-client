from abc import ABC, abstractmethod


class ConditionalCustomExecutorTestPointService(ABC):
    @abstractmethod
    def operateConditionalCustomExecutorTestPoint(self, *args, **kwargs):
        pass
