from dotenv import load_dotenv
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Any, List
from pathlib import Path
import google.generativeai as genai
from PyPDF2 import PdfReader
import os,io
from langchain.prompts import PromptTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain.chains.question_answering import load_qa_chain
from langchain_community.vectorstores import FAISS
from fastapi.responses import JSONResponse

# Load environment variables from .env file (if any)
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

UPLOAD_DIR = Path() / 'uploads'


class Response(BaseModel):
    result: str | None

origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:3000"
]

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_pdf_text(pdf_docs):
    text=""
    for pdf in pdf_docs:
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text

def get_text_chunks(text):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000,chunk_overlap=1000)
    chunks = text_splitter.split_text(text)
    return chunks

def get_vector_store(text_chunks):
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    vector_store = FAISS.from_texts(text_chunks,embedding=embeddings)
    vector_store.save_local("faiss_index")

def get_conversational_chain():
     prompt_template = """
     Answer the question as detailed as possible from the provided context, make sure to provide all the details, if the answer is not in the
     provided context just say, "answer is not available in the context", don't provide the wrong answer\n\n
     Context:\n {context}?\n
     Question:\n {question}\n

     Answer:
     """
     model = ChatGoogleGenerativeAI(model="gemini-pro",temperature=0.5)

     prompt = PromptTemplate(template=prompt_template, input_variables=["context","question"])
     chain = load_qa_chain(model,chain_type="stuff",prompt=prompt)
     return chain

def user_input(user_question):
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

    new_db = FAISS.load_local("faiss_index",embeddings)
    docs = new_db.similarity_search(user_question)

    chain = get_conversational_chain()

    response = chain(
        {"input_documents":docs, "question": user_question}
        , return_only_outputs=True)
        
    return response["output_text"]

@app.post("/predict", response_model = Response)
async def predict(file: UploadFile = File(...),question: str = Form(...)) -> Any:
    content = await file.read()
    save_to = UPLOAD_DIR/file.filename
    with open(save_to, 'wb') as f:
        f.write(content)
    ans = file.filename
    if file.filename.endswith('.pdf'):
        raw_text = get_pdf_text(content)
        text_chunks = get_text_chunks(raw_text)
        get_vector_store(text_chunks)
        ans = user_input(question)
    return {"result": ans}