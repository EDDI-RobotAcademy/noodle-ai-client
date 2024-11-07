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
            n_ctx=4000,
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

        # template = f"""
        # 당신은 애자일 프로젝트 관리자이자 기술 문서 작성 전문가입니다. 아래 제공되는 프로젝트 백로그 정보를 바탕으로 상세한 프로젝트 결과 보고서를 작성해주세요.
        #
        # **톤앤매너**
        #     - 전문적이고 객관적인 어조 유지
        #     - 기술적 내용과 비즈니스 가치를 균형있게 서술
        #
        # **보고서 양식**
        #     - 큰 제목에만 ## 사용
        #     - 작은 제목에는 ### 사용
        #     - 세부 사항은 - **세부 사항** 과 같은 양식 사용
        #
        # **백로그 항목**
        # {generatedBacklog}
        #
        # **요청 사항**\n
        # **다음 구조로 프로젝트 결과 보고서를 작성해주세요**:
        #
        # ## 프로젝트 제목
        #     - [여기에 프로젝트 제목을 작성하세요]
        #
        # ## 프로젝트 개요
        #     - [여기에 프로젝트 개요를 작성하세요]
        #
        # ## 기술 스택
        #     - 사용한 언어와 프레임워크를 나열해주세요
        #
        # ## 주요 기능
        # **다음 구조로 주요 기능을 작성해주세요**
        #
        # ## 앞에 넘버링을 붙이지 않고 백로그를 기반으로 한 주요 기능을 작성해주세요
        #     - 해당 기능의 세부 사항을 작성해주세요
        #
        # ## 활용 방안
        # **다음 구조로 활용 방안을 작성해주세요**
        #     - 활용 방안: 백로그를 기반으로 어떤 서비스에 사용할 수 있을지 예시를 작성해주세요
        #     - 상세 설명: 해당 예시에 대한 설명을 작성해주세요
        #
        # ## 보완할 점
        #     - 입력 값의 보강 사항을 바탕으로 작성해주세요
        #
        # ## 완성도
        # **다음 구조로 완성도를 작성해주세요**
        #     ## 보안:
        #     - **점수**: 입력 값의 보안 측면 점수를 숫자로만 작성해주세요
        #     - **상세 정보**: 입력 값의 보안 측면 점수의 상세 정보를 작성해주세요
        #     ## 유지보수:
        #     - **점수**: 입력 값의 코드 및 유지보수 측면 점수를 숫자로만 작성해주세요
        #     - **상세 정보**: 입력 값의 코드 및 유지보수 측면 점수의 상세 정보를 작성해주세요
        #     ## 전체
        #     - **점수**: 입력 값의 종합 점수를 숫자로만 작성해주세요
        #     - **상세 정보**: 입력 값의 종합 점수의 상세 정보를 작성해주세요"""

        template = f"""
        당신은 애자일 프로젝트 관리자이자 기술 문서 작성 전문가입니다. 아래 제공되는 프로젝트 백로그 정보를 바탕으로 상세한 프로젝트 결과 보고서를 작성해주세요.

        **톤앤매너**
            - 전문적이고 객관적인 어조 유지
            - 기술적 내용과 비즈니스 가치를 균형있게 서술

        **백로그 항목**
        {generatedBacklog}
        
         **요청 사항**\n
         **다음 구조로 프로젝트 결과 보고서를 작성해주세요**:

        ### 프로젝트 제목
            - [여기에 프로젝트 제목을 작성하세요]

        ### 프로젝트 개요
            - [여기에 프로젝트 개요를 작성하세요]

        ### 기술 스택
            - 사용한 언어와 프레임워크를 나열해주세요

        ### 주요 기능
        #### 주요 기능을 작성해주세요
            - **성공 기준**: 해당 기능의 성공 기준을 작성해주세요
            - **도메인 분리**: 해당 기능의 도메인을 작성해주세요
            - **작업 목록**: 해당 목록의 작업 목록을 작성해주세요
                - 작업 1
                - 작업 2
                - 작업 3

        ### 활용 방안
            - 프로젝트의 활용 방안을 작성해주세요
            
        ### 보완할 점
            - 입력 값의 보강 사항을 바탕으로 작성해주세요

        ### 완성도
        #### 보안: 입력 값의 보안 측면 점수를 숫자로만 작성해주세요
            - **상세 정보**: 입력 값의 보안 측면 점수의 상세 정보를 작성해주세요
        #### 유지보수: 입력 값의 코드 및 유지보수 측면 점수를 숫자로만 작성해주세요
            - **상세 정보**: 입력 값의 코드 및 유지보수 측면 점수의 상세 정보를 작성해주세요
        #### 전체: 입력 값의 종합 점수를 숫자로만 작성해주세요
            - **상세 정보**: 입력 값의 종합 점수의 상세 정보를 작성해주세요

        ### 요청 사항을 준수한 결과 보고서 출력 예시는 아래와 같습니다. ###
        
        <example>
        ### 프로젝트 제목
        - CNN및 residual network를 활용한 교통 표지판 분류 프로젝트 결과 보고서
        
        ### 프로젝트 개요
        - 이 프로젝트는 CNN과 ResNet을 활용한 인공 신경망을 기반으로 프레임 단위의 영상에서 추출한 표지판을 판별할 수 있는 모델의 학습 속도를 단축하는 것을 목표로 한다
        
        ### 기술 스택
        - **언어**: Python
        - **프레임워크**: Tensorflow, Keras
        
        ### 주요 기능
        #### 교통 표지판 데이터 전처리
        - **성공 기준**: 표지판 데이터를 학습 가능한 형식으로 변환하고 노이즈 및 왜곡을 제거하여 정확한 분류 가능
        - **도메인 분리**: 데이터 수집 및 정리, 리사이징, 정규화
        - **작업 목록**: 
            - 이미지 데이터 수집
            - 이미지 전처리
            - 데이터 증강
            
        #### CNN기반 특징 추출
        - **성공 기준**: 입력된 교통 표지판 이미지에서 주요 특징을 자동으로 추출하여 정확한 분류 기반 제공
        - **도메인 분리**: 필터, pooling layer, activation function
        - **작업 목록**:
            - CNN 네트워크 설계
            - 활성화 함수 및 풀링 기법 적용
            - 이미지 특징 맵 추출
            
        #### Residual Network 적용
        - **성공 기준**: 깊은 신경망에서의 학습 성능 저하 방지 및 정확도 향상
        - **도메인 분리**: ResNet블록 설계, skip connection 적용
        - **작업 목록**:
            - ResNet 블록 설계 및 구현
            - skip connection 추가
            - CNN과 ResNet 통합
            
        #### 모델 학습 및 검증
        - **성공 기준**: 학습된 모델이 검증 데이터에서 높은 정확도를 기록
        - **도메인 분리**: 모델 학습, 검증, 과적합 방지
        - **작업 목록**: 
            - 학습 데이터 및 검증 데이터 분리
            - 모델 훈련 및 검증
            - 과적합 방지 기법 적용
        
        ### 활용 방안
        - 운전 보조 시스템에 적용하여 운전자가 놓칠 수 있는 표지판을 자동으로 인식하고 경고하는 기능에 활용될 수 있음
        
        ### 보완할 점
        - 데이터의 다양성 부족: 표지판 데이터가 제한되어있으므로, 데이터를 추가하여 범용성을 향상시킬 필요가 있음
        - 복합 표지판 처리: 여러 표지판이 같이 나타나는 다중 표지판의 경우도 정확도의 개선이 필요함
        
        ### 완성도
        #### 보안: 60
        - 모델의 학습 및 검증 과정에서 데이터 유출 방지를 위한 보안 대책 수립 필요
        
        #### 유지보수: 85
        - 주석 작성으로 유지보수성을 높였으며, 향후 기능 추가 및 성능 최적화를 쉽게 적용 가능
        - 데이터 업데이트 시 새로운 표지판 유형에 대한 모델 학습이 간편하게 이루어지도록 설계됨
        
        #### 전체: 70
        - 모델은 성공적으로 교통 표지판 분류를 수행하고, 실시간으로 교통 표지판을 인식하는 데, 적합한 기능을 구현하였음
        - 데이터 다양성 및 실시간 성능 최적화에 대한 개선이 필요하지만, 기본 기능은 만족할 만한 수준으로 구현되었음
        </example>
        
        **입력 값을 반환하기 전에 스스로 한번 더 검증하세요**
        """

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
