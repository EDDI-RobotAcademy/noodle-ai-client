import os

from llama_cpp import Llama
from transformers import AutoTokenizer


model_id = 'MLP-KTLim/llama-3-Korean-Bllossom-8B-gguf-Q4_K_M'
tokenizer = AutoTokenizer.from_pretrained(model_id)
llm = Llama.from_pretrained(
	repo_id="MLP-KTLim/llama-3-Korean-Bllossom-8B-gguf-Q4_K_M",
	filename="llama-3-Korean-Bllossom-8B-Q4_K_M.gguf",
    n_gpu_layers=-1,
    n_ctx=1024
)

PROMPT = \
'''당신은 유용한 AI 어시스턴트입니다. 사용자의 질의에 대해 친절하고 정확하게 답변해야 합니다.
You are a helpful AI assistant, you'll need to answer users' queries in a friendly and accurate manner.'''


githubRepositoryPath = "./github_repositories/noodle-backend"

responseList = []
for path, dirs, files in os.walk(githubRepositoryPath):
    for file in files:
        if not file.endswith(".py"):
            continue

        filePath = os.path.join(path, file)
        context = f"File: {filePath}\n"
        with open(filePath, "r") as f:
            context += f.read()

        context = context[:1024]
        template = f"""당신은 소스 코드 분석을 위한 AI 어시스턴트입니다. 아래에 제공된 소스 코드를 분석하여 그 역할을 간단하게 설명하세요.

            ### Input:
            {context}
            
            ### 요청 사항:
            1. 코드의 전체적인 역할을 간단하게 요약하세요. (50자 이내)
            2. 주요 함수나 클래스의 이름과 그 역할을 설명하세요. (200자 이내)
            3. 함수 간의 상호작용을 설명하세요. (150자 이내)
            
            출력은 한국어로 해주세요.
            Answer:"""

        messages = [
            {"role": "system", "content": f"{PROMPT}"},
            {"role": "user", "content": f"{template}"}
        ]

        prompt = tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )

        generation_kwargs = {
            "max_tokens": 512,
            "stop": ["<|eot_id|>"],
            "top_p": 0.9,
            "temperature": 0.2,
            "echo": True,  # Echo the prompt in the output
            "stream": True
        }

        resonse_msg = llm(prompt, **generation_kwargs)
        for chunk in resonse_msg:
            print(chunk['choices'][0]['text'], end="")
