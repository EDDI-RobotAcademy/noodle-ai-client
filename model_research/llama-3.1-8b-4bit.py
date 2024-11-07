from mlx_lm import load, stream_generate

model, tokenizer = load("mlx-community/Meta-Llama-3.1-8B-Instruct-4bit",
                        tokenizer_config={"eos_token": "<|endoftext|>", "trust_remote_code": True})

context = ""
with open("test_file.txt", "r") as f:
    for line in f.readlines():
        context += line

prompt = f"""
다음 코드를 분석하고, 애자일 프로세스에 따라 개발 백로그를 작성해 주세요. 
오직 1개의 백로그 항목만 작성해야합니다.
1개의 백로그는 코드의 전체 흐름과 기능을 설명할 수 있어야 합니다.
주어진 조건 이외에 다른 내용은 출력하면 안됩니다.
백로그는 다음 정보를 포함해야 합니다:

1. 백로그 제목
2. 설명 (전체 코드의 역할을 언급)
3. 우선순위 (1~5 사이에서 중복되지 않도록 각 항목에 하나씩만 할당)
4. 추정 소요 시간 (단위: 시간, 간략히 1~5시간으로 범위 내에서 지정)


코드: {context}
"""
response = stream_generate(model, tokenizer, prompt=prompt, max_tokens=512)

for res in response:
    print(res, end="")
