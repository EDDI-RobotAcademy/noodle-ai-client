import asyncio
import concurrent.futures

from llama_cpp import Llama
from transformers import AutoTokenizer

from generate_result_report.repository.generate_result_report_repository import GenerateResultReportRepository
from template.utility.color_print import ColorPrinter


class GenerateResultReportRepositoryImpl(GenerateResultReportRepository):
    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)

        return cls.__instance

    @classmethod
    def getInstance(cls):
        if cls.__instance is None:
            cls.__instance = cls()

        return cls.__instance

    def modelCall(self, llm, prompt, max_tokens, stop, top_p, temperature, echo):
        result = llm(prompt, max_tokens=max_tokens, stop=stop, top_p=top_p, temperature=temperature, echo=echo)
        return result

    async def generate(self, generatedBacklog):
        model_id = 'MLP-KTLim/llama-3-Korean-Bllossom-8B-gguf-Q4_K_M'
        ColorPrinter.print_important_message("Before load tokenizer")
        tokenizer = AutoTokenizer.from_pretrained(model_id)
        ColorPrinter.print_important_message("After load tokenizer")

        ColorPrinter.print_important_message("Before load llm")
        llm = Llama.from_pretrained(
            repo_id=model_id,
            filename="llama-3-Korean-Bllossom-8B-Q4_K_M.gguf",
            n_gpu_layers=-1,
            n_ctx=3000,
            flash_attn=True,
            seed=1
        )
        ColorPrinter.print_important_message("After load llm")

        generation_kwargs = {
            "max_tokens": 1200,
            "stop": ["<|eot_id|>"],
            "top_p": 0.01,
            "top_k": 1,
            "temperature": 0.0,
            "echo": False
        }

        template = f"""
        당신은 애자일 프로젝트 관리자이자 기술 문서 작성 전문가입니다. 아래 제공되는 프로젝트 백로그 정보를 바탕으로 상세한 프로젝트 결과 보고서를 작성해주세요.

        **톤앤매너**
            - 전문적이고 객관적인 어조 유지
            - 기술적 내용과 비즈니스 가치를 균형있게 서술
        
        **보고서 양식**
            - 큰 제목에만 ## 사용
            - 작은 제목에는 ### 사용
            - 세부 사항은 - **세부 사항** 과 같은 양식 사용

        **백로그 항목**
        {generatedBacklog}

        **요청 사항**\n
        **다음 구조로 프로젝트 결과 보고서를 작성해주세요**:

        ## 프로젝트 제목
            - [여기에 프로젝트 제목을 작성하세요]

        ## 프로젝트 개요
            - [여기에 프로젝트 개요를 작성하세요]

        ## 기술 스택
            - 사용한 언어와 프레임워크를 나열해주세요

        ## 주요 기능
        **다음 구조로 주요 기능을 작성해주세요**
        
        ## 앞에 넘버링을 붙이지 않고 백로그를 기반으로 한 주요 기능을 작성해주세요
            - 해당 기능의 세부 사항을 작성해주세요 

        ## 활용 방안
        **다음 구조로 활용 방안을 작성해주세요**
            - 활용 방안: 백로그를 기반으로 어떤 서비스에 사용할 수 있을지 예시를 작성해주세요
            - 상세 설명: 해당 예시에 대한 설명을 작성해주세요

        ## 보완할 점
            - 입력 값의 보강 사항을 바탕으로 작성해주세요

        ## 완성도
        **다음 구조로 완성도를 작성해주세요**
            ## 보안: 
            - **점수**: 입력 값의 보안 측면 점수를 숫자로만 작성해주세요
            - **상세 정보**: 입력 값의 보안 측면 점수의 상세 정보를 작성해주세요
            ## 유지보수: 
            - **점수**: 입력 값의 코드 및 유지보수 측면 점수를 숫자로만 작성해주세요
            - **상세 정보**: 입력 값의 코드 및 유지보수 측면 점수의 상세 정보를 작성해주세요
            ## 전체
            - **점수**: 입력 값의 종합 점수를 숫자로만 작성해주세요
            - **상세 정보**: 입력 값의 종합 점수의 상세 정보를 작성해주세요"""

        PROMPT = \
            '''당신은 유용한 AI 어시스턴트입니다. 사용자의 질의에 대해 한국어로 친절하고 정확하게 답변해야 합니다.
            You are a useful AI assistant. You should answer your questions kindly and accurately in Korean.'''

        messages = [
            {"role": "system", "content": f"{PROMPT}"},
            {"role": "user", "content": f"{template}"}
        ]

        ColorPrinter.print_important_message("Before apply chat template to tokenizer")
        prompt = tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )
        ColorPrinter.print_important_message("After apply chat template to tokenizer")

        loop = asyncio.get_running_loop()
        ColorPrinter.print_important_message("Before inference!")
        with concurrent.futures.ThreadPoolExecutor() as pool:
            response_msg = await loop.run_in_executor(
                pool,
                self.modelCall,
                llm,
                prompt,
                generation_kwargs["max_tokens"],
                generation_kwargs["stop"],
                generation_kwargs["top_p"],
                generation_kwargs["temperature"],
                generation_kwargs["echo"]
            )
            ColorPrinter.print_important_message("After inference")

        response_text = response_msg['choices'][0]['text']

        return response_text
