import pandas as pd
from datasets import load_dataset
from llama_cpp import Llama
from evaluate import load
from tqdm import tqdm
import pytesseract

model_name = "Phi-3.5-mini-instruct-Q4_K_M.gguf"
repo_id = "bartowski/Phi-3.5-mini-instruct-GGUF"

dataset = load_dataset("nielsr/docvqa_1200_examples_donut", split="train[:5%]")
metric = load("rouge")

def evaluate_qa(model_name, repo_id, dataset):
    model = Llama.from_pretrained(repo_id=repo_id, filename=model_name, n_ctx=2048)

    references = []
    answers = []

    for data in tqdm(dataset, total=len(dataset)):
        image = data['image']
        question = data['query']['en']
        context = pytesseract.image_to_string(image)

        message = [
            {"role": "user", "content": f"너는 주어진 Context를 이용해서 사용자의 질문에 대답해주는 질의응답 어시스턴트야. You are a assistant that helps users by using given Context.\n\nContext: {context}\nQuestion: {question}\n"}
        ]

        answer = model.create_chat_completion(message, max_tokens=2048)
        print("answer:", answer["choices"][0]['message']['content'])

        answers.append(answer["choices"][0]['message']['content'])
        references.append(data['answer']['text'])

    df = pd.DataFrame(list(zip(answers, references)), columns=['Question-Answering', 'Answer'])
    print("Processing to make dataframe to csv...")
    df.to_csv(f'./{model_name.split("/")[0]}.csv')
    print("Process completed.")
    score = metric.compute(predictions=answers, references=references)

    return score

score = evaluate_qa(model_name, repo_id, dataset)
print("Model:", model_name)
print("Score:", score)
with open(f"{model_name.split('/')[0]}.txt", "w") as f:
    f.write(f"{score}")
print(f"Complete to save {model_name} rouge score in {model_name.split('/')[0]}.txt")