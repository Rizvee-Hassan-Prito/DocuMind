from fastapi import FastAPI, File, UploadFile
from langchain_pipeline import *
from pydantic import BaseModel
from utils.util_functions import *
from utils.embedder import *
from openai import OpenAI
from dotenv import load_dotenv
import os
import base64
import io
import uuid
import uvicorn

load_dotenv()
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = FastAPI()

class QueryRequest(BaseModel):
    question: str
    image_base64: str = None

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    suffix = file.filename.split(".")[-1]
    content = ""
    page_numbers = None
    if suffix == "pdf":
        content, page_numbers = extract_text_from_pdf(file.file)
    elif suffix == "docx":
        content = extract_text_from_docx(file.file)
    elif suffix == "txt":
        content = extract_text_from_txt(file.file)
    elif suffix in ["jpg", "jpeg", "png"]:
        image_base64 = base64.b64encode(file.file.read()).decode("utf-8")
        image_data = base64.b64decode(image_base64)
        image = Image.open(io.BytesIO(image_data))
        content = extract_text_from_image(image)
    elif suffix == "csv":
        content = extract_text_from_csv(file.file)
    elif suffix == "db" or suffix == "sqlite3":
        with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as tmp:
            tmp.write(await file.read())
            tmp.flush()
            content = extract_text_from_db(tmp.name)
    else:
        return {"error": "Unsupported file format"}

    file_id = str(uuid.uuid4())
    
    if suffix == "pdf":
        texts = content
        ingest_chunks(texts, file.filename, file_id, page_numbers)
    
    else:
        texts = content
        ingest_chunks(texts, file.filename, file_id)
    
    return {"status": "success", "filename": file.filename, "file_id":file_id}



@app.post("/query/")
async def query_api(request: QueryRequest):
    question = request.question

    if request.image_base64:
        image_data = base64.b64decode(request.image_base64)
        
        question += "Respond based on the below context that is extracted from single or multiple image:\n" + extract_text_from_image(image_data)

        completion = openai_client.chat.completions.create(
        model="gpt-4",
        messages = [
        {
            "role": "system",
            "content": (
                "You are an expert image-based text analyzing assistant. Analyze the image's text content and answer the user's questions elaborately "
                "using only the information provided in the context below."
                "If the answer is not explicitly stated or cannot be confidently inferred, "
                "say 'The answer is not available in the provided image.'"
            )
        },
        {
            "role": "user",
            "content": f"Question: {question}"
        }
        ]
        )
    
        return {
                "context": {"result": completion.choices[0].message.content.strip()}
            }
    else:
        result = ask_question(question)
        return {
        
            "context": result
        }



if __name__ == "__main__":
    host = os.getenv("FASTAPI_HOST", "127.0.0.1")
    port = int(os.getenv("FASTAPI_PORT", 8000))

    uvicorn.run("main:app", host=host, port=port, reload=True)
