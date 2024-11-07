# import os
#
# import openai
# from dotenv import load_dotenv
#
# load_dotenv()
# client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
#
# text = ""
# with open("code.txt", "r") as f:
#     text += f.read()
#
# def generateBacklogByOpenAI(textFromSourceCode):
#     systemPrompt = \
#         '''당신은 유용한 AI 어시스턴트입니다. 사용자의 질의에 대해 한국어로 친절하고 정확하게 답변해야 합니다.
#         You are a helpful AI assistant, You should answer your questions kindly and accurately in Korean.'''
#
#     userPrompt = (
#         "You are generating an Agile backlog from the following source code. "
#         "Each backlog item should include a title, success criteria, domain separation, and task list."
#         "Additionally, please make a list of the language and frameworks based on the source code."
#         "Lastly, if there is anything more to supplement among the code contents, please write it down."
#         "If the most perfect code is 100 points, please decide what the source code below is and write it.\n\n"
#         f"Source code:\n{textFromSourceCode}\n"
#
#         "Answer:"
#         "Languages: (Used programming languages in source code)"
#         "Frameworks: (Used frameworks in source code)"
#         "Supplements: (Supplements you judged)"
#         "Scores of source code: "
#         "   - Security Aspect: (Integer score you judged)"
#         "   - Code Structure and Maintainability Aspect: (Integer score you judged)"
#         "   - Overall score: (Integer score you judged)"
#     )
#
#     messages = [
#         {
#             "role": "system", "content": systemPrompt,
#         },
#         {
#             "role": "user", "content": userPrompt
#         }
#     ]
#
#     response = client.chat.completions.create(
#         model="gpt-4o-mini",
#         messages=messages,
#         temperature=0.0,
#         max_tokens=1500,
#         top_p=0.01,
#         seed=1
#     )
#
#     return response.choices[0].message.content
#
# generatedBacklogs = generateBacklogByOpenAI(text)
#
# with open("backlogs.txt", "w") as f:
#     f.writelines(generatedBacklogs)
#
import os

from langchain_core.runnables import RunnablePassthrough

os.environ["KMP_DUPLICATE_LIB_OK"]='True'

from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate, BaseChatPromptTemplate
from langchain_huggingface import HuggingFaceEndpointEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from llama_cpp import Llama
from transformers import AutoTokenizer

model_id = 'MLP-KTLim/llama-3-Korean-Bllossom-8B-gguf-Q4_K_M'

tokenizer = AutoTokenizer.from_pretrained(model_id)

llm = Llama.from_pretrained(
    repo_id=model_id,
    filename="llama-3-Korean-Bllossom-8B-Q4_K_M.gguf",
    n_gpu_layers=-1,
    n_ctx=4500,
    flash_attn=True,
    seed=1)

generation_kwargs = {
    "max_tokens": 1000,
    "stop": ["<|eot_id|>"],
    "top_p": 0.01,
    "top_k": 1,
    "temperature": 0.0,
    "echo": False
}

text = ""
with open('backlogs.txt', "r") as f:
    text += f.read()

splitter = RecursiveCharacterTextSplitter(chunk_size=512, chunk_overlap=16)
chunkList = splitter.split_text(text)
documentList = [Document(page_content=chunk) for chunk in chunkList]

load_dotenv()
hf_embeddings = HuggingFaceEndpointEmbeddings(
    model="intfloat/multilingual-e5-large-instruct",
    task="feature-extraction",
    huggingfacehub_api_token=os.getenv("HUGGINGFACE_API_KEY")
)

vectorstore = FAISS.from_documents(documentList, hf_embeddings)
retriever = vectorstore.as_retriever(k=20)

def format_docs(docs):
    return "\n\n".join([doc.page_content for doc in docs])

questionList = [
    "이 프로젝트의 기술 스택 목록을 작성해줘."
]

