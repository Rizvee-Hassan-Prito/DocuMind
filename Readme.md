# 🧠📄 DocuMind – Intelligent Q&A over documents

## 🔍 Overview
DocuMind is a full-stack, RAG-based (Retrieval-Augmented Generation) web application that enables intelligent question-answering over a wide range of documents. Built with Streamlit, FastAPI, LangChain, Docker, and OpenAI’s GPT-4, this app empowers users to extract answers from both textual and image-based files.

Users can upload files in various formats including:

Textual documents: PDF, DOCX, TXT, CSV, DB

Image documents: PNG, JPG, JPEG, and scanned PDFs containing text

For image-based content, the app performs OCR (Optical Character Recognition) to extract embedded text. Once processed, users can ask natural language questions, and the app responds using GPT-4 based on the extracted and semantically indexed content.

Each answer includes:

✅ The relevant context used for generation

📂 The source file name(s) for transparency and traceability

This system combines modern LLM capabilities with custom document understanding, offering a powerful tool for document analysis and automated insights.

## 🚀 Instructions
    
### Environment Setup: ▶️ How to Run with Docker

1. **Clone the repository**
```bash
git clone https://github.com/Rizvee-Hassan-Prito/DocuMind.git
cd DocuMind
```
2. **Add OPENAI_API_KEY in all the .env files (Root folder, frontend, backend):**
```bash
OPENAI_API_KEY="Your OpenAI Api-Key"
```
2. **Build and start the services:**
```bash
docker-compose up --build
```

3. **Access the app in a browser**
```bash
Frontend: http://localhost:8501
Backend API: http://localhost:8000
```

### Environment Setup: ▶️ How to Run without Docker

1. Install tesseract-ocr using the tesseract-ocr-setup-3.02.02.exe file.
After installation, update the tesseract_cmd path in the backend/utils/util_functions.py file by replacing the placeholder with the actual installation path:
```bash 
pytesseract.pytesseract.tesseract_cmd = r'Include Tesseract-OCR installation path' 
``` 

2. **Create a virtual environment and install dependencies:**
```bash
python -m venv venv
venv\Scripts\activate  # or source venv\bin\activate on Linux
pip install -r requirements.txt
```
3. **Add OPENAI_API_KEY and edit FastAPI_URL in all the .env files (Root folder, frontend, backend)::**
```bash
OPENAI_API_KEY="Your OpenAI Api-Key"
FastAPI_URL="http://localhost:8000"
```
4. **Open a terminal and run FastAPI as the Backend**
```bash
cd backend
uvicorn main:app --reload
```
5. **In a separate terminal, run StreamLit as the Frontend**
```bash
cd frontend
streamlit run app.py
```
### ▶️ How to use features

To use the features, follow the below steps:

1. **Uoload files or images**
2. **Ask quetions based on the uploaded files**
3. **Press Get Answer** 

#### 📸 UI Image 
<img width="318" height="311" alt="image" src="https://github.com/user-attachments/assets/21202f61-0aef-4588-a06e-3175b56bed85" />


## 🔌 API Usage

Base URL: `http://localhost:8000`

---

### 📄 POST `/upload/` endpoint

**Description**: Upload a document file (PDF, image, etc.) for processing and extraction.

- **Headers**:
  - `accept: application/json`
  - `Content-Type: multipart/form-data`

- **Form Data**:
  - `file`: File to be uploaded

- **cURL Example**:
```bash
  curl -X 'POST' \
    'http://localhost:8000/upload/' \
    -H 'accept: application/json' \
    -H 'Content-Type: multipart/form-data' \
    -F 'file=@yourfile.pdf;type=application/pdf'
```

---

### 💬 POST `/query/` endpoint

**Description**: Ask a question about the uploaded document (supports questions with embedded images in base64).

- **Headers**:
  - `accept: application/json`
  - `Content-Type: application/json`

- **Request Body**:
  ```json
  {
    "question": "What is the summary of the document?",
    "image_base64": "optional_base64_encoded_image_string"
  }

- **cURL Example**:
```bash
curl -X 'POST' \
  'http://localhost:8000/query/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "question": "What is the summary of the document?",
  "image_base64": "string"
}'
```
----

## 🔑 Sample .env 
```bash
# OpenAI API Key
OPENAI_API_KEY="Your OpenAI API_key"  

# FastAPI configuration
FastAPI_URL="http://backend:8000"  #<-For Docker  #For Local access: http://localhost:8000
FASTAPI_HOST=127.0.0.1
FASTAPI_PORT=8000

# Streamlit configuration
STREAMLIT_HOST=127.0.0.1
STREAMLIT_PORT=8501
```
