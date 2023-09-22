import requests
from bs4 import BeautifulSoup

def scrape_blog_urls(base_url, num_pages=10):
    blog_urls = []
    
    for page_number in range(1, num_pages + 1):
        page_url = f"{base_url}/page/{page_number}"
        response = requests.get(page_url)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Assuming that the blog post URLs are in anchor (a) tags with a specific class
            post_links = soup.find_all('a', class_='your-blog-link-class')
            
            for link in post_links:
                blog_urls.append(link['href'])
        else:
            print(f"Failed to retrieve data from page {page_number}. Status Code: {response.status_code}")
    
    return blog_urls

# Specify the base URL of the blog
base_blog_url = "https://neptune.ai/blog"

# Specify the number of pages to scrape (default is 10)
num_pages_to_scrape = 10

# Call the function to scrape blog URLs
blog_urls = scrape_blog_urls(base_blog_url, num_pages_to_scrape)

# Print the scraped blog URLs
for url in blog_urls:
    print(url)
