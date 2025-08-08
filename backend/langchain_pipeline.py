# langchain_pipeline.py

import os
from dotenv import load_dotenv
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.text_splitter import CharacterTextSplitter, RecursiveCharacterTextSplitter
from langchain.llms import OpenAI
from langchain.chains import ConversationalRetrievalChain, RetrievalQA
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain.docstore.document import Document

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

from langchain.text_splitter import TextSplitter

class SentenceTextSplitter(TextSplitter):
    def __init__(self, chunk_size: int = 5, chunk_overlap: int = 1):
        super().__init__()
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def sentence_tokenize(self, text: str):
        sentence_endings = {"\n\n", '\n'}
        sentences = []
        sentence = ""

        for char in text:
            sentence += char
            if char in sentence_endings:
                trimmed = sentence.strip()
                if trimmed:
                    sentences.append(trimmed)
                sentence = ""

        return sentences

    def split_text(self, text: str):
        sentences = self.sentence_tokenize(text)
        chunks = []
        start = 0

        while start < len(sentences):
            end = start + self.chunk_size
            chunk = "\n".join(sentences[start:end])
            chunks.append(chunk)
            start += self.chunk_size - self.chunk_overlap

        return chunks

    def split_documents(self, documents: list[Document]) -> list[Document]:
        split_docs = []

        for doc in documents:
            text_chunks = self.split_text(doc.page_content)
            for i, chunk in enumerate(text_chunks):
                metadata = dict(doc.metadata)
                metadata["chunk"] = i
                split_docs.append(Document(page_content=chunk, metadata=metadata))

        return split_docs



embedding = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY, model="text-embedding-3-small")


CHROMA_DIR = "chroma_db"
vectorstore = Chroma(
    collection_name="rag_docs",
    embedding_function=embedding,
    persist_directory=CHROMA_DIR, 
)

llm = ChatOpenAI(
    openai_api_key=OPENAI_API_KEY,
    model="gpt-4",
)

system_prompt = SystemMessagePromptTemplate.from_template(
    "You are an expert document assistant. Analyze the document and answer the user's questions elaborately "
    "using only the information provided in the context below. "
    "If the answer is not explicitly stated or cannot be confidently inferred, "
    "say 'The answer is not available in the provided document.'"
)


human_prompt = HumanMessagePromptTemplate.from_template(
    "Document:\n{context}\n\nQuestion: {question}"
)


chat_prompt = ChatPromptTemplate.from_messages([system_prompt, human_prompt])


qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=vectorstore.as_retriever(search_kwargs={"k": 5},),
    chain_type="stuff",
    chain_type_kwargs={"prompt": chat_prompt},
    return_source_documents=True
)


def ingest_chunks(chunks, filename, file_id, page_numbers=None):
    if page_numbers:
        docs = [
        Document(page_content=chunk, metadata={"filename": filename, "file_id":file_id, "page": page})
        for chunk, page in zip(chunks, page_numbers)
    ]
    else:
        docs = [Document(page_content=chunks, metadata={"filename": filename, "file_id":file_id})]

    splitter = SentenceTextSplitter(chunk_size=5, chunk_overlap=1)
    split_docs = splitter.split_documents(docs)
    vectorstore.add_documents(split_docs)
    vectorstore.persist()


def ask_question(question: str):
    result = qa_chain.invoke({"query": question})
    return result


