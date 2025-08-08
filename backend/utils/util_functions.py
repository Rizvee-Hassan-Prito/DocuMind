import pdfplumber
import pytesseract
from PIL import Image
from docx import Document
import sqlite3
import pandas as pd
import os
import tempfile
import base64, io

import platform
if platform.system() == "Windows":
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe'
else:
    pytesseract.pytesseract.tesseract_cmd = 'tesseract'

def extract_text_from_pdf(file):
    text = ""
    chunks = []
    page_numbers = []
    
    with pdfplumber.open(file) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            text = page.extract_text()
            if not text:
                continue

            chunks.append(text)
            page_numbers.append(page_num)  
    return chunks, page_numbers



def extract_text_from_docx(file):

    file.seek(0)

    docx_bytes = file.read()

    doc = Document(io.BytesIO(docx_bytes))
    return "\n".join([para.text for para in doc.paragraphs])


def extract_text_from_txt(file):
    return file.read().decode("utf-8")


def extract_text_from_image(file):
    
    text = ""
    try:
        img = Image.open(io.BytesIO(file))
        img.verify()
        text = pytesseract.image_to_string(Image.open(io.BytesIO(file)))
    except (IOError, SyntaxError) as e:
        with pdfplumber.open(io.BytesIO(file)) as pdf:
            for page in pdf.pages:
                image = page.to_image(resolution=300).original
                text += pytesseract.image_to_string(image) + "\n"
        
    return text


def extract_text_from_csv(file):
    df = pd.read_csv(file)
    return df.to_string()

def extract_text_from_db(file):
    con = sqlite3.connect(file)
    text = ""
    for table in pd.read_sql("SELECT name FROM sqlite_master WHERE type='table';", con)["name"]:
        df = pd.read_sql_query(f"SELECT * FROM {table}", con)
        text += f"Table: {table}\n" + df.to_string() + "\n"
    con.close()
    return text
