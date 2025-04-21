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

# mount static files
#app.mount("/static", StaticFiles(directory="/app/static"), name="static")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="template")

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def extract_text_from_html(html_content):
    """
    Extract only the visible text content from an HTML string.
    
    Args:
        html_content (str): Raw HTML content to parse
        
    Returns:
        str: Extracted visible text with preserved paragraph structure
    """
    # Parse the HTML with BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Remove script, style, head, and other non-visible elements
    for element in soup(['script', 'style', 'head', 'title', 'meta', 'link', 'noscript', 'header', 'footer']):
        element.decompose()
    
    # Get text and handle whitespace
    text = soup.get_text(separator=' ', strip=True)
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Handle line breaks for better readability
    for br in soup.find_all(['br', 'p', 'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li']):
        br.append('\n')
    
    # Get text with line breaks
    text_with_breaks = soup.get_text(separator=' ', strip=True)
    
    # Clean up multiple line breaks
    text_with_breaks = re.sub(r'\n+', '\n', text_with_breaks)
    text_with_breaks = re.sub(r'\s+\n', '\n', text_with_breaks)
    text_with_breaks = re.sub(r'\n\s+', '\n', text_with_breaks)
    
    return text_with_breaks.strip()


db = firestore.Client()
syllabus_collection = db.collection("syllabi")

@app.get("/")
async def read_root(request: Request):

  #  return FileResponse('index.html')
  return templates.TemplateResponse(request= request, name = "index.html")


@app.post("/chat")
async def chat_upload(files: List[UploadFile] = File(...)):
    file_responses = []

    # Process each uploaded file
    for file in files:
        # Generate a unique filename to prevent overwrites
        
        #file_ext = os.path.splitext(file.filename)[1]
        #unique_filename = f"{uuid.uuid4()}{file_ext}"
        #file_path = os.path.join(UPLOAD_DIR, unique_filename)
        
        # Save the file
        content = await file.read()
        # with open(file_path, "wb") as f:
        #     f.write(content)
        
        # # Add file info to response
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
        You will be receiving a college syllabus. Your job is to summarize the syllabus in under 400 words.
        Be sure to include the grading scale and any important dates or assignments.
        """
        
        response = client.models.generate_content(
            model=model_id,
            contents=[content, prompt],
        )

        print(response.text)
        syllabus_collection.add({
            "filename": file.filename,
            "description": response.text
        })
        return response.text





