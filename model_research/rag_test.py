import os
from git import Repo
from transformers import pipeline
import faiss
import torch

# 1. GitHub 리포지토리 클론
def clone_repository(repo_url, clone_dir):
    if not os.path.exists(clone_dir):
        os.makedirs(clone_dir)
        Repo.clone_from(repo_url, clone_dir)
    else:
        print(f"Repository already cloned at {clone_dir}")

# 2. 코드 파일 수집 및 전처리
def collect_code_files(root_dir, extensions=['.py']):
    code_files = []
    for subdir, _, files in os.walk(root_dir):
        for file in files:
            if any(file.endswith(ext) for ext in extensions):
                code_files.append(os.path.join(subdir, file))
    return code_files

def extract_code_snippets(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        code = f.read()
    # 필요한 전처리 작업 수행 (예: 주석 추출 등)
    # 여기서는 전체 코드를 하나의 문서로 사용
    return code

# 3. 문서 생성
def create_documents(code_files):
    documents = []
    for file_path in code_files:
        code_content = extract_code_snippets(file_path)
        documents.append(code_content)
    return documents

# 4. 문서 임베딩 및 인덱싱
def embed_documents(documents, embedder):
    embeddings = embedder.encode(documents, convert_to_tensor=True)
    embeddings = embeddings.cpu().numpy()
    return embeddings

def create_faiss_index(embeddings):
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)
    return index

# 5. 질문에 대한 응답 생성
def retrieve_documents(question, embedder, index, documents, k=5):
    question_embedding = embedder.encode([question], convert_to_tensor=True)
    question_embedding = question_embedding.cpu().numpy()
    distances, indices = index.search(question_embedding, k)
    retrieved_docs = [documents[i] for i in indices[0]]
    return retrieved_docs

def generate_answer(question, pipe, retrieved_docs):
    context = '\n'.join(retrieved_docs)
    input_text = f"질문: {question}\n코드 문맥:\n{context}\n답변:"
    outputs = pipe(
        input_text,
        max_new_tokens=512,
        do_sample=True,
        temperature=0.7,
    )
    answer = outputs[0]["generated_text"].split("답변:")[-1].strip()
    return answer

# 메인 실행 흐름
if __name__ == "__main__":
    from sentence_transformers import SentenceTransformer
    import numpy as np
    import os
    from dotenv import load_dotenv
    import time
    
    start = time.time()
    
    load_dotenv()
    HUGGING_FACE_ACCESS_TOKEN = os.getenv("HUGGING_FACE_ACCESS_TOKEN")

    # 리포지토리 정보
    repo_url = "https://github.com/ih9511/noodle-backend"
    clone_dir = "./noodle-backend"

    # 1. 리포지토리 클론
    clone_repository(repo_url, clone_dir)

    # 2. 코드 파일 수집
    code_files = collect_code_files(clone_dir)

    # 3. 문서 생성
    documents = create_documents(code_files)

    # 4. 임베딩 모델 로드
    embedder = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

    # 문서 임베딩 및 인덱싱
    document_embeddings = embed_documents(documents, embedder)
    index = create_faiss_index(document_embeddings)

    # 5. 파이프라인 로드
    model_id = "meta-llama/Llama-3.2-3B-Instruct"
    pipe = pipeline(
        "text-generation",
        model=model_id,
        torch_dtype=torch.bfloat16,
        token = HUGGING_FACE_ACCESS_TOKEN,
        device_map="auto",
    )

    # 6. 질문에 대한 응답 생성
    question = f"""
    프로젝트에 대해 프로젝트 맥락에 맞게 주요 함수 및 메서드 단위 기능 중심으로 백로그들을 만드십시오.
    주요 언어는 Python 입니다.
    
    백로그 작성 전략은 다음과 같습니다.
    1. 각 함수 및 메서드들에 대해 `Success Criteria`와 이에 따른 `To Do`로 나눌 것.
    2. `JSON` 형태로 반환하여 데이터화가 용이하게 할 것.
    
    `JSON` 형태는 예시는 다음과 같습니다.
    Backlog name: 
    Success Criteria: 
    To Do: 
    """
    retrieved_docs = retrieve_documents(question, embedder, index, documents)
    answer = generate_answer(question, pipe, retrieved_docs)
    print(answer)

    end = time.time()
    
    print(f'추론 소요 시간 = {end - start: .2f}s')