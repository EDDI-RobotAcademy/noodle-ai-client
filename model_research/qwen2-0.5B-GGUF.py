from llama_cpp import Llama

llm = Llama.from_pretrained(
	repo_id="Qwen/Qwen2-0.5B-Instruct-GGUF",
	filename="qwen2-0_5b-instruct-q6_k.gguf",
    n_ctx=2048,
    n_gpu_layers=-1
)

code_input = ""
with open("test_file.txt", "r") as f:
	for line in f.readlines():
		code_input += line

system_prompt = """
Please analyze the following code and write the development backlog according to the Agile process.
Only one backlog entry must be created.
One backlog must be able to describe the full flow and function of the code.
You should not print anything other than the conditions given.
Backlogs must contain the following information:

1. Backlog title
2. Description (Referring to the role of the full code)
3. Priority (assign only one for each item to avoid duplication between 1 and 5)
4. Estimated time taken (in units of time, within a range of 1 to 5 hours)
"""

output = llm.create_chat_completion(
	messages = [
		{
			"role": "system",
			"content": system_prompt
		},
		{
			"role": "user",
			"content": f"Code: {code_input}"
		}
	],
    stream=True,
	stop=["<|user|>", "<|assistant|>", "<|system|>", "<|end|>", "<|endoftext|>"]
)

for out in output:
	delta = out['choices'][0]['delta']

	if 'role' in delta:
		print(delta["role"], end=": ")
	elif 'content' in delta:
		print(delta['content'], end="")
