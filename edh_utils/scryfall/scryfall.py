import time
from typing import Generic, TypeVar

import requests
from pydantic import BaseModel

from edh_utils.logging import logger

SEARCH_URL = "https://api.scryfall.com/cards/search"

log = logger()

T = TypeVar("T")


class CardNotFound(BaseModel):
    query: str


class ScryfallResult(BaseModel, Generic[T]):
    error: CardNotFound | None = None
    payload: T | None = None


def search(query: str) -> ScryfallResult[list[dict]]:
    """Search the Scryfall API and return all matching cards across all pages.

    Handles pagination automatically. Waits 100ms after each request to
    respect Scryfall's rate limit guidelines. Returns a ScryfallResult with
    a CardNotFound error on 404.
    """
    results = []
    url = SEARCH_URL
    params: dict | None = {"q": query, "format": "json"}
    page = 0

    while url:
        page += 1
        log.debug(f"Searching Scryfall: query={query!r} page={page}")
        response = requests.get(url, params=params)
        try:
            response.raise_for_status()
        except requests.HTTPError as e:
            if e.response.status_code == 404:
                return ScryfallResult(error=CardNotFound(query=query))
            raise
        time.sleep(0.1)

        data = response.json()
        results.extend(data.get("data", []))

        url = data.get("next_page")
        params = None  # next_page URL already includes query params

    log.debug(f"Scryfall search complete: query={query!r} pages={page} total_results={len(results)}")
    return ScryfallResult(payload=results)
