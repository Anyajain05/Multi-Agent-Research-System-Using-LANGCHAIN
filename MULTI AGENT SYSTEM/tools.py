from langchain.tools import tool
import requests
from bs4 import BeautifulSoup
from tavily import TavilyClient
import os
from dotenv import load_dotenv
load_dotenv()

tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))


def search_web_raw(query: str, max_results: int = 5) -> list[dict]:
    """Return raw Tavily results with defensive error handling."""
    try:
        results = tavily.search(query=query, max_results=max_results)
        return results.get("results", [])
    except Exception:
        return []


def format_search_results(results: list[dict]) -> str:
    """Format Tavily search results into the text block expected by the pipeline."""
    out = []
    for r in results:
        title = r.get("title", "Untitled")
        url = r.get("url", "")
        snippet = (r.get("content") or "")[:300]
        out.append(f"Title: {title}\nURL: {url}\nSnippet: {snippet}\n")
    return "\n----\n".join(out)


def scrape_url_raw(url: str, timeout: int = 8) -> str:
    """Scrape a URL and return cleaned text, or a short failure message."""
    try:
        resp = requests.get(url, timeout=timeout, headers={"User-Agent": "Mozilla/5.0"})
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer"]):
            tag.decompose()
        text = soup.get_text(separator=" ", strip=True)
        if not text:
            return "Could not scrape URL: no readable text found"
        return text[:3000]
    except Exception as e:
        return f"Could not scrape URL: {str(e)}"

@tool
def web_search(query : str) -> str:
    """Search the web for recent and reliable information on a topic . Returns Titles , URLs and snippets."""
    results = search_web_raw(query=query, max_results=5)
    return format_search_results(results)

@tool
def scrape_url(url: str) -> str:
    """Scrape and return clean text content from a given URL for deeper reading."""
    return scrape_url_raw(url=url, timeout=8)