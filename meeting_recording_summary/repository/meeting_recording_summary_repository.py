from abc import abstractmethod, ABC

class MeetingRecordingSummaryRepository(ABC):
    @abstractmethod
    def extractTextFromWebm(self, filePath):
        pass

