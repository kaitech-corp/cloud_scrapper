from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import uvicorn
import os
import asyncio
from pydantic import BaseModel
from typing import List
from scrape import Scrape
from gpt import GPT
from storage import Storage
from utils import validate_url, create_json
from starlette.middleware.cors import CORSMiddleware
from google.cloud import pubsub_v1
from concurrent.futures import TimeoutError

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins='*',
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="templates")


class Urls(BaseModel):
    urls: List[str]


# Create Pub/Sub clients
publisher_client = pubsub_v1.PublisherClient()
subscriber_client = pubsub_v1.SubscriberClient()

# Project ID
project_id = "api-project-371618"
# Define the Pub/Sub topic name
topic_name = f"projects/{project_id}/topics/scrape-topic"

# Define the Pub/Sub subscription name
subscription_name = "projects/api-project-371618/subscriptions/scrape_sub"


# Message publisher
def send_message_to_pubsub(url):
    data = url.encode("utf-8")
    future = publisher_client.publish(topic_name, data)
    print(f"Published message to Pub/Sub: {future.result()}, data: {data}")

# Message subscriber
async def process_pubsub_messages():
    def callback(message):
        try:
            # Process the URL from the received message
            url = message.data.decode("utf-8")
            print(url)
            process_url(url)
            message.ack()
            print(f"Processed message from Pub/Sub")
        except Exception as e:
            print(f"Error processing message: {str(e)}")

    # Subscribe to the Pub/Sub subscription and start listening
    subscription_path = subscriber_client.subscription_path(
        f"{project_id}", "scrape_sub"
    )
    streaming_pull_future = subscriber_client.subscribe(
        subscription_path, callback=callback
    )
    timeout = 5.0
    # Keep the function running to continue processing messages
    # Wrap subscriber in a 'with' block to automatically call close() when done.
    with subscriber_client:
        try:
            # When `timeout` is not set, result() will block indefinitely,
            # unless an exception is encountered first.
            streaming_pull_future.result(timeout=timeout)
        except TimeoutError:
            streaming_pull_future.cancel()  # Trigger the shutdown.
            streaming_pull_future.result()  # Block until the shutdown is complete.


@app.post("/scrape")
async def scrape(urls: Urls):
    if not urls:
        raise HTTPException(status_code=400, detail="Invalid URL")

    # Send each URL as a message to Pub/Sub
    for url in urls.urls:
        send_message_to_pubsub(url)

    return {"message": "URLs queued for scraping"}

# Function to process the url


async def process_url(url):
    if not validate_url(url):
        print(e)
        raise HTTPException(status_code=400, detail="Invalid URL")

    try:
        scraper = Scrape()  # Create a new instance of Scraper inside the coroutine
        gpt = GPT()  # Create a new instance of GPT inside the coroutine
        storage = Storage()  # Create a new instance of Storage inside the coroutine

        title, content = scraper.scrape(url)
        date_posted = scraper.scrape_posted_date(url)
        tags = gpt.generate_tags(content)
        summary = gpt.generate_summary(content)
        json_obj = create_json(
            title, content, summary, tags, date_posted, url)
        storage.store(json_obj)
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))


# @app.post("/scrape")
# async def scrape(urls: Urls):
#     for url in urls.urls:
#         if not validate_url(url):
#             raise HTTPException(status_code=400, detail="Invalid URL")

#     scraper = Scrape()
#     gpt = GPT()
#     storage = Storage()

#     for url in urls.urls:
#         try:
#             title, content = scraper.scrape(url)
#             date_posted = scraper.scrape_posted_date(url)
#             tags = gpt.generate_tags(content)
#             summary = gpt.generate_summary(content)
#             json_obj = create_json(
#                 title, content, summary, tags, date_posted, url)
#             storage.store(json_obj)
#         except Exception as e:
#             raise HTTPException(status_code=500, detail=str(e))

#     return {"message": "Scraping completed successfully",
#             "tags": tags,
#             "json": json_obj,
#             "title": title,
#             "content": content,
#             "summary": summary}


@app.get('/', response_class=HTMLResponse)
async def hello(request: Request):
    """Return a friendly HTTP greeting."""
    message = "It's running!"

    return templates.TemplateResponse("index.html", {"request": request, "message": message, })


# Execute the application when the script is run
if __name__ == "__main__":
    # Get the server port from the environment variable
    server_port = os.environ.get("PORT", "8080")

    # Run the FastAPI application
    uvicorn.run(app, host="0.0.0.0", port=int(server_port))
    process_pubsub_messages()
