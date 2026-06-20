import functools
import pandas as pd
from turballoc.config import settings
from turballoc.logging_utils import get_logger

logger = get_logger(__name__)

model = "ProsusAI/finbert"
batchsize = 32

@functools.lru_cache(maxsize=1)
def get_pipeline():
    import torch
    from transformers import pipeline
    torch.manual_seed(settings.random_seed)
    logger.info("Loading FinBERT Pipeline (%s)", model)
    return pipeline("text-classification", model = model, top_k = None,
    truncation = True, max_length = 512)

def score_texts(texts):
    cols = ["text", "label", "p_positive", "p_negative", "p_neutral", "sentiment"]
    if not texts:
        return pd.DataFrame({c: pd.Series(dtype = "object") for c in cols})
    pipe = get_pipeline()
    outputs = pipe(list(texts), batch_size = batchsize)
    rows = []
    for text, scores in zip(texts, outputs):
        probs = {d["label"].lower(): float(d["score"]) for d in scores}
        p_pos = probs.get("positive", 0.0)
        p_neg = probs.get("negative", 0.0)
        p_neu = probs.get("neutral", 0.0)
        label = max(probs, key = probs.get)
        rows.append({"text": text, "label": label, "p_positive": p_pos,
                    "p_negative": p_neg, "p_neutral" : p_neu, "sentiment": p_pos - p_neg})
    return pd.DataFrame(rows, columns = cols)
