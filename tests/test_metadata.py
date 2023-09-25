from scrapy import Spider

from scrapy_spider_metadata import Args, get_metadata_for_spider
from tests.test_params import Params, get_expected_schema


def test_metadata_empty():
    class MySpider(Spider):
        name = "my_spider"

    assert get_metadata_for_spider(MySpider) == {}


def test_metadata_simple():
    class MySpider(Spider):
        name = "my_spider"
        metadata = {
            "description": "This is my spider.",
            "category": "My basic spiders",
        }

    assert get_metadata_for_spider(MySpider) == {
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

    assert get_metadata_for_spider(MySpider) == {
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

    assert get_metadata_for_spider(BaseSpider) == {
        "description": "Base spider.",
        "category": "Base spiders",
    }

    assert get_metadata_for_spider(BaseNewsSpider) == {
        "description": "Base news spider.",
        "category": "Base spiders",
    }

    assert get_metadata_for_spider(CNNSpider) == {
        "description": "CNN spider.",
        "category": "Concrete spiders",
        "website": "CNN",
    }
