import os
import requests
from dotenv import load_dotenv

load_dotenv()


class APIClient:
    def __init__(self):
        self.base_url = os.getenv("BASE_URL")
        self.default_headers = {
            "api-key": os.getenv("API_KEY"),
            "authorization": f"Bearer {os.getenv('BEARER_TOKEN')}",
            "origin": os.getenv("ORIGIN"),
        }

    def get(self, endpoint, params=None):
        url = f"{self.base_url}{endpoint}"
        response = requests.get(url, headers=self.default_headers, params=params)
        response.raise_for_status()
        return response.json()

    def post(self, endpoint, data=None, json=None):
        url = f"{self.base_url}{endpoint}"
        response = requests.post(
            url, headers=self.default_headers, data=data, json=json
        )
        response.raise_for_status()
        return response.json()
