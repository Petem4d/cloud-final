import vertexai
from vertexai.preview.generative_models import GenerativeModel
from google.genai.types import HttpOptions, Part
from google import genai
from fastapi import FastAPI, Form, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
# from typing import Annotated
# import datetime
from starlette.responses import FileResponse 
from google.cloud import firestore
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import os
from typing import List
import uuid
from bs4 import BeautifulSoup
import re


app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="template")



def extract_text_from_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    

    for element in soup(['script', 'style', 'head', 'title', 'meta', 'link', 'noscript', 'header', 'footer']):
        element.decompose()
    
    text = soup.get_text(separator=' ', strip=True)
    
    text = re.sub(r'\s+', ' ', text)
    
    for br in soup.find_all(['br', 'p', 'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li']):
        br.append('\n')
    
    text_with_breaks = soup.get_text(separator=' ', strip=True)
    
    text_with_breaks = re.sub(r'\n+', '\n', text_with_breaks)
    text_with_breaks = re.sub(r'\s+\n', '\n', text_with_breaks)
    text_with_breaks = re.sub(r'\n\s+', '\n', text_with_breaks)
    
    return text_with_breaks.strip()


db = firestore.Client()
syllabus_collection = db.collection("syllabi")

@app.get("/")
async def read_root(request: Request):
  return templates.TemplateResponse(request= request, name = "index.html")


@app.post("/chat")
async def chat_upload(files: List[UploadFile] = File(...)):

    for file in files:

        content = await file.read()
        # file_responses.append({
        #     "filename": file.filename,
        #     "saved_as": unique_filename,
        #     "content_type": file.content_type,
        #     "size": len(content)
        # })
        
        content = extract_text_from_html(content)        
        client = genai.Client(vertexai= True, project = "cloud-agent-457418", location = "us-central1", http_options=HttpOptions(api_version="v1"))
        model_id = "gemini-2.0-flash-001"
        prompt = """
        You are a highly skilled document summarization specialist.
        You will be receiving a college syllabus. Your job is to summarize the syllabus in under 300 words.
        Be sure to include the grading scale and any important dates or assignments.
        The first line of your response should be the class name.
        The second line should be the teacher's name
        The rest of the response should be the formatted summary.
        If the document does not appear to be a syllabus, respond "NOT A SYLLABUS"
        """
        
        response = client.models.generate_content(
            model=model_id,
            contents=[content, prompt],
        )
        class_name = response.text.splitlines()[0]
        teacher = response.text.splitlines()[1]
        description = response.text.split("\n",2)[2]
        if(response != "NOT A SYLLABUS"):
            syllabus_collection.add({
                "class": class_name,
                "teacher": teacher,
                "description": description
            })
        
        return response.text

@app.get("/syllabi")
async def read_root(request: Request):
    all_syllabi = syllabus_collection.stream()
    response_list = []
    for doc in all_syllabi:
        response = "CLASS: " + doc.to_dict()["class"] + "\nTeacher: " + doc.to_dict()["teacher"] + doc.to_dict()["description"] + "\n\n"
        response_list.append(response)
    return response_list


