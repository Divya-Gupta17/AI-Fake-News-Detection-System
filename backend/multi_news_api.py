


# multi_news_api.py
import requests
from config import Config

def fetch_all_sources(query: str = "breaking news", limit: int = 20):
    key = Config.NEWS_API_KEY
    if not key:
        print("No NEWS_API_KEY set - fetch_all_sources returning empty list.")
        return []

    url = "https://newsapi.org/v2/everything"
    params = {
        "q": query or "breaking news",
        "pageSize": min(limit, 100),
        "apiKey": key,
        "sortBy": "publishedAt",
        "language": "en"
    }
    try:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        payload = r.json()
        items = payload.get("articles", []) or []
        out = []
        for it in items:
            out.append({
                "title": it.get("title"),
                "description": it.get("description"),
                "content": it.get("content"),
                "url": it.get("url"),
                "image_url": it.get("urlToImage"),
                "source": (it.get("source") or {}).get("name", "Unknown"),
                "published_at": it.get("publishedAt")
            })
        return out
    except Exception as e:
        print("Error fetching news from NewsAPI:", e)
        return []

