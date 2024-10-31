import asyncio

import nltk
from lightning_whisper_mlx import LightningWhisperMLX
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

from meeting_recording_summary.repository.meeting_recording_summary_repository import MeetingRecordingSummaryRepository
from template.utility.color_print import ColorPrinter


class MeetingRecordingSummaryRepositoryImpl(MeetingRecordingSummaryRepository):
    __instance = None
    WHISPER_MODEL = LightningWhisperMLX(model="large-v3", batch_size=12, quant="8bit")
    LANGUAGE = "ko"
    MODEL_NAME = 'eenzeenee/t5-base-korean-summarization'
    SUMMARIZATION_MODEL = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)
    SUMMARIZATION_TOKENIZER = AutoTokenizer.from_pretrained(MODEL_NAME)

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)

        return cls.__instance

    @classmethod
    def getInstance(cls):
        if cls.__instance is None:
            cls.__instance = cls()

        return cls.__instance

    async def extractTextFromWebm(self, filePath):
        loop = asyncio.get_event_loop()

        result = await loop.run_in_executor(None, self.WHISPER_MODEL.transcribe, filePath, self.LANGUAGE)
        print("extractTextFromWebm Result:", result)

        return result['text']

