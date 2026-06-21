import pandas as pd
import pytest
from turballoc.nlp import features, sentiment

@pytest.fixture
def sample_texts():
    idx = pd.to_datetime(["2020-01-01 09:00", "2020-01-01 15:00", "2020-01-02 10:00"])
    idx.name = "date"
    return pd.DataFrame({"title": ["stocks rally hard", "markets crash badly", "fed holds rates steady"]}, index = idx)\

def fake_score_texts(texts):
    mapping = {"stocks rally hard": 0.8, "markets crash badly": -0.6, "fed holds rates steady": 0.0}
    rows = [{"text": t, "label": "x", "p_positive": 0.0, "p_negative": 0.0, "p_neutral": 0.0, "sentiment": mapping.get(t, 0.0)} for t in texts]
    return pd.DataFrame(rows)

def test_daily_sentiment_aggregates(monkeypatch, sample_texts):
      monkeypatch.setattr(sentiment, "score_texts", fake_score_texts)
      daily = features.daily_sentiment(sample_texts)
      assert list(daily.columns) == ["sentiment", "count"]
      assert daily.index.name == "date"
      assert len(daily) == 2
      day1 = pd.Timestamp("2020-01-01")
      assert daily.loc[day1, "count"] == 2
      assert daily.loc[day1, "sentiment"] == pytest.approx(0.1)

def test_daily_sentiment_empty(monkeypatch):
    monkeypatch.setattr(sentiment, "score_texts", fake_score_texts)
    empty = pd.DataFrame({"title": []}, index=pd.DatetimeIndex([], name="date"))
    daily = features.daily_sentiment(empty)
    assert daily.empty
    assert list(daily.columns) == ["sentiment", "count"]

def test_score_texts_empty_no_model():
    out = sentiment.score_texts([])
    assert out.empty
    assert "sentiment" in out.columns

def test_build_sentiment_feature_writes(monkeypatch, sample_texts):
    monkeypatch.setattr(sentiment, "score_texts", fake_score_texts)
    written = {}
    
    class FakeStore:
        def write(self, table, frame):
            written["table"] = table
            written["frame"] = frame

    daily = features.build_sentiment_feature(sample_texts, store=FakeStore())
    assert written["table"] == "sentiment"
    assert written["frame"].equals(daily) 