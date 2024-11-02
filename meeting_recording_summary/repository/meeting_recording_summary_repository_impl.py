import asyncio

import nltk
from lightning_whisper_mlx import LightningWhisperMLX
from llama_cpp import Llama
from mlx_lm import load, generate
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

from meeting_recording_summary.repository.meeting_recording_summary_repository import MeetingRecordingSummaryRepository
from template.utility.color_print import ColorPrinter


class MeetingRecordingSummaryRepositoryImpl(MeetingRecordingSummaryRepository):
    __instance = None
    WHISPER_MODEL = LightningWhisperMLX(model="large-v3", batch_size=12, quant="8bit")
    LANGUAGE = "ko"
    # MODEL_NAME = 'eenzeenee/t5-base-korean-summarization'
    # SUMMARIZATION_MODEL = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)
    # SUMMARIZATION_TOKENIZER = AutoTokenizer.from_pretrained(MODEL_NAME)
    REPO_ID = "bartowski/Llama-3.2-1B-Instruct-GGUF"
    FILENAME = "Llama-3.2-1B-Instruct-Q4_K_M.gguf"
    SUMMARIZATION_MODEL = Llama.from_pretrained(
        repo_id=REPO_ID, filename=FILENAME, n_gpu_layers=-1, n_ctx=2048, flash_attn=True)

    model, tokenizer = load("mlx-community/gemma-2-2b-it-4bit")

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

    # async def getSummarizedText(self, text):
    #     inputText = f"summarize: \n{text}"
    #     ColorPrinter.print_important_message("Before SUMMARIZATION_TOKENIZER")
    #     inputs = self.SUMMARIZATION_TOKENIZER([inputText], max_length=2048, truncation=True, return_tensors="pt")
    #     ColorPrinter.print_important_message("After SUMMARIZATION_TOKENIZER")
    #     ColorPrinter.print_important_message("Before SUMMARIZATION_MODEL generate")
    #     output = self.SUMMARIZATION_MODEL.generate(**inputs, num_beams=3, do_sample=True, min_length=10, max_length=256)
    #     ColorPrinter.print_important_message("After SUMMARIZATION_MODEL generate")
    #     ColorPrinter.print_important_message("Before SUMMARIZATION_TOKENIZER batch_decode")
    #     decodedOutput = self.SUMMARIZATION_TOKENIZER.batch_decode(output, skip_special_tokens=True)[0]
    #     ColorPrinter.print_important_message("After SUMMARIZATION_TOKENIZER batch_decode")
    #     ColorPrinter.print_important_message("Before nltk sent_tokenize")
    #     result = nltk.sent_tokenize(decodedOutput.strip())[0]
    #     ColorPrinter.print_important_message("After nltk sent_tokenize")
    #
    #     print("getSummarizedText result:", result)
    #
    #     return result

    async def getSummarizedText(self, text):
        messages = [
            {
                "role": 'user',
                "content": f"다음 내용을 요약해주세요. 사용자의 요청에 맞는 대답인지 스스로 검증한 후, 필요한 대답만 해주세요.\n\n내용: {text}\n\n대답:"
            }
        ]
        summarizedText = self.SUMMARIZATION_MODEL.create_chat_completion(messages=messages)
        ColorPrinter.print_important_data("summarizedText:", summarizedText)

        return summarizedText['choices'][0]['message']['content']

    async def get(self, text):
        return generate(self.model, self.tokenizer,
                        prompt=f"다음 내용을 요약해주세요. 요약한 내용이 입력된 내용을 설명할 수 있는지 스스로 검증하고 대답하세요.\n"
                               f"**내용**: {text}\n\n**대답**:")
