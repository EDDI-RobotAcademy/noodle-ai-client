from abc import abstractmethod, ABC

class MeetingRecordingSummaryRepository(ABC):
    @abstractmethod
    def extractTextFromWebm(self, filePath):
        pass

    @abstractmethod
    def extractTextFromWebmUsingWhisper(self, filePath):
        pass

    # @abstractmethod
    # def getSummarizedText(self, text):
    #     pass

    @abstractmethod
    def get(self, text):
        pass

    @abstractmethod
    def getSummaryFromTextUsingOpenAIAPI(self, text):
        pass