import pandas as pd
import torch
from transformers import pipeline, GenerationConfig
from datasets import load_dataset
from evaluate import load
from tqdm import tqdm

model_name = "naver-clova-ix/donut-base-finetuned-docvqa"
task = "document-question-answering"

dataset = load_dataset("nielsr/docvqa_1200_examples_donut", split="train[:5%]")
print("Sample data:", dataset[0])
print("Question:", dataset[0]['query']['en'])
print("Answer:", dataset[0]['answer']['text'])
metric = load("rouge")

def evaluate_qa(model_name, dataset):
    print("Start evaluating QA")

    pipe = pipeline(
        task,
        model=model_name,
        model_kwargs={"torch_dtype": torch.bfloat16},
        # device="mps"
        device="cuda"
    )
    pipe.model.eval()

    beginners =  [
        pipe.tokenizer.bos_token_id
    ]
    terminators = [
        pipe.tokenizer.eos_token_id,
        pipe.tokenizer.convert_tokens_to_ids("<end_of_turn>")
    ]

    generation_config = GenerationConfig(
        max_new_tokens=2048,
        do_sample=True,
        top_k=40,
        temperature=0.3,
        bos_token_id=beginners,
        eos_token_id=terminators,
        pad_token_id=pipe.tokenizer.pad_token_id
    )
    pipe.model.generation_config = generation_config

    references = []
    answers = []

    for data in tqdm(dataset, total=len(dataset)):
        image = data['image']
        question = data['query']['en']

        answer = pipe(
            image=image,
            question=question,
        )

        print("answer:", answer[0]['answer'])

        answers.append(answer[0]['answer'])
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
    f.write(f"{score}")
print(f"Complete to save {model_name} rouge score in {model_name.split('/')[0]}.txt")