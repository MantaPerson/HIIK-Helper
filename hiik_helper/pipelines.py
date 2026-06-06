"""Scrapy item pipelines for post-processing crawled data."""


class HiikHelperPipeline:
    """Pass-through pipeline kept as a hook for future item processing."""

    def process_item(self, item, spider):
        """Return scraped items unchanged."""

        return item
