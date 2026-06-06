"""Scrapy item pipelines for post-processing crawled data."""

# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class HiikHelperPipeline:
    """Pass-through pipeline kept as a hook for future item processing."""

    def process_item(self, item, spider):
        """Return scraped items unchanged."""

        return item
