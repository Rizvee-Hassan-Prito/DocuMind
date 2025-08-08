import streamlit as st
import requests
import base64
import os

from dotenv import load_dotenv

load_dotenv()

host = os.getenv("STREAMLIT_HOST", "127.0.0.1")
port = int(os.getenv("STREAMLIT_PORT", 8501))

FastAPI_URL = os.getenv("FastAPI_URL")

if "document_ids" not in st.session_state:
    st.session_state.document_ids = {}

st.title(" 🧠📄 DocuMind – Intelligent Q&A over documents")
st.subheader("Upload Document")
# Upload Section
uploaded_files = st.file_uploader("Upload pdf/docx/txt/csv/db files here:", type=["pdf", "docx", "txt", "csv", "db", "sqlite3"], accept_multiple_files=True)
if uploaded_files:
    with st.spinner("🌀 Uploading files..."):
        for uploaded_file in uploaded_files:
            res = requests.post(f"{FastAPI_URL}/upload/", files={"file": uploaded_file})
            if res.ok:
                json_data = res.json()
                doc_id = json_data.get("file_id")
                st.success(f"✅ Uploaded: {uploaded_file.name},  File ID: {doc_id}")
                st.session_state.document_ids[uploaded_file.name] = doc_id
            else:
                st.error(f"❌ Failed to upload {uploaded_file.name}")
# Query Section
st.subheader("Ask Questions")
question = st.text_input("Ask questions based on uploaded documents or images:")
st.subheader("Optional: Upload image for OCR")
image = st.file_uploader("Upload png/jpg/jpeg or pdf containing images", type=["png", "jpg", "jpeg", "pdf"])

if st.button("Get Answer"):
    with st.spinner("⏳ Result is generating. Please wait..."):
        image_base64 = None
        if image:
            image_base64 = base64.b64encode(image.read()).decode("utf-8")

        payload = {"question": question}
        if image_base64:
            payload["image_base64"] = image_base64

        res = requests.post(f"{FastAPI_URL}/query/", json=payload)

        if res.ok:
            data = res.json()["context"]

            st.subheader("Answer")
            st.write(data["result"])
            if "source_documents" in data:
                st.subheader("Contexts & Sources")
                contexts=[]
                sources=[]
                for i in data["source_documents"]:
                    if i["page_content"] not in contexts:
                        contexts.append(i["page_content"])
                        sources.append(i["metadata"])
                for i,context in enumerate(contexts):
                    st.write(f"Context {i+1}:")
                    st.text(context)
                    if "page" in sources[i]:
                        st.write("Source Info: Page ",f"{sources[i]['page']}", "of ", sources[i]['filename'])
                    else:
                        st.write("Source Info: ",sources[i]['filename'])
        else:
            st.error("Error fetching answer: " + res.text)


