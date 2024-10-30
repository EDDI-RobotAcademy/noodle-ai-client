from abc import ABC, abstractmethod


class ConditionalCustomExecutorMultipleUserTestRepository(ABC):
    @abstractmethod
    def operate(self, *args, ipcExecutorConditionalCustomExecutorChannel=None, **kwargs):
        pass
