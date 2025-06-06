from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
from bs4 import BeautifulSoup
import anthropic
import os
from dotenv import load_dotenv
import base64
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import tempfile
import time

###new libraries imported: 
#1. CORS (communicate front and backend)
#2. basemodel (defines whata data should look like)
#3. requests (web requests)
#4. beautifulsoup (webscraping tool, analyzes the html code)
#5. anthropic: (claude) AI of choice
#6. load_dotenv: reads secret info
#7. base64: converts images to texts to easily send
#8. selenium: controls real web automatically
#9. tempfile: creates temp file that gets deleted automatically
#10. time: pause certain amounts of time

load_dotenv()

app = FastAPI(title = "Website Cloning API")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"],)


class CloneRequest(BaseModel):
    url:str

class CloneResponse(BaseModel):
    cloned_html: str
    success: bool

anthropic_client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


















@app.get("/")
def read_root():
    return {"message": "Hello World"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
