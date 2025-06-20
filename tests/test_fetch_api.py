from fastapi.testclient import TestClient
from backend.app import app, news_store, store
from config import STUDENT_ID
import feedparser

client = TestClient(app)

def test_get_news_empty():
    news_store[STUDENT_ID] = []
    res = client.get(f"/news/{STUDENT_ID}")
    assert res.status_code == 200
    assert res.json() == {"articles": []}

class DummyFeed:
    entries = [
        {"title": "T1", "link": "<http://a>", "published": "2025-01-01"},
        {"title": "T2", "link": "<http://b>", "published": ""}
    ]

def test_fetch_and_get(monkeypatch):
    monkeypatch.setattr("config.SOURCES", ["http://example.com/rss"])

    store[STUDENT_ID] = ["http://example.com/rss"]

    monkeypatch.setattr(feedparser, "parse", lambda url: DummyFeed)

    news_store[STUDENT_ID] = []

    res1 = client.post(f"/fetch/{STUDENT_ID}")
    assert res1.status_code == 200
    assert res1.json() == {"fetched": 2}

    res2 = client.get(f"/news/{STUDENT_ID}")
    assert res2.status_code == 200
    assert res2.json() == {
        "articles": [
            {"title": "T1", "link": "<http://a>", "published": "2025-01-01"},
            {"title": "T2", "link": "<http://b>", "published": ""}
        ]
    }

def test_fetch_custom_feed(monkeypatch):
    news_store[STUDENT_ID] = []
    store[STUDENT_ID] = []

    response = client.post(f"/sources/{STUDENT_ID}", json={"url": "http://test.com/rss"})
    assert response.status_code == 200
    assert "http://test.com/rss" in response.json()["sources"]

    class DummyFeedCustom:
        entries = [{"title": "X", "link": "L", "published": "2025-04-28"}]

    monkeypatch.setattr(feedparser, "parse", lambda _: DummyFeedCustom())

    r = client.post(f"/fetch/{STUDENT_ID}")
    assert r.status_code == 200
    assert r.json() == {"fetched": 1}

    r_news = client.get(f"/news/{STUDENT_ID}")
    assert r_news.status_code == 200
    articles = r_news.json()["articles"]
    assert len(articles) == 1
    assert articles[0]["title"] == "X"
    assert articles[0]["link"] == "L"
    assert articles[0]["published"] == "2025-04-28"
