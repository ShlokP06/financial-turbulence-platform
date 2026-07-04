import httpx
import pandas as pd
from turballoc.config import settings
from turballoc.logging_utils import get_logger

logger = get_logger(__name__)

TAVILY_URL = "https://api.tavily.com/search"
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

def asset_drivers(store, date, window = 126, top_k = 4):
    """Assets with the largest standardized moves on `date` — the drivers of that day's
    Mahalanobis turbulence. Returns a list of {asset, ret, z} sorted by |z| descending."""
    returns = store.read("returns").dropna(how = "any")
    ts = pd.Timestamp(date)
    if ts not in returns.index:
        raise ValueError(f"no returns for {date}")
    loc = returns.index.get_loc(ts)
    past = returns.iloc[max(0, loc - window):loc]
    if len(past) < 2:
        raise ValueError(f"not enough history before {date}")
    row = returns.iloc[loc]
    z = (row - past.mean()) / past.std(ddof = 0).replace(0, 1e-9)
    order = z.abs().sort_values(ascending = False).index[:top_k]
    return [{"asset": a, "ret": float(row[a]), "z": float(z[a])} for a in order]

def _news_window(date, before = 3, after = 2):
    "Return (start, end) YYYY-MM-DD dates bracketing `date` for scoping the news search."
    d = pd.Timestamp(date)
    return ((d - pd.Timedelta(days = before)).date().isoformat(),
            (d + pd.Timedelta(days = after)).date().isoformat())

def _fetch_news(date, context, max_results = 6):
    """Tavily news search scoped to the days *around* `date`.

    Without a date window Tavily returns today's headlines regardless of the date asked about,
    so explanations of historical spikes were grounded in the wrong news. `start_date`/`end_date`
    pin the search to the event window (a few days either side, so the reporting that explains the
    move is included), which makes the retrieved headlines actually match the day.
    """
    start, end = _news_window(date)
    query = f"US stock market around {date}: what drove the market volatility? {context}"
    resp = httpx.post(TAVILY_URL, timeout = 25.0, json = {
        "api_key": settings.tavily_api_key,
        "query": query,
        "topic": "news",
        "search_depth": "advanced",
        "start_date": start,
        "end_date": end,
        "max_results": max_results,
    })
    resp.raise_for_status()
    results = resp.json().get("results", [])
    return [{"title": r.get("title", ""), "url": r.get("url", ""),
             "published": r.get("published_date", "")} for r in results]

def _summarize(date, turbulence, regime, drivers, sources):
    "Ask Groq to explain the day's turbulence, grounded in the asset moves and headlines."
    driver_lines = "\n".join(f"- {d['asset']}: {d['z']:+.1f} sigma ({d['ret'] * 100:+.2f}%)" for d in drivers)
    headlines = "\n".join(f"- {s['title']} ({s['published']})" for s in sources) or "(no headlines found)"
    prompt = (
        f"On {date}, our market-turbulence index (Mahalanobis distance of multi-asset returns "
        f"from their trailing distribution) read {turbulence:.1f}, a {regime} regime.\n\n"
        f"The assets with the largest standardized moves that day:\n{driver_lines}\n\n"
        f"News headlines from around that date:\n{headlines}\n\n"
        "In 3-4 sentences, explain what most likely drove the elevated turbulence. Ground the "
        "explanation in the asset moves and the headlines. If the headlines don't clearly explain "
        "it, say so rather than inventing a cause."
    )
    resp = httpx.post(GROQ_URL, timeout = 30.0,
        headers = {"Authorization": f"Bearer {settings.groq_api_key}"},
        json = {
            "model": settings.groq_model,
            "temperature": 0.3,
            "max_tokens": 300,
            "messages": [
                {"role": "system", "content": "You are a precise, grounded markets analyst. Be concise."},
                {"role": "user", "content": prompt},
            ],
        })
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"].strip()

def explain_day(store, date):
    """Why was turbulence elevated on `date`? Pulls the day's turbulence and regime, decomposes
    the driving asset moves, fetches news via Tavily, and has Groq tie it together. Raises
    ValueError if the date has no data."""
    turb = store.read("turbulence")
    ts = pd.Timestamp(date)
    if ts not in turb.index or pd.isna(turb.loc[ts, "turbulence"]):
        raise ValueError(f"no turbulence for {date}")
    value = float(turb.loc[ts, "turbulence"])
    regime = str(turb.loc[ts, "regime"])
    drivers = asset_drivers(store, ts)
    context = f"{regime} regime; biggest moves " + ", ".join(d["asset"] for d in drivers)
    sources = _fetch_news(date, context)
    explanation = _summarize(date, value, regime, drivers, sources)
    logger.info("Explained turbulence for %s (%d sources)", date, len(sources))
    return {"date": str(date), "turbulence": value, "regime": regime,
            "drivers": drivers, "sources": sources, "explanation": explanation}
