import time

import requests

SEARCH_URL = "https://api.scryfall.com/cards/search"


def search(query: str) -> list[dict]:
    """Search the Scryfall API and return all matching cards across all pages.

    Handles pagination automatically. Waits 100ms after each request to
    respect Scryfall's rate limit guidelines.
    """
    results = []
    url = SEARCH_URL
    params: dict | None = {"q": query, "format": "json"}

    while url:
        response = requests.get(url, params=params)
        response.raise_for_status()
        time.sleep(0.1)

        data = response.json()
        results.extend(data.get("data", []))

        url = data.get("next_page")
        params = None  # next_page URL already includes query params

    return results
