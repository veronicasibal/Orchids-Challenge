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
from webdriver_manager.chrome import ChromeDriverManager
import tempfile
import time
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

app = FastAPI(title="Website Cloning API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CloneRequest(BaseModel):
    url: str

class CloneResponse(BaseModel):
    cloned_html: str
    success: bool
    error_message: str = None

try:
    anthropic_client = anthropic.Anthropic(
        api_key=os.getenv("ANTHROPIC_API_KEY")
    )
    logger.info("Anthropic client initialized successfully")
except Exception as e:
    logger.error(f"Anthropic client initialization failed: {e}")
    anthropic_client = None

def setup_selenium_driver():
    """Set up headless Chrome driver for web scraping"""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    try:
        logger.info("🔧 Setting up Chrome driver with webdriver-manager...")
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        logger.info("Chrome driver setup successful")
        return driver
    except Exception as e:
        logger.error(f"Chrome driver setup failed: {e}")
        try:
            logger.info("Trying fallback Chrome driver setup...")
            driver = webdriver.Chrome(options=chrome_options)
            logger.info("Fallback Chrome driver setup successful")
            return driver
        except Exception as e2:
            logger.error(f"Fallback Chrome driver setup also failed: {e2}")
            raise HTTPException(
                status_code=500, 
                detail=f"Failed to setup Chrome driver. Main error: {str(e)}, Fallback error: {str(e2)}"
            )

def scrape_website_data(url: str) -> dict:
    """Scrape website for design context"""
    driver = None
    screenshot_path = None
    
    try:
        logger.info(f"🌐 Starting to scrape: {url}")
        driver = setup_selenium_driver()
        
        driver.get(url)
        logger.info("📄 Page loaded, waiting for content...")
        time.sleep(5)  # Wait for page to load and JS to execute
        
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        screenshot_path = tempfile.mktemp(suffix='.png')
        success = driver.save_screenshot(screenshot_path)
        logger.info(f"📸 Screenshot saved: {success}")
        
        screenshot_base64 = None
        if os.path.exists(screenshot_path) and os.path.getsize(screenshot_path) > 0:
            with open(screenshot_path, 'rb') as f:
                screenshot_base64 = base64.b64encode(f.read()).decode()
                logger.info(f"🖼️ Screenshot encoded, size: {len(screenshot_base64)} chars")
        
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        
        for script in soup(["script", "style"]):
            script.decompose()
        
        data = {
            'screenshot_base64': screenshot_base64,
            'title': soup.title.string.strip() if soup.title and soup.title.string else 'Untitled',
            'html_structure': str(soup.prettify())[:8000],  # Increased limit
            'text_content': soup.get_text(separator=' ', strip=True)[:3000],  # Increased limit
            'links': [a.get('href') for a in soup.find_all('a', href=True)][:15],
            'images': [img.get('src') for img in soup.find_all('img', src=True)][:15],
            'headings': []
        }
        
        for i in range(1, 7):
            headings = soup.find_all(f'h{i}')
            for heading in headings[:3]:  # Limit to 3 per level
                data['headings'].append({
                    'level': i,
                    'text': heading.get_text(strip=True)
                })
        
        logger.info(f"✅ Successfully scraped data for {url}")
        return data
        
    except Exception as e:
        logger.error(f"Error scraping website: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to scrape website: {str(e)}")
        
    finally:
        if driver:
            driver.quit()
        if screenshot_path and os.path.exists(screenshot_path):
            try:
                os.remove(screenshot_path)
            except Exception as e:
                logger.warning(f"⚠️ Could not remove temp file: {e}")

def generate_html_with_ai(website_data: dict) -> str:
    """Use Claude to generate HTML based on website data"""
    
    if not anthropic_client:
        logger.warning("⚠️ Anthropic client not available, using fallback")
        return create_fallback_html(website_data)
    
    prompt = f"""You are an expert web developer tasked with recreating a website based on scraped data.

Website Information:
- Title: {website_data['title']}

Content Structure:
- Main headings: {website_data.get('headings', [])}
- Text content preview: {website_data['text_content'][:500]}...

Visual Elements:
- Images found: {len(website_data.get('images', []))} images
- Links found: {len(website_data.get('links', []))} links

HTML Structure Sample:
{website_data['html_structure'][:2000]}

Please create a complete, modern HTML page that recreates this website. Requirements:
1. Use semantic HTML5 structure
2. Include comprehensive inline CSS styling
3. Make it responsive and mobile-friendly
4. Use modern web design principles
5. Include proper typography and spacing
6. Add hover effects and smooth transitions
7. Use a professional color scheme
8. Ensure good contrast and readability

Focus on making it visually appealing and functional. Return ONLY the complete HTML code without any explanations or markdown formatting."""

    try:
        logger.info("🤖 Sending request to Claude...")
        response = anthropic_client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=4000,
            temperature=0.3,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )
        
        generated_html = response.content[0].text
        logger.info(f"AI generated HTML, length: {len(generated_html)} chars")
        
        # Basic validation - ensure it's actually HTML
        if not generated_html.strip().startswith('<!DOCTYPE html>') and not generated_html.strip().startswith('<html'):
            logger.warning("⚠️ Generated content doesn't look like HTML, using fallback")
            return create_fallback_html(website_data)
        
        return generated_html
        
    except Exception as e:
        logger.error(f"AI generation failed: {e}")
        return create_fallback_html(website_data)

