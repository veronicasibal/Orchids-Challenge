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
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import tempfile
import time

# Load environment variables
load_dotenv()

app = FastAPI(title="Website Cloning API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class CloneRequest(BaseModel):
    url: str

class CloneResponse(BaseModel):
    cloned_html: str
    success: bool

# Initialize Anthropic client
try:
    anthropic_client = anthropic.Anthropic(
        api_key=os.getenv("ANTHROPIC_API_KEY")
    )
except Exception as e:
    print(f"Warning: Anthropic client initialization failed: {e}")
    anthropic_client = None

def setup_selenium_driver():
    """Set up headless Chrome driver for web scraping"""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    
    try:
        # Try to create driver with automatic driver management
        driver = webdriver.Chrome(options=chrome_options)
        return driver
    except Exception as e:
        print(f"Error setting up Chrome driver: {e}")
        raise HTTPException(status_code=500, detail="Failed to setup web browser")

def scrape_website_data(url: str) -> dict:
    """Scrape website for design context"""
    driver = setup_selenium_driver()
    
    try:
        # Navigate to the website
        driver.get(url)
        time.sleep(3)  # Wait for page to load
        
        # Take screenshot
        screenshot_path = tempfile.mktemp(suffix='.png')
        driver.save_screenshot(screenshot_path)
        
        # Read screenshot as base64
        with open(screenshot_path, 'rb') as f:
            screenshot_base64 = base64.b64encode(f.read()).decode()
        
        # Get page source and parse with BeautifulSoup
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

def generate_html_with_ai(website_data: dict) -> str:
    """Use Claude to generate HTML based on website data"""
    
    if not anthropic_client:
        # Return fallback HTML if Anthropic client is not available
        return create_fallback_html(website_data)
    
    prompt = f"""
You are an expert web developer. I need you to recreate a website based on the following information:

Website Title: {website_data['title']}

Text Content: {website_data['text_content']}

HTML Structure Sample: {website_data['html_structure']}

Links found: {website_data['links']}

Images found: {website_data['images']}

Please generate a complete HTML page that recreates this website as closely as possible. Include:
1. Proper HTML5 structure
2. Inline CSS styling to match the design
3. Responsive design principles
4. Professional styling and layout

Make it look modern and visually appealing. Return only the HTML code, no explanations.
"""

    try:
        response = anthropic_client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=4000,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )
        
        return response.content[0].text
        
    except Exception as e:
        print(f"AI generation failed: {e}")
        return create_fallback_html(website_data)

def create_fallback_html(website_data: dict) -> str:
    """Create fallback HTML if AI fails"""
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{website_data['title']}</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
            .container {{ max-width: 800px; margin: 0 auto; }}
            h1 {{ color: #333; border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
            .content {{ background: #f9f9f9; padding: 20px; border-radius: 8px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>{website_data['title']}</h1>
            <div class="content">
                <p>This is a recreated version of the website. The AI service encountered an error, so this is a simplified version.</p>
                <p>Original content preview: {website_data['text_content'][:200]}...</p>
            </div>
        </div>
    </body>
    </html>
    """

@app.get("/")
async def root():
    return {"message": "Website Cloning API is running!"}

@app.post("/clone-website", response_model=CloneResponse)
async def clone_website(request: CloneRequest):
    """Main endpoint to clone a website"""
    
    try:
        # Validate URL
        if not request.url.startswith(('http://', 'https://')):
            request.url = 'https://' + request.url
        
        # Scrape website data
        website_data = scrape_website_data(request.url)
        
        # Generate HTML with AI
        cloned_html = generate_html_with_ai(website_data)
        
        return CloneResponse(
            cloned_html=cloned_html,
            success=True
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to clone website: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)