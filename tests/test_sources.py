import httpx

from nutricion.memory.store import Store
from nutricion.sources.catalog import SOURCES, Category, Source, category_of_the_day
from nutricion.sources.feeds import fetch_source
from nutricion.sources.images import find_og_image

RSS = b"""<?xml version="1.0"?>
<rss version="2.0" xmlns:media="http://search.yahoo.com/mrss/"><channel>
<item><title>Nvidia &amp; IA</title><link>https://x/1</link>
<description>&lt;p&gt;Texto &lt;b&gt;importante&lt;/b&gt;&lt;/p&gt;</description>
<media:content url="https://img/1.jpg" medium="image"/>
<source url="https://bloomberg.com">Bloomberg</source></item>
</channel></rss>"""


def _client(body: bytes, content_type: str = "application/rss+xml") -> httpx.Client:
    transport = httpx.MockTransport(
        lambda request: httpx.Response(200, content=body, headers={"content-type": content_type})
    )
    return httpx.Client(transport=transport)


def test_feed_entry_is_cleaned_and_keeps_publisher_and_image():
    source = Source("Bloomberg (vía Google News)", "https://feed", Category.FINANZAS)
    [candidate] = fetch_source(source, _client(RSS))
    assert candidate.title == "Nvidia & IA"
    assert candidate.summary == "Texto importante"
    assert candidate.source == "Bloomberg"
    assert candidate.image_url == "https://img/1.jpg"
    assert candidate.category is Category.FINANZAS


def test_old_entries_are_skipped():
    old = RSS.replace(b"<item>", b"<item><pubDate>Mon, 01 Jan 2024 00:00:00 GMT</pubDate>")
    source = Source("Feed", "https://feed", Category.NEGOCIOS)
    assert fetch_source(source, _client(old)) == []


def test_og_image_is_found_in_article_html():
    page = b'<html><head><meta property="og:image" content="https://cdn/x.png"></head></html>'
    assert find_og_image("https://art", _client(page, "text/html")) == "https://cdn/x.png"


def test_og_image_missing_returns_empty():
    assert find_og_image("https://art", _client(b"<html></html>", "text/html")) == ""


def test_every_category_has_sources_and_rotates():
    assert {s.category for s in SOURCES} == set(Category)
    assert [category_of_the_day(n) for n in range(4)] == [
        Category.NEGOCIOS,
        Category.FINANZAS,
        Category.INVESTIGACION,
        Category.NEGOCIOS,
    ]


def test_old_database_is_migrated(tmp_path):
    import sqlite3

    path = tmp_path / "old.db"
    db = sqlite3.connect(path)
    db.executescript(
        "CREATE TABLE lessons (id INTEGER PRIMARY KEY AUTOINCREMENT, created_at TEXT NOT NULL,"
        " headline TEXT NOT NULL, what_happened TEXT NOT NULL, why_it_matters TEXT NOT NULL,"
        " source_url TEXT NOT NULL UNIQUE, challenge TEXT NOT NULL, state TEXT NOT NULL,"
        " answer TEXT, feedback TEXT, scores TEXT);"
        "INSERT INTO lessons VALUES (1, 'x', 'h', 'w', 'y', 'https://u', 'c', 'awaiting_answer',"
        " NULL, NULL, NULL);"
    )
    db.commit()
    db.close()
    lesson = Store(str(path)).open_lesson()
    assert lesson.pill.headline == "h" and lesson.pill.options == () and lesson.choice == ""
