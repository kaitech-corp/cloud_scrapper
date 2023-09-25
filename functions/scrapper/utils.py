from urllib.parse import urlparse
import json
import datetime
import re

def validate_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False

def create_json(title, content, summary, tags, date_posted, url):
    json_obj = {
        'id': str(datetime.datetime.now()),
        'title': title,
        'content': content,
        'summary': summary,
        'tags': tags,
        'current_date': str(datetime.datetime.now()),
        'date_posted': str(date_posted),
        'url': url
    }
    print(json_obj)

    return json.dumps(json_obj)

def remove_unwanted_characters(text):
    # Define a regular expression pattern to match unwanted characters
    pattern = r'\\[a-zA-Z0-9]+'

    # Use re.sub to replace matched patterns with an empty string
    cleaned_text = re.sub(pattern, '', text)

    return cleaned_text