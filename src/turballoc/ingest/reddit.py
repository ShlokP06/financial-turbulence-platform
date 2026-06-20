import praw
import pandas as pd
from turballoc.config import settings
from turballoc.logging_utils import get_logger

logger = get_logger(__name__)
subreddits = ("wallstreetbets", "investing", "stocks", "StockMarket", "economics")
columns = ["subreddit", "title", "selftext", "score"]

def client():
    if not (settings.reddit_client_id and settings.reddit_client_secret and settings.reddit_user_agent):
        raise ValueError("Reddot Credentials are not fully set. ")
    return praw.Reddit(client_id = settings.reddit_client_id, client_secret = settings.reddit_client_secret,
                       user_agent = settings.reddit_user_agent, check_for_async = False)

def fetch_reddit(subs = subreddits, sort = "hot", limit = 100):
    "Pull recent posts from finance subreddits"
    reddit = client()
    reddit.read_only = True
    rows = []
    for sub in subs:
        try:
            listing = getattr(reddit.subreddit(sub), sort)(limit = limit)
            for post in listing:
                rows.append({"date": post.created_utc, "subreddit": sub, "title": post.title, "selftext": post.selftext or "", "score": post.score})
        except Exception as e:
            logger.warning("Reddit fetch failed....")
    if not rows:
        idx = pd.DatetimeIndex([], name="date")
        return pd.DataFrame({c: pd.Series(dtype = "object") for c in columns}, index = idx)
    df = pd.DataFrame(rows)
    df["date"] = pd.to_datetime(df["date"], unit = "s")
    df = df.set_index("date").sort_index()
    logger.info(f"Fetched {len(df)} reddit posts...")
    return df[columns]