def create_fallback_html(website_data: dict) -> str:
    """Create fallback HTML if AI fails"""
    headings_html = ""
    for heading in website_data.get('headings', [])[:5]:
        headings_html += f"<h{heading['level']}>{heading['text']}</h{heading['level']}>\n"
    
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{website_data['title']}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f8f9fa;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2rem 0;
            text-align: center;
            margin-bottom: 2rem;
            border-radius: 10px;
        }}
        
        .header h1 {{
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
            font-weight: 700;
        }}
        
        .content {{
            background: white;
            padding: 2rem;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin-bottom: 2rem;
        }}
        
        .content h2 {{
            color: #495057;
            margin-bottom: 1rem;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid #e9ecef;
        }}
        
        .preview-text {{
            background: #f8f9fa;
            padding: 1rem;
            border-radius: 5px;
            font-style: italic;
            margin: 1rem 0;
        }}
        
        @media (max-width: 768px) {{
            .container {{
                padding: 10px;
            }}
            
            .header h1 {{
                font-size: 2rem;
            }}
            
            .content {{
                padding: 1rem;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{website_data['title']}</h1>
            <p>Website Successfully Cloned</p>
        </div>
        
        <div class="content">
            <h2>Website Content</h2>
            {headings_html}
            
            <div class="preview-text">
                <strong>Content Preview:</strong><br>
                {website_data['text_content'][:400]}...
            </div>
        </div>
    </div>
</body>
</html>"""

@app.get("/")
async def root():
    return {
        "message": "Website Cloning API is running!",
        "status": "healthy",
        "anthropic_available": anthropic_client is not None
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "website-cloning-api",
        "anthropic_client": anthropic_client is not None,
        "environment_vars": {
            "ANTHROPIC_API_KEY": bool(os.getenv("ANTHROPIC_API_KEY"))
        }
    }

@app.post("/clone-website", response_model=CloneResponse)
async def clone_website(request: CloneRequest):
    """Main endpoint to clone a website"""
    
    try:
        logger.info(f"Received clone request for: {request.url}")
        
        url = request.url.strip()
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        logger.info(f"Normalized URL: {url}")
        
        website_data = scrape_website_data(url)
        
        cloned_html = generate_html_with_ai(website_data)
        
        logger.info("Website cloning completed successfully")
        return CloneResponse(
            cloned_html=cloned_html,
            success=True
        )
        
    except HTTPException:
        raise  
    except Exception as e:
        logger.error(f"💥 Unexpected error in clone_website: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to clone website: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    print("Starting Website Cloning API...")
    print("Server will be available at: http://localhost:8000")
    print("Test endpoint: http://localhost:8000/clone-website")
    print("API docs: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")