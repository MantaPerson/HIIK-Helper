import json

from scrapy.http import Request, TextResponse
from scrapy.selector import Selector

import hiik_helper.spiders.hiik_default_spider as default_spider_module
from hiik_helper.spiders.hiik_default_spider import HiikDefaultSpider
from hiik_helper.spiders.hiik_xml_spider import HiikXmlSpider


def test_default_spider_load_json_file_creates_missing_file(tmp_path):
    path = tmp_path / "visited_urls.json"

    data = HiikDefaultSpider.load_json_file(path, [])

    assert data == []
    assert json.loads(path.read_text(encoding="utf-8")) == []


def test_default_spider_load_json_file_falls_back_on_invalid_json(tmp_path):
    path = tmp_path / "visited_urls.json"
    path.write_text("{", encoding="utf-8")

    data = HiikDefaultSpider.load_json_file(path, [])

    assert data == []


def test_default_spider_handles_missing_or_invalid_article_links():
    spider = object.__new__(HiikDefaultSpider)
    spider.article_link_domains = ["example.test/2024"]

    assert spider.get_url_in_article("<p>No link</p>") is None
    assert spider.link_is_article(None) is False
    assert spider.link_is_article("https://example.test/2024/story") is True
    assert spider.link_is_article("https://example.test/about") is False
    assert spider.article_contains_more_link('<a class="more-link button">More</a>')
    assert spider.clean_text_from_html("<p>Hello <strong>world</strong></p>") == (
        "Hello world"
    )


def test_xml_spider_feed_configuration_is_defined():
    assert HiikXmlSpider.iterator == "iternodes"
    assert HiikXmlSpider.itertag == "item"
    assert not HiikXmlSpider.namespaces


def test_default_spider_saves_found_articles_to_configured_file(tmp_path, monkeypatch):
    found_articles_path = tmp_path / "found_articles.json"
    found_articles_path.write_text(
        json.dumps({"https://example.test/old": {"headline": "Old"}}),
        encoding="utf-8",
    )
    monkeypatch.setattr(
        default_spider_module, "FOUND_ARTICLES_PATH", found_articles_path
    )
    spider = object.__new__(HiikDefaultSpider)
    spider.found_articles = {
        "https://example.test/new": {
            "headline": "New",
            "subheadline": "Sub",
            "paragraphs": "Body",
        }
    }

    spider.save_found_articles_to_json()

    saved = json.loads(found_articles_path.read_text(encoding="utf-8"))
    assert set(saved) == {"https://example.test/old", "https://example.test/new"}


def test_default_spider_saves_sorted_unique_visited_urls(tmp_path, monkeypatch):
    visited_urls_path = tmp_path / "visited_urls.json"
    monkeypatch.setattr(default_spider_module, "VISITED_URLS_PATH", visited_urls_path)
    spider = object.__new__(HiikDefaultSpider)
    spider.visited_json_urls = {"https://example.test/b"}
    spider.visited_urls_this_scrape = {
        "https://example.test/a",
        "https://example.test/b",
    }

    spider.save_visited_urls_to_json()

    assert json.loads(visited_urls_path.read_text(encoding="utf-8")) == [
        "https://example.test/a",
        "https://example.test/b",
    ]


def test_default_spider_identifies_and_extracts_article_markup():
    body = """
    <html>
      <body>
        <div class="entry-content entry clearfix">Article body</div>
        <div class="entry-content"><a href="https://example.test/2024/story">More</a></div>
      </body>
    </html>
    """
    response = TextResponse(
        url="https://example.test",
        body=body,
        encoding="utf-8",
        request=Request("https://example.test"),
    )
    spider = object.__new__(HiikDefaultSpider)
    spider.content_class_article = "entry-content entry clearfix"
    spider.content_class_list = "entry-content"

    assert spider.current_page_is_article(response) is True
    assert spider.current_page_is_list(response) is True
    assert spider.parse_article(response) == [
        '<div class="entry-content entry clearfix">Article body</div>'
    ]
    assert spider.get_url_in_article(spider.parse_article_list(response)[0]) == (
        "https://example.test/2024/story"
    )


def test_default_spider_parse_article_records_content():
    body = """
    <html>
      <head><meta property="article:published_time" content="2024-08-01T00:00:00+00:00"></head>
      <body>
        <h1>Headline</h1>
        <h2>Subheadline</h2>
        <div class="entry-content entry clearfix">Article body</div>
        <p>First paragraph.</p>
        <p>Second paragraph.</p>
      </body>
    </html>
    """
    response = TextResponse(
        url="https://karennews.org/2024/story",
        body=body,
        encoding="utf-8",
        request=Request("https://karennews.org/2024/story"),
    )
    spider = object.__new__(HiikDefaultSpider)
    spider.visited_json_urls = set()
    spider.visited_urls_this_scrape = set()
    spider.found_articles = {}
    spider.content_class_article = "entry-content entry clearfix"
    spider.content_class_list = "entry-content"
    spider.article_link_domains = ["karennews.org/2024"]
    spider.link_extractor = default_spider_module.LinkExtractor()

    yielded = list(spider.parse(response))

    assert not yielded
    assert spider.visited_urls_this_scrape == {"https://karennews.org/2024/story"}
    assert spider.found_articles["https://karennews.org/2024/story"] == {
        "url": "https://karennews.org/2024/story",
        "accessing-date": spider.found_articles["https://karennews.org/2024/story"][
            "accessing-date"
        ],
        "last-modification": "2024-08-01T00:00:00+00:00",
        "headline": "Headline",
        "subheadline": "Subheadline",
        "paragraphs": "First paragraph.\n\nSecond paragraph.",
    }


def test_default_spider_parse_list_page_follows_unvisited_article_links():
    body = """
    <html>
      <body>
        <div class="entry-content">
          <a href="https://karennews.org/2024/story">Read more</a>
        </div>
      </body>
    </html>
    """
    response = TextResponse(
        url="https://karennews.org",
        body=body,
        encoding="utf-8",
        request=Request("https://karennews.org"),
    )
    spider = object.__new__(HiikDefaultSpider)
    spider.visited_json_urls = set()
    spider.visited_urls_this_scrape = set()
    spider.found_articles = {}
    spider.content_class_article = "entry-content entry clearfix"
    spider.content_class_list = "entry-content"
    spider.article_link_domains = ["karennews.org/2024"]
    spider.link_extractor = default_spider_module.LinkExtractor()

    yielded = list(spider.parse(response))

    assert [request.url for request in yielded] == ["https://karennews.org/2024/story"]


def test_default_spider_spider_closing_persists_both_state_files(tmp_path, monkeypatch):
    found_articles_path = tmp_path / "found_articles.json"
    visited_urls_path = tmp_path / "visited_urls.json"
    found_articles_path.write_text("{}", encoding="utf-8")
    monkeypatch.setattr(
        default_spider_module, "FOUND_ARTICLES_PATH", found_articles_path
    )
    monkeypatch.setattr(default_spider_module, "VISITED_URLS_PATH", visited_urls_path)
    spider = object.__new__(HiikDefaultSpider)
    spider.found_articles = {"https://example.test/article": {"headline": "Headline"}}
    spider.visited_json_urls = set()
    spider.visited_urls_this_scrape = {"https://example.test/article"}

    spider.spider_closing(spider)

    assert json.loads(found_articles_path.read_text(encoding="utf-8")) == {
        "https://example.test/article": {"headline": "Headline"}
    }
    assert json.loads(visited_urls_path.read_text(encoding="utf-8")) == [
        "https://example.test/article"
    ]


def test_xml_spider_parse_node_extracts_title_and_link():
    spider = object.__new__(HiikXmlSpider)
    selector = Selector(
        text="<rss><channel><item><title>Title</title><link>https://example.test</link></item></channel></rss>",
        type="xml",
    )
    node = selector.xpath("//item")[0]

    parsed = spider.parse_node(None, node)

    assert parsed == {"title": "Title", "link": "https://example.test"}


def test_xml_spider_closing_is_noop():
    spider = object.__new__(HiikXmlSpider)

    assert spider.spider_closing(spider=None) is None
