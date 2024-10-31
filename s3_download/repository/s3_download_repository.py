from abc import abstractmethod, ABC


class S3DownloadRepository(ABC):
    @abstractmethod
    def downloadFile(self, fileName, filePath):
        pass