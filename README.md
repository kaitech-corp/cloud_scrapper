Core classes, functions, and methods:

1. `main.py`: Entry point of our application. Contains the FastAPI app instance and the API endpoint definitions.

2. `scrape.py`:  `Scrape` class, handles the scraping of the webpages.

3. `gpt.py`:  `GPT` class, handles the generation of tags using the ChatGPT API.

4. `storage.py`: `Storage` class, handles the storage of the JSON object in the cloud storage bucket.

5. `utils.py`: This file contains utility functions such as `validate_url` for URL validation and `create_json` for creating the JSON object.

6. `test_main.py`: Test cases for the application.

7. `Dockerfile`: This file contains the instructions to build the Docker image for our application.

8. `requirements.txt`: Lists all the Python dependencies needed for the application.


