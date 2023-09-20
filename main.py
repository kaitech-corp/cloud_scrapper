from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import uvicorn
import os
from pydantic import BaseModel
from typing import List
from scrape import Scrape
from gpt import GPT
from storage import Storage
from utils import validate_url, create_json

app = FastAPI()

templates=Jinja2Templates(directory="templates")

class Urls(BaseModel):
    urls: List[str]

@app.post("/scrape")
async def scrape(urls: Urls):
    for url in urls.urls:
        if not validate_url(url):
            raise HTTPException(status_code=400, detail="Invalid URL")

    scraper = Scrape()
    gpt = GPT()
    storage = Storage()

    for url in urls.urls:
        try:
            title, content = scraper.scrape(url)
            date_posted = scraper.scrape_posted_date(url)
            tags = gpt.generate_tags(content)
            summary = gpt.generate_summary(content)
            json_obj = create_json(title, content, summary, tags, date_posted, url)
            storage.store(json_obj)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    return {"message": "Scraping completed successfully", "tags": tags, "json": json_obj}

@app.get('/', response_class=HTMLResponse)
async def hello(request: Request):
    """Return a friendly HTTP greeting."""
    message="It's running!"


    return templates.TemplateResponse("index.html", {"request": request, "message": message,})


# Execute the application when the script is run
if __name__ == "__main__":
    # Get the server port from the environment variable
    server_port=os.environ.get("PORT", "8080")

    # Run the FastAPI application
    uvicorn.run(app, host="0.0.0.0", port=int(server_port))