PROMPT = \
            '''당신은 유용한 AI 어시스턴트입니다. 사용자의 질의에 대해 한국어로 친절하고 정확하게 답변해야 합니다.
            You are a useful AI assistant. You should answer your questions kindly and accurately in Korean.'''

question = "프로젝트의 내용을 기반으로, 사업성을 평가해주세요."

context = format_docs(retriever.invoke(question))
print(context)
print("\n\n")
template = f"""
        당신은 소프트웨어 개발 프로젝트의 사업성을 평가하는 전문가입니다. 
        **제공된 애자일 백로그를 바탕으로 프로젝트의 사업성을 분석해주세요.**
        
        다음은 백로그 분석의 예시입니다:
        
        입력 예시:
        <example>
        ### Agile Backlog
        
        #### 1. **Title**: User Authentication System
           - **Success Criteria**: Users can securely sign up, log in, and manage their accounts.
           - **Domain Separation**: Authentication and user management.
           - **Task List**:
             - Implement user registration
             - Create login functionality
             - Develop password reset feature
        
        #### 2. **Title**: Product Catalog
           - **Success Criteria**: A searchable, filterable catalog of products is available to users.
           - **Domain Separation**: Product management and display.
           - **Task List**:
             - Design database schema for products
             - Implement search and filter functionality
             - Create product detail pages
        
        ### Languages and Frameworks
        - **Languages**: JavaScript
        - **Frameworks**: React, Node.js, Express
        
        ### Supplements
        - **Security**: Implement proper authentication and authorization mechanisms.
        - **Error Handling**: Provide clear error messages to users and log errors for debugging.
        - **Testing**: Conduct unit and integration tests for all major features.
        
        ### Scores of Source Code
        - **Security Aspect**: 85
        - **Code Structure and Maintainability Aspect**: 80
        - **Overall Score**: 82
        </example>
        
        출력 예시:
        <example>
        1. 기술적 실현 가능성: 8/10
           추론 과정:
           a) 기술 스택 평가: React, Node.js, Express는 현재 업계에서 널리 사용되는 기술입니다. 이는 안정성과 커뮤니티 지원을 의미합니다.
           b) 기능 복잡도 분석: 사용자 인증과 제품 카탈로그는 웹 애플리케이션의 기본적인 기능입니다. 복잡도가 높지 않아 구현이 상대적으로 용이할 것입니다.
           c) 아키텍처 검토: 백로그에서 언급된 도메인 분리와 보안 고려사항은 견고한 아키텍처를 시사합니다.
           결론: 기술적 측면에서 이 프로젝트는 실현 가능성이 높습니다.
        
        2. 시장 잠재력: 7/10
           추론 과정:
           a) 기능의 보편성: 사용자 인증과 제품 카탈로그는 대부분의 e-커머스 플랫폼에 필수적입니다. 이는 넓은 적용 가능성을 의미합니다.
           b) 차별화 요소 분석: 현재 백로그에서는 특별한 차별화 요소가 보이지 않습니다. 이는 시장에서의 경쟁력에 영향을 줄 수 있습니다.
           c) 시장 규모 추정: 구체적인 타겟 시장이 명시되지 않아 정확한 규모 추정이 어렵습니다. 그러나 e-커머스 시장 자체는 계속 성장 중입니다.
           결론: 기본적인 시장 잠재력은 있으나, 차별화 부족으로 인해 높은 점수를 주기는 어렵습니다.
        
        3. 리스크 요인: 6/10
           추론 과정:
           a) 보안 리스크: 사용자 인증 시스템은 항상 보안 위험을 수반합니다. 그러나 백로그에서 보안에 대한 인식이 있어 긍정적입니다.
           b) 기술적 리스크: 사용된 기술 스택이 안정적이므로 기술적 리스크는 낮습니다.
           c) 프로젝트 관리 리스크: 구체적인 일정과 리소스 정보가 없어 이 부분의 리스크를 정확히 평가하기 어렵습니다.
           결론: 보안 리스크가 주요 관심사이며, 프로젝트 관리 측면의 불확실성이 있습니다.
        
        4. 예상 ROI: 7/10
           추론 과정:
           a) 개발 비용 추정: 사용된 기술과 기능의 복잡도를 고려할 때, 개발 비용은 중간 정도로 예상됩니다.
           b) 유지보수 비용 예측: 안정적인 기술 스택으로 인해 유지보수 비용은 상대적으로 낮을 것으로 보입니다.
           c) 수익 모델 분석: 구체적인 수익 모델이 명시되지 않아 정확한 수익 예측이 어렵습니다.
           결론: 개발 및 유지보수 비용 대비 잠재적 수익은 긍정적이나, 구체적인 수익 모델 부재로 높은 점수는 어렵습니다.
        
        5. 개선 제안사항:
           a) 사용자 경험(UX) 향상: 현재 백로그는 기본 기능에 집중되어 있습니다. 사용자 만족도를 높이기 위한 UX 관련 기능 추가를 고려해야 합니다.
           b) 확장성 고려: 향후 성장을 위해 마이크로서비스 아키텍처 도입을 검토할 수 있습니다.
           c) 데이터 활용: 사용자 행동 분석이나 제품 추천 시스템 등 데이터 기반의 기능을 추가하여 비즈니스 가치를 높일 수 있습니다.
        
        종합 평가: 72/100
        최종 추론: 이 프로젝트는 기술적으로 안정적이며 기본적인 e-커머스 기능을 갖추고 있어 실현 가능성이 높습니다. 
        그러나 차별화 요소가 부족하여 시장에서의 경쟁력 확보가 과제입니다. 보안에 대한 인식은 긍정적이지만, 구체적인 비즈니스 모델과 목표 시장이 명확하지 않아 정확한 ROI 예측이 어렵습니다. 
        전반적으로 안정적이지만 보수적인 프로젝트로 평가됩니다. 
        제안된 개선사항을 고려하여 프로젝트의 가치를 높일 수 있을 것입니다.
        </example>
        
        ### 이제 다음 백로그에 대해 위 예시와 같은 방식으로 사업성을 분석해주세요: ###
        {context}
        
        분석 지침:
        1. 각 평가 항목(기술적 실현 가능성, 시장 잠재력, 리스크 요인, 예상 ROI, 개선 제안사항)에 대해 a), b), c) 등으로 세부 추론 과정을 나누어 설명하세요.
        2. 각 항목에 대해 1-10 척도로 점수를 매기고, 구체적인 근거를 제시하세요.
        3. 각 항목의 결론을 간단히 요약하세요.
        4. 마지막에 전체적인 사업성에 대한 종합 평가와 1-100 점수를 제공하세요.
        
        출력 형식:
        1. 기술적 실현 가능성: [점수]/10
           추론 과정:
           a) [세부 추론]
           b) [세부 추론]
           c) [세부 추론]
           결론: [간단한 요약]
        
        2. 시장 잠재력: [점수]/10
           [위와 같은 형식으로 작성]
        
        3. 리스크 요인: [점수]/10
           [위와 같은 형식으로 작성]
        
        4. 예상 ROI: [점수]/10
           [위와 같은 형식으로 작성]
        
        5. 개선 제안사항:
           a) [제안 1]
           b) [제안 2]
           c) [제안 3]
        
        종합 평가: [점수]/100
        최종 추론: [전체적인 사업성 평가 요약]
        
        주의사항:
        - 각 항목에 대해 제공된 백로그 정보를 바탕으로 구체적이고 논리적인 분석을 제공하세요.
        - 예시 답변을 그대로 복사하지 말고, 제공된 백로그의 특성에 맞게 새롭게 분석하세요.
        - 기술적 측면, 시장 상황, 프로젝트의 특성을 종합적으로 고려하여 평가하세요.
        """

result = llm(template, **generation_kwargs)

print(result['choices'][0]['text'])
