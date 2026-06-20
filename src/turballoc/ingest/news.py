import datetime as dt
import pandas as pd
import requests
from turballoc.config import settings
from turballoc.logging_utils import get_logger

logger = get_logger(__name__)

timeout = 20
gdelt_url = "https://api.gdeltproject.org/api/v2/doc/doc"
newsapi_url = "https://newsapi.org/v2/everything"
def_query = "stock market OR inflation OR recession OR interest rates"

columns = ["title", "source", "url"]

def _empty():
    idx = pd.DatetimeIndex([], name="date")
    return pd.DataFrame({c: pd.Series(dtype = "object") for c in columns}, index = idx)

def fetch_news(query = def_query, timespan = "7d", maxrecords = 200):
    "Fetch recent finance headlines"
    if settings.newsapi_key:
        return fetch_newsapi(query, maxrecords)
    return fetch_gdelt(query, timespan, maxrecords)

def fetch_gdelt(query, timespan, maxrecords):
    params = {"query": query, "mode": "ArtList", "format": "json",
              "maxrecords": int(maxrecords), "timespan": timespan, "sort": "DateDesc"}
    try:
        resp = requests.get(gdelt_url, params = params, timeout = timeout)
        resp.raise_for_status()
        articles = resp.json().get("articles", [])
    except (requests.RequestException, ValueError) as e:
        logger.warning("GDELT fetch failed: %s", e)
        return _empty()
    if not articles:
        logger.warning("GDELT returned no articles for query %r", query)
        return _empty()
    rows = []
    for a in articles:
        rows.append({"date": parse_gdelt_date(a.get("seendate")),
                     "title": a.get("title"), "source": a.get("domain"),
                     "url": a.get("url")})
        return frame(rows)
    
def fetch_newsapi(query, maxrecords):
    params = {"q": query, "language": "en", "sprtBy": "publishedAt", "pageSize": min(int(maxrecords), 100), "apiKey": settings.newsapi_key}
    try:
        resp = requests.get(newsapi_url, params = params, timeout = timeout)
        resp.raise_for_status()
        articles = resp.json().get("articles", [])
    except (requests.RequestException, ValueError) as e:
        logger.warning(f"NewsAPI fetch failed: {e}")
        return _empty()
    if not articles:
        logger.warning("NewsAPI returned no articles for query %r", query)
        return _empty()
    rows = []
    for a in articles:
        rows.append({"date": a.get("publishedAt"), "title": a.get("title"), "source": (a.get("source") or {}).get("name"), "url": a.get("url")})
    return frame(rows)

def frame(rows):
    df = pd.DataFrame(rows)
    df["date"] = pd.to_datetime(df["date"], errors="coerce", utc = True).dt.tz_localize(None)
    df = df.dropna(subset = ["date"]).set_index("date").sort_index()
    logger.info("Fetched %d news headlines", len(df))
    return df[columns]

def parse_gdelt_date(value):
    if not value:
        return pd.NaT
    return pd.to_datetime(value, format = "%Y%m%dT%H%M%SZ", errors = "coerce", utc = True)