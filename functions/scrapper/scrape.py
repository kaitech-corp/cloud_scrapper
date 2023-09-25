from bs4 import BeautifulSoup
import dateutil.parser as dparser
import requests

from utils import remove_unwanted_characters

class Scrape:
    def scrape(self, url):
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.title.string
        content = soup.get_text(strip=True)
        cleaned_content = remove_unwanted_characters(content)

        return title, cleaned_content


    def scrape_posted_date(self, url):
        try:
            # Send an HTTP GET request to the URL
            response = requests.get(url)
            
            # Check if the request was successful
            if response.status_code == 200:
                # Parse the HTML content of the page using BeautifulSoup
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Search for common HTML tags that often contain post dates
                date_elements = soup.find_all(['time', 'span', 'div', 'p'], {'class': ['date', 'post-date']})
                
                # Extract the date text from the elements found
                date_text = ""
                for element in date_elements:
                    date_text += element.get_text() + " "
                
                # Attempt to parse the date using dateutil.parser
                parsed_date = dparser.parse(date_text, fuzzy=True)
                
                if parsed_date:
                    return parsed_date.strftime("%Y-%m-%d %H:%M:%S")
                else:
                    return "Date not found"
            else:
                return "HTTP request failed"
        except Exception as e:
            return str(e)
