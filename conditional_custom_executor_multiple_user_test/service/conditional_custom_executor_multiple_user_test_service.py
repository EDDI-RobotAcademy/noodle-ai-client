from abc import ABC, abstractmethod


class ConditionalCustomExecutorMultipleUserTestService(ABC):
    @abstractmethod
    def operateConditionalCustomExecutorMultipleUserTest(self, *args, **kwargs):
        pass
