from scrapy import Spider

from scrapy_spider_metadata import Args, get_spider_metadata
from tests.test_params import Params, get_expected_schema


def test_metadata_empty():
    class MySpider(Spider):
        name = "my_spider"

    assert get_spider_metadata(MySpider) == {}


def test_metadata_simple():
    class MySpider(Spider):
        name = "my_spider"
        metadata = {
            "description": "This is my spider.",
            "category": "My basic spiders",
        }

    assert get_spider_metadata(MySpider) == {
        "description": "This is my spider.",
        "category": "My basic spiders",
    }


def test_metadata_params():
    class MySpider(Args[Params], Spider):
        name = "my_spider"
        metadata = {
            "description": "This is my spider.",
            "category": "My basic spiders",
        }

    assert get_spider_metadata(MySpider) == {
        "description": "This is my spider.",
        "category": "My basic spiders",
        "param_schema": get_expected_schema(Params),
    }


def test_metadata_inheritance():
    class BaseSpider(Spider):
        metadata = {
            "description": "Base spider.",
            "category": "Base spiders",
        }

    class BaseNewsSpider(BaseSpider):
        metadata = {
            **BaseSpider.metadata,
            "description": "Base news spider.",
        }

    class CNNSpider(BaseNewsSpider):
        metadata = {
            **BaseNewsSpider.metadata,
            "description": "CNN spider.",
            "category": "Concrete spiders",
            "website": "CNN",
        }

    assert get_spider_metadata(BaseSpider) == {
        "description": "Base spider.",
        "category": "Base spiders",
    }

    assert get_spider_metadata(BaseNewsSpider) == {
        "description": "Base news spider.",
        "category": "Base spiders",
    }

    assert get_spider_metadata(CNNSpider) == {
        "description": "CNN spider.",
        "category": "Concrete spiders",
        "website": "CNN",
    }
