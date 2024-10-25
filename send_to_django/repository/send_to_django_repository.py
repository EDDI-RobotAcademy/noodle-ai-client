from abc import ABC, abstractmethod

class SendToDjangoRepository(ABC):
    @abstractmethod
    def sendBacklogToDjango(self,ipcExecutorConditionalCustomExecutorChannel, userToken, backlogList):
        pass

