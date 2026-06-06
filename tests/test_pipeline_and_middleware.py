from hiik_helper.items import HiikHelperItem
from hiik_helper.middlewares import (
    HiikHelperDownloaderMiddleware,
    HiikHelperSpiderMiddleware,
)
from hiik_helper.pipelines import HiikHelperPipeline


def test_pipeline_returns_item_unchanged():
    item = {"headline": "Headline"}

    assert HiikHelperPipeline().process_item(item, spider=None) is item


def test_placeholder_item_can_be_instantiated():
    assert isinstance(HiikHelperItem(), HiikHelperItem)


def test_spider_middleware_passes_output_and_start_requests_through():
    middleware = HiikHelperSpiderMiddleware()
    output = [{"item": 1}, {"item": 2}]

    assert list(middleware.process_spider_output(None, output, None)) == output
    assert list(middleware.process_start_requests(output, None)) == output
    assert middleware.process_spider_input(response=None, spider=None) is None
    assert middleware.process_spider_exception(None, Exception("boom"), None) is None


def test_downloader_middleware_passes_request_and_response_through():
    middleware = HiikHelperDownloaderMiddleware()
    request = object()
    response = object()

    assert middleware.process_request(request, spider=None) is None
    assert middleware.process_response(request, response, spider=None) is response
    assert middleware.process_exception(request, Exception("boom"), spider=None) is None
