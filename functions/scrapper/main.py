
import functions_framework
from gpt import GPT
from scrape import Scrape
from storage import Storage
from utils import create_json, validate_url

@functions_framework.http
def process_url(request):
    # Parse the incoming JSON data
    request_json = request.get_json()

    if "url" not in request_json:
        return "Error: 'url' parameter is missing from the request.", 400

    url = request_json["url"]
    if not validate_url(url):
        return "Error: 'url' parameter is not valid.", 400

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

        return f'Url has been processed.'
    except Exception as e:
        print(e)
        return f'Did not process link. {e}'