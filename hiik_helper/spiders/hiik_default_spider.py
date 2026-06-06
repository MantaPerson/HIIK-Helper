"""Default Scrapy spider for discovering and extracting Karen News articles."""

import datetime
import json
import logging
import re
from pathlib import Path

import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.signals import spider_closed
from scrapy.signalmanager import dispatcher


logger = logging.getLogger(__name__)

FOUND_ARTICLES_PATH = Path("found_articles.json")
VISITED_URLS_PATH = Path("visited_urls.json")


class HiikDefaultSpider(scrapy.Spider):
    """Crawl article pages and persist discovered article content as JSON."""

    name = "HIIK Default Spider"

    def __init__(
        self, start_urls: list[str], allowed_domains: list[str], *args, **kwargs
    ):
        """Initialize crawl targets, URL state, and extraction selectors."""

        logger.info("Initializing spider")
        super().__init__(*args, **kwargs)
        # Add spider close handler to save the found articles to a JSON file
        dispatcher.connect(self.spider_closing, signal=spider_closed)

        self.start_urls: list[str] = start_urls
        self.allowed_domains: list[str] = allowed_domains
        self.article_link_domains: list[str] = [
            "karennews.org/category/article",
            "karennews.org/2024",
        ]
        self.link_extractor = LinkExtractor()

        self.found_articles: dict[str, dict[str, str]] = {}
        self.content_class_article = "entry-content entry clearfix"
        self.content_class_list = "entry-content"

        self.visited_urls_this_scrape = set()

        logger.info("Loading visited URLs from JSON")
        self.visited_json_urls = set(self.load_json_file(VISITED_URLS_PATH, []))

        logger.info("Spider initialized")

    @staticmethod
    def load_json_file(path: Path, default):
        """Load a JSON file, creating it with a default value when missing."""

        if not path.exists():
            path.write_text(json.dumps(default, indent=4), encoding="utf-8")
            return default.copy() if hasattr(default, "copy") else default

        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            logger.warning("Could not parse %s; using an empty default.", path)
            return default.copy() if hasattr(default, "copy") else default

    def parse(self, response):
        """Parse a response as an article or list page and follow article links."""

        article_links: set = set()

        url = response.url

        if (
            url not in self.visited_json_urls
            and url not in self.visited_urls_this_scrape
        ):
            if self.current_page_is_article(response):
                # Get content of the article on the page
                article_content = self.parse_article(response)

                # Add the article content to the list of found articles

                for supposed_article in article_content:
                    # Get article:modified_time from meta property
                    article_modified_time = response.xpath(
                        "//meta[@property='article:published_time']/@content"
                    ).get()

                    # Get the headline of the article
                    headline = response.xpath("//h1/text()").get()

                    # Get subheadline of the article
                    subheadline = response.xpath("//h2/text()").get()

                    # Get all paragraphs of the article
                    paragraphs = response.xpath("//p/text()").getall()
                    paragraph_text = "\n\n".join(paragraphs)

                    # Add the article to the list of found articles
                    article_dict = {
                        "url": url,
                        "accessing-date": str(datetime.datetime.now(datetime.UTC)),
                        "last-modification": article_modified_time,
                        "headline": headline,
                        "subheadline": subheadline,
                        "paragraphs": paragraph_text,
                    }
                    self.found_articles[url] = article_dict

                    self.visited_urls_this_scrape.add(url)

            elif self.current_page_is_list(response):
                # Get content of the article on the page
                article_list = self.parse_article_list(response)

                for supposed_article in article_list:
                    # Get the more link of the article
                    more_link_url = self.get_url_in_article(supposed_article)
                    if more_link_url and self.link_is_article(more_link_url):
                        article_links.add(more_link_url)

        extracted_links = self.link_extractor.extract_links(response)
        # Filter out the article links

        article_links = article_links.union(
            {link.url for link in extracted_links if self.link_is_article(link.url)}
        )

        yield_links = [
            link
            for link in article_links
            if link not in self.visited_json_urls
            and link not in self.visited_urls_this_scrape
        ]

        # Follow the next article link
        for link in yield_links:
            yield response.follow(link, callback=self.parse)

    def current_page_is_article(self, response):
        """Return whether the response contains the configured article body."""

        # Check if the current page is an article
        if response.xpath(f'//div[@class="{self.content_class_article}"]'):
            return True
        return False

    def current_page_is_list(self, response):
        """Return whether the response contains a list of article excerpts."""

        # Check if the current page is a list of articles
        if response.xpath(f'//div[@class="{self.content_class_list}"]'):
            return True
        return False

    def parse_article(self, response):
        """Extract raw article content blocks from an article response."""

        # Parse the article content
        # Mocked implementation
        return response.xpath(f'//div[@class="{self.content_class_article}"]').getall()

    def parse_article_list(self, response):
        """Extract raw article list blocks from a list response."""

        # Parse the article content
        # Mocked implementation
        return response.xpath(f'//div[@class="{self.content_class_list}"]').getall()

    def link_is_article(self, url):
        """Return whether a URL matches the configured article URL patterns."""

        if not url:
            return False

        # Check if the link is an article
        for article_link_domain in self.article_link_domains:
            if article_link_domain in url:
                return True
        return False

    def article_contains_more_link(self, article):
        """Return whether an article excerpt contains a read-more link."""

        # Check if the article contains a more link
        # Mocked implementation
        return "more-link button" in article

    def get_url_in_article(self, article):
        """Extract the first linked URL from a raw article excerpt."""

        # Get the more link in the article
        urls = re.findall(r'href="([^"]*)"', article)
        return urls[0] if urls else None

    def clean_text_from_html(self, text):
        """Remove HTML tags from a string."""

        # Clean the text from HTML tags
        # Mocked implementation
        return re.sub(r"<[^>]*>", "", text)

    def save_found_articles_to_json(self):
        """Merge newly found articles into `found_articles.json`."""

        # Save the found articles to a JSON file
        data = self.load_json_file(FOUND_ARTICLES_PATH, {})

        data.update(self.found_articles)

        with FOUND_ARTICLES_PATH.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    def save_visited_urls_to_json(self):
        """Persist URLs visited during this crawl into `visited_urls.json`."""

        self.visited_json_urls.update(self.visited_urls_this_scrape)

        # Save the visited URLs to a JSON file
        with VISITED_URLS_PATH.open("w", encoding="utf-8") as f:
            json.dump(sorted(self.visited_json_urls), f, indent=4)

    def spider_closing(self, spider):
        """Persist crawl state when Scrapy closes the spider."""

        logger.info("Spider closing")

        logger.info("Saving visited URLs to JSON")
        self.save_visited_urls_to_json()

        logger.info("Saving found articles to JSON")
        self.save_found_articles_to_json()
