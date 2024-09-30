from typing import List

from langchain.chains.retrieval_qa.base import RetrievalQA
from langchain_community.vectorstores.utils import DistanceStrategy
from langchain_core.embeddings import Embeddings
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableConfig
from langchain_openai import ChatOpenAI
from openai import OpenAI
from git import Repo
from langchain_community.document_loaders.generic import GenericLoader
from langchain_community.document_loaders.parsers import LanguageParser
from langchain_text_splitters import Language
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from sympy.physics.units import temperature

# Clone
repo_path = "./github_repositories"
# repo = Repo.clone_from("https://github.com/SKNETWORKS-FAMILY-AICAMP/SKN02-1st-1Team", to_path=repo_path)

# Load
loader = GenericLoader.from_filesystem(
    repo_path,
    glob="**/*",
    suffixes=[".py"],
    exclude=["**/non-utf8-encoding.py"],
    parser=LanguageParser(language=Language.PYTHON, parser_threshold=100)
)
documents = loader.load()
print(len(documents))

# Splitting
python_splitter = RecursiveCharacterTextSplitter.from_language(
    language=Language.PYTHON, chunk_size=1000, chunk_overlap=100
)

texts = python_splitter.split_documents(documents)
print(len(texts))


# Custom Embedding
# Embeddings을 상속해야하고,
# 내부에 embed_documents와 embed_query가 정의되어야 한다.
class LMStudioEmbeddings(Embeddings):
    def __init__(self, base_url, api_key="lm_studio"):
        self.client = OpenAI(base_url=base_url, api_key=api_key)

    def embed_documents(self, textList: List[str], model="nomic-ai/nomic-embed-text-v1.5-GGUF") -> List[List[float]]:
        textList = list(map(lambda text: text.replace("\n", " "), textList))
        datas = self.client.embeddings.create(input=textList, model=model).data
        return list(map(lambda data: data.embedding, datas))

    def embed_query(self, text: str) -> List[float]:
        return self.embed_documents([text])[0]


embed = LMStudioEmbeddings(base_url="http://localhost:1234/v1")


# RAG
vectorstore = FAISS.from_documents(texts, embedding=embed, distance_strategy=DistanceStrategy.COSINE)
retriever = vectorstore.as_retriever()

template = """
Please analyze the following source code and extract the individual functionalities implemented in the code. Present the analysis in a structured format that makes it easy to preprocess the data and extract the functionalities. Follow these guidelines:

1. If there are classes in the code, provide the information in the following structured format:
   - **Class Name:**
     - **Method:**
       - Method Name: Detailed explanation of the method's functionality

2. If there are no classes but only functions, provide the information in the following structured format:
   - **Function:**
     - Function Name: Detailed explanation of the function's functionality

3. If there are neither classes nor functions, provide an overview of the entire code and break down the functionalities into separate items in the following structured format:
   - **Code Segment:**
     - Segment Description: Detailed explanation of the functionality

Ensure to clearly outline the role and purpose of each functionality, as this information will be used to create backlog items for an Agile development process.
{context}
"""

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            template,
        ),
        (
            "human",
            "{question}"
        )
    ]
)

llm = ChatOpenAI(
    base_url="http://localhost:1234/v1",
    api_key="lm_studio",
    model="lmstudio-community/Yi-Coder-9B-Chat-GGUF",
    temperature=0.3
)

chain = (
    {"context": retriever, "question": RunnablePassthrough(),}
    | prompt
    | llm
    | StrOutputParser()
)

user_input = "User input: Following this code, I want to implement a login function using the Github API, so please write a backlog accordingly."
for chunk in chain.stream(input=user_input):
    print(chunk, end="")
