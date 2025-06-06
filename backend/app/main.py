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

app = FastAPI(title = "Website Cloning API") #creates web server

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"],) #allows for frontend/backend data sharing

#data shared should be a url
class CloneRequest(BaseModel):
    url:str

#data recieved should be html text
class CloneResponse(BaseModel):
    cloned_html: str
    success: bool #indicating success

#connects to Claude
anthropic_client = anthropic.Anthropic(api_key=os.getenv("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"))


###WEBSCRAPING###
def setup_selenium_driver(): #function that sets up chrome driver 
    chrome_options = Options()
    chrome_options.add_argument("--headless") #dont show window
    chrome_options.add_argument("--no-sandbox") #remove security restriction to make it easier to run in server
    chrome_options.add_argument("--disable-dev-shm-usage") #prevents memory issues
    chrome_options.add_argument("--window-size=1920,1080") #sets browser window size (avoids problem of different window screen sizes)
    
    return webdriver.Chrome(options=chrome_options) #returns new chrome browser

def scrape_website_data(url: str) -> dict: #main function for scraping!!! returns a dictionary
    driver = setup_selenium_driver() #calls chrome driver from previous function
    try: #first, attempt to visit the url website
        driver.get(url)
        time.sleep(3) #gives time to let website fully load

        # Take screenshot
        screenshot_path = tempfile.mktemp(suffix='.png')
        driver.save_screenshot(screenshot_path)

        # Read screenshot as base64
        with open(screenshot_path, 'rb') as f:
            screenshot_base64 = base64.b64encode(f.read()).decode()

        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        
        # Extract useful information
        return {
            'screenshot_base64': screenshot_base64,
            'title': soup.title.string if soup.title else 'No title',
            'html_structure': str(soup.prettify())[:5000],  # Limit size
            'text_content': soup.get_text()[:2000],  # Limit size
            'links': [a.get('href') for a in soup.find_all('a', href=True)][:10],
            'images': [img.get('src') for img in soup.find_all('img', src=True)][:10],
        }
        
    finally:
        driver.quit()
        # Clean up screenshot file
        if os.path.exists(screenshot_path):
            os.remove(screenshot_path)












@app.get("/")
def read_root():
    return {"message": "Hello World"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
