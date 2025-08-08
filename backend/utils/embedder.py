import os
from openai import OpenAI
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
from dotenv import load_dotenv

load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
openai_ef = embedding_functions.OpenAIEmbeddingFunction(api_key=openai_api_key, model_name="text-embedding-3-small")


client = chromadb.PersistentClient(path="./chroma_data")
collection = client.get_or_create_collection(name="rag_docs",  embedding_function=openai_ef)


def chunk_text(text, chunk_size=500, overlap=100):
    chunks = []
    for i in range(0, len(text), chunk_size - overlap):
        chunks.append(text[i:i + chunk_size])
    return chunks

def embed_and_store(chunks, metadata):
    metadatas = []
    file_id=metadata.get("file_id", None)
    # all_ids = collection.get(include=["ids"])["ids"]
    if metadata["page_num"]:
        for i, chunk in enumerate(chunks):
            metadata_json = {
                "filename": metadata['filename'],
                "chunk_index": i,
                "file_id": file_id,
                "page_num": None
            }
            page_numbers=metadata["page_num"]
            if page_numbers:
                metadata_json["page_num"] = page_numbers[i] if i < len(page_numbers) else None
            metadatas.append(metadata_json)
    else:
        for i, chunk in enumerate(chunks):
            metadatas.append({"filename": metadata['filename'], "file_id": file_id, "chunk_index": i})
    
    collection.add(
        documents=chunks,
        metadatas=metadatas,
        ids=[f"{ metadata['filename']}_{i}" for i in range(len(chunks))],
    )


def query_chunks(question):
    results = collection.query(
        query_texts=[question],
        n_results=3,
    )
    return results
