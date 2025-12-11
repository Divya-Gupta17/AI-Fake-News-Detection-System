# import requests
# from .config import Config

# def fetch_news_from_api(query, sources=None, page_size=20):
#     """
#     Fetches news from NewsAPI.org based on query and optional sources.
#     """
#     api_key = Config.NEWS_API_KEY
#     if not api_key or api_key == 'YOUR_NEWS_API_KEY':
#         print("NewsAPI key not set. Returning dummy news.")
#         return [
#             {"title": "Dummy News: Great breakthroughs in AI!", "description": "AI models are becoming super intelligent.", "content": "Full text about amazing AI advancements. Source: Example Inc.", "url": "http://example.com/ai-breakthrough", "source_name": "Example News"},
#             {"title": "Dummy News: Local Elections rigged!", "description": "Unsubstantiated claims about election fraud.", "content": "Claims of election rigging circulating without evidence. Source: Gossip Blog.", "url": "http://example.com/election-fraud", "source_name": "Conspiracy Today"},
#         ]

#     base_url = "https://newsapi.org/v2/everything"
#     params = {
#         'q': query,
#         'language': 'en',
#         'sortBy': 'relevancy', # or 'publishedAt' for truly live
#         'apiKey': api_key,
#         'pageSize': page_size
#     }

#     if sources:
#         # NewsAPI expects a comma-separated string of source IDs
#         params['sources'] = ",".join(sources)

#     try:
#         response = requests.get(base_url, params=params)
#         response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
#         data = response.json()
        
#         articles = []
#         for article in data.get('articles', []):
#             # Ensure essential fields exist
#             if all(key in article and article[key] for key in ['title', 'description', 'content', 'url', 'source']):
#                 articles.append({
#                     'title': article['title'],
#                     'description': article['description'],
#                     'content': article['content'],
#                     'url': article['url'],
#                     'source_name': article['source']['name'] # Extract source name
#                 })
#         return articles
#     except requests.exceptions.RequestException as e:
#         print(f"Error fetching news from NewsAPI: {e}")
#         return []



# import requests
# from config import Config

# def fetch_news_from_api(query="india", page_size=12, sources=None):
#     """
#     Uses NewsAPI 'everything' endpoint. Requires NEWS_API_KEY.
#     """
#     url = "https://newsapi.org/v2/everything"
#     params = {
#         "q": query,
#         "pageSize": page_size,
#         "language": "en",
#         "sortBy": "publishedAt",
#         "apiKey": Config.NEWS_API_KEY
#     }
#     if sources:
#         params["sources"] = ",".join(sources)

#     r = requests.get(url, params=params, timeout=15)
#     r.raise_for_status()
#     payload = r.json()

#     articles = []
#     for a in payload.get("articles", []):
#         articles.append({
#             "title": a.get("title") or "",
#             "description": a.get("description") or "",
#             "content": a.get("content") or "",
#             "url": a.get("url") or "",
#             "source_name": (a.get("source") or {}).get("name") or ""
#         })
#     return articles




import requests
from config import Config

def fetch_news_from_api(topics=None, sources=None, page_size=12):
    """
    Fetch live news from NewsAPI using:
    - Multiple topics as OR queries
    - Optional specific sources
    """

    # If no topics selected → default trending news
    if not topics:
        query = "latest news"
    else:
        query = " OR ".join(topics)

    url = "https://newsapi.org/v2/everything"
    params = {
        "q": query,
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": page_size,
        "apiKey": Config.NEWS_API_KEY
    }

    if sources:
        params["sources"] = ",".join(sources)

    try:
        r = requests.get(url, params=params, timeout=15)
        r.raise_for_status()
        data = r.json()

        articles = []
        for a in data.get("articles", []):
            articles.append({
                "title": a.get("title") or "",
                "description": a.get("description") or "",
                "content": a.get("content") or "",
                "url": a.get("url") or "",
                "image_url": a.get("urlToImage") or "",
                "source": (a.get("source") or {}).get("name") or "",
                "published_at": a.get("publishedAt") or ""
            })
        return articles

    except Exception as e:
        print("NewsAPI error:", e)
        return []

