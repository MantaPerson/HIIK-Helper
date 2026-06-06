"""Experimental XML feed spider for article feed parsing."""

import logging

import scrapy
import scrapy.spiders
from scrapy.signals import spider_closed
from scrapy.signalmanager import dispatcher


logger = logging.getLogger(__name__)


class HiikXmlSpider(scrapy.spiders.XMLFeedSpider):
    """Parse item nodes from an XML feed.

    This spider is currently a scaffold and is not wired into the normal crawl
    workflow.
    """

    name = "HIIK XML Spider"
    iterator = "iternodes"
    itertag = "item"
    namespaces: list[tuple[str, str]] = []

    def __init__(
        self, start_urls: list[str], allowed_domains: list[str], *args, **kwargs
    ):
        """Initialize feed targets and connect the spider-close signal."""

        logger.info("Initializing spider")
        super().__init__(*args, **kwargs)
        # Add spider close handler to save the found articles to a JSON file
        dispatcher.connect(self.spider_closing, signal=spider_closed)

        self.start_urls: list[str] = start_urls
        self.allowed_domains: list[str] = allowed_domains

    # def parse_node(self, response, node):
    #     # Save all links from the XML feed
    #     links = node.xpath("ns:link/text()", namespaces=self.namespaces).getall()

    #     yield {
    #         "title": node.xpath("ns:title/text()", namespaces=self.namespaces).get(),
    #         "link": node.xpath("ns:link/text()", namespaces=self.namespaces).get(),
    #     }

    def parse_node(self, response, selector):
        """Parse a single XML item node into a minimal title/link record."""

        self.logger.info(
            "Hi, this is a <%s> node!: %s", self.itertag, "".join(selector.getall())
        )

        return {
            "title": selector.xpath("title/text()").get(),
            "link": selector.xpath("link/text()").get(),
        }

    def spider_closing(self, spider):
        """Placeholder close hook for future XML crawl output persistence."""

        # logger.info("Saving found articles to JSON")
        # with open("found_articles.json", "w") as f:
        #     json.dump(self.found_articles, f)
        # logger.info("Saved found articles to JSON")
        return None
