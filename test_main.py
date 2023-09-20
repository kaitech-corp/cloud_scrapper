from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_scrape():
    response = client.post(
        "/scrape/",
        json={"urls": ["https://www.google.com"]},
    )
    assert response.status_code == 200
    assert response.json() == {"message": "Scraping completed successfully"}
