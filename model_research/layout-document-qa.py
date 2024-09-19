import torch
from transformers import pipeline
from datasets import load_dataset
from evaluate import load
from tqdm import tqdm
import pandas as pd

model_name = "impira/layoutlm-document-qa"
task = "document-question-answering"

dataset = load_dataset("nielsr/docvqa_1200_examples_donut", split="train[:5%]")
print("Sample data:", dataset[0])
print("Question:", dataset[0]['query']['en'])
print("Answer:", dataset[0]['answer']['text'])
metric = load("rouge")

def evaluate_qa(model_name, dataset):
    print("Start evaluating QA")
    pipe = pipeline(task, model=model_name, device="mps")

    references = []
    answers = []

    for data in tqdm(dataset, total=len(dataset)):
        image = data['image']

        question = data['query']['en']
        answer = pipe(image=image, question=question)
        print("answer:", answer)
        if answer:
            answers.append(answer[0]['answer'])
        else:
            answers.append("")
        references.append(data['answer']['text'])

    df = pd.DataFrame(list(zip(answers, references)), columns=['Question-Answering', 'Answer'])
    print("Processing to make dataframe to csv...")
    df.to_csv(f'./{model_name.split("/")[0]}.csv')
    print("Process completed.")
    score = metric.compute(predictions=answers, references=references)
    return score

score = evaluate_qa(model_name, dataset)
print("Model:", model_name)
print("Score:", score)
with open(f"{model_name.split('/')[0]}.txt", "w") as f:
    f.write(score)
print(f"Complete to save {model_name} rouge score in {model_name.split('/')[0]}.txt")