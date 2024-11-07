from s3_download.repository.s3_download_repository_impl import S3DownloadRepositoryImpl
from meeting_recording_summary.repository.meeting_recording_summary_repository_impl import MeetingRecordingSummaryRepositoryImpl
from meeting_recording_summary.service.meeting_recording_summary_service import MeetingRecordingSummaryService
from template.utility.color_print import ColorPrinter


class MeetingRecordingSummaryServiceImpl(MeetingRecordingSummaryService):
    __instance = None
    DOWNLOAD_PATH = "./meeting-recording-download"

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
            cls.__instance.__s3DownloadRepository  = S3DownloadRepositoryImpl.getInstance()
            cls.__instance.__meetingRecordingSummaryRepository = MeetingRecordingSummaryRepositoryImpl.getInstance()

        return cls.__instance

    @classmethod
    def getInstance(cls):
        if cls.__instance is None:
            cls.__instance = cls()

        return cls.__instance

    async def getSummary(self, *args, **kwargs):
        ColorPrinter.print_important_message(f"args: {args}")
        ColorPrinter.print_important_message(f"args[0]: {args[0]}")
        ColorPrinter.print_important_message(f"args[1]: {args[1]}")
        ColorPrinter.print_important_message(f"args[2]: {args[2]}")

        userToken = args[0]
        fileName = args[1]
        username = args[2]

        filePath = f"{self.DOWNLOAD_PATH}/{fileName}"
        await self.__s3DownloadRepository.downloadFile(fileName, filePath)
        text = await self.__meetingRecordingSummaryRepository.extractTextFromWebm(filePath)
        # summarizedText = await self.__meetingRecordingSummaryRepository.getSummarizedText(text)
        summarizedText = await self.__meetingRecordingSummaryRepository.get(text)

        return {"userToken": userToken, "message": summarizedText}

    async def getOpenAIWhisperSummary(self, *args, **kwargs):
        ColorPrinter.print_important_message("openaiWhisperSummary()")
        ColorPrinter.print_important_message(f"args: {args}")
        ColorPrinter.print_important_message(f"args[0]: {args[0]}")
        ColorPrinter.print_important_message(f"args[1]: {args[1]}")
        ColorPrinter.print_important_message(f"args[2]: {args[2]}")

        userToken = args[0]
        fileName = args[1]
        username = args[2]

        filePath = f"{self.DOWNLOAD_PATH}/{fileName}"
        await self.__s3DownloadRepository.downloadFile(fileName, filePath)
        text = await self.__meetingRecordingSummaryRepository.extractTextFromWebmUsingWhisper(filePath)
        summarizedText = await self.__meetingRecordingSummaryRepository.getSummaryFromTextUsingOpenAIAPI(text)

        return {"userToken": userToken, "message": summarizedText}
