from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import uvicorn
import os
import asyncio
import requests
from pydantic import BaseModel
from typing import List
from starlette.middleware.cors import CORSMiddleware
from google.cloud import pubsub_v1
from concurrent.futures import TimeoutError, ThreadPoolExecutor

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
            process_url_with_cloud_function(url)
            message.ack()
            print(f"Processed message from Pub/Sub. Link: {url}")
            
        except Exception as e:
            url = message.data.decode("utf-8")
            print(f"Error processing message: {str(e)}. Link: {url}")

    # Subscribe to the Pub/Sub subscription and start listening
    subscription_path = subscriber_client.subscription_path(
        f"{project_id}", "scrape_sub"
    )
    streaming_pull_future = subscriber_client.subscribe(
        subscription_path, callback=callback
    )
    # Keep the function running to continue processing messages
    # Wrap subscriber in a 'with' block to automatically call close() when done.
    # with subscriber_client:
        # try:
            # When `timeout` is not set, result() will block indefinitely,
            # unless an exception is encountered first.
    await streaming_pull_future.result()
        # except TimeoutError:
        #     streaming_pull_future.cancel()  # Trigger the shutdown.
        #     streaming_pull_future.result()  # Block until the shutdown is complete.



def process_url_with_cloud_function(url):
    # Define the Cloud Function URL
    cloud_function_url = "https://scrapper-xaoktxu34q-uc.a.run.app"

    # Define the input data as a dictionary
    data = {
        "url": url
    }

    try:
        # Send a POST request to the Cloud Function
        response = requests.post(cloud_function_url, json=data)

        # Check the response
        if response.status_code == 200:
            # Request was successful
            # result = response.json()
            return "Result Successful"
        else:
            # Request encountered an error
            return {"error": f"Error {response.status_code}: {response.text}"}
    except Exception as e:
        # Handle any exceptions that may occur during the request
        return {"error": f"An error occurred: {str(e)}"}


@app.post("/scrape")
async def scrape(urls: Urls):
    # Send each URL as a message to Pub/Sub
    for url in urls.urls:
        send_message_to_pubsub(url)
        # print("Link: " + url)

    return {"message": "URLs queued for scraping"}

@app.get('/', response_class=HTMLResponse)
async def hello(request: Request):
    """Return a friendly HTTP greeting."""
    message = "It's running!"

    return templates.TemplateResponse("index.html", {"request": request, "message": message, })


# Function to start the FastAPI application
def start_fastapi_server():
    # Get the server port from the environment variable
    server_port = os.environ.get("PORT", "8080")

    # Run the FastAPI application
    uvicorn.run(app, host="0.0.0.0", port=int(server_port))

if __name__ == "__main__":
    # Create a ThreadPoolExecutor to run the FastAPI server and Pub/Sub message processing concurrently
    with ThreadPoolExecutor(max_workers=2) as executor:
        # Start the FastAPI server in one thread
        executor.submit(start_fastapi_server)

        # Start Pub/Sub message processing in another thread
        asyncio.run(process_pubsub_messages())
