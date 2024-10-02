from transformers import TextStreamer, AutoModelForCausalLM, AutoTokenizer
import torch

# device = "mps" if torch.backends.mps.is_available() else "cpu"
device = "cuda" if torch.backends.mps.is_available() else "cpu"

model_id = "facebook/xglm-564M"

tokenizer = AutoTokenizer.from_pretrained(model_id)
# tokenizer.chat_template = "<prompt_template>"

model = AutoModelForCausalLM.from_pretrained(model_id)
model.to(device)

context = ""

with open("test_file.txt", "r") as f:
    for line in f.readlines():
        context += line

# user_input = input("질문을 입력하세요: ")

prompt = [
    {"role": "system", "content": """You are a chatbot that analyzes the code. 
    You need to analyze the following user input code and write backlogs of the Agile process about this code.
    Backlog means A product backlog is a list of the new features, 
    changes to existing features, bug fixes, infrastructure changes, 
    or other activities that a team may deliver in order to achieve a specific outcome."""},
    {"role": "user", "content": context},
]


question = tokenizer(context, return_tensors="pt").to(device)

streamer = TextStreamer(tokenizer, skip_prompt=True)

model.generate(**question, streamer=streamer,
               pad_token_id=tokenizer.eos_token_id,
               max_length=2048,
               do_sample=True,
               temperature=0.3,
               top_p=0.8,
               repetition_penalty=1.5)
