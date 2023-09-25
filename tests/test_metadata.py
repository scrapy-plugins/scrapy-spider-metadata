from pydantic import BaseModel
from scrapy import Spider

from scrapy_spider_metadata import Args, get_metadata_for_spider


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
        "param_schema": {},
    }


def test_metadata_params():
    class Params(BaseModel):
        pass

    class MySpider(Args[Params], Spider):
        name = "my_spider"
        metadata = {
            "description": "This is my spider.",
            "category": "My basic spiders",
        }

    assert get_metadata_for_spider(MySpider) == {
        "description": "This is my spider.",
        "category": "My basic spiders",
        "param_schema": {
            "properties": {},
            "title": "Params",
            "type": "object",
        },
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
        "param_schema": {},
    }

    assert get_metadata_for_spider(BaseNewsSpider) == {
        "description": "Base news spider.",
        "category": "Base spiders",
        "param_schema": {},
    }

    assert get_metadata_for_spider(CNNSpider) == {
        "description": "CNN spider.",
        "category": "Concrete spiders",
        "website": "CNN",
        "param_schema": {},
    }
