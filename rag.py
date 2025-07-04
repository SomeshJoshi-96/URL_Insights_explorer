import os
from uuid import uuid4
from dotenv import load_dotenv
from pathlib import Path

from langchain.chains import RetrievalQAWithSourcesChain
from langchain_community.document_loaders import SeleniumURLLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq


load_dotenv()
CHUNK_SIZE = 100
EMBEDDING_MODEL = "Alibaba-NLP/gte-base-en-v1.5"
VECTORSTORE_DIR   = Path(__file__).parent / "resources/vectorstore"
COLLECTION_NAME   = "real_estate"
CHUNK_OVERLAP = 0

llm = None
vector_store = None

print("Initializing Components")
def initialize_components():
    global llm

    if llm is None:
        llm = ChatGroq(model="llama-3.3-70b-versatile",
                   temperature=0.9, max_tokens = 500)


    global vector_store

    if vector_store is None:
        ef = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL, model_kwargs = {"trust_remote_code":True})
        vector_store = Chroma(collection_name = COLLECTION_NAME, persist_directory =str(VECTORSTORE_DIR),
                          embedding_function = ef)


def generate_answer(query):
    if not vector_store:
        raise RuntimeError("VectorDB not initialized!")
    chain = RetrievalQAWithSourcesChain.from_llm(llm=llm, retriever=vector_store.as_retriever())
    result = chain.invoke({"question": query}, return_only_outputs=True)
    sources = result.get("sources", "")

    return result['answer'], sources


def process_urls(urls):
    initialize_components()
    yield "Resetting collection..."
    vector_store.reset_collection()
    loader = SeleniumURLLoader(urls)
    yield "Loading Data..."
    data = loader.load()

    yield "Splitting text..."
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        separators = ["\n\n", "\n", ".", " "],
        chunk_overlap=CHUNK_OVERLAP
    )
    docs = text_splitter.split_documents(data)
    # yield(f"Number of text chunks: {len(docs)}")
    # for i, d in enumerate(docs[:5]):
    #     print(f"── chunk {i} ({len(d.page_content)} chars): {d.page_content[:50]!r}…")
    uuids = [str(uuid4()) for _ in range(len(docs))]
    yield "Adding docs to vector db..."
    vector_store.add_documents(docs, ids=uuids)
    yield "Done adding docs to vector db..."
if __name__ == "__main__":
    urls = [
        "https://www.cnbc.com/2024/12/21/how-the-federal-reserves-rate-policy-affects-mortgages.html",
        "https://www.cnbc.com/2024/12/20/why-mortgage-rates-jumped-despite-fed-interest-rate-cut.html",
    ]
    process_urls(urls)
    # results = vector_store.similarity_search(
    #     "30 year mortgage rate",
    #     k=2
    # )
    # print(results)
    answer, sources = generate_answer("Tell me what was the 30 year fixed mortgage rate along with the date?")
    print(f"Answer: {answer}")
    print(f"Sources: {sources}")
