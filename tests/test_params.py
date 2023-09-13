from pydantic import BaseModel, ValidationError
from pytest import raises
from scrapy import Spider

from scrapy_spider_metadata import parse_spider_kwargs

from . import get_spider


def test_parse_spider_kwargs_convert():
    class Params(BaseModel):
        foo: int

    class ParamSpider(Spider):
        name = "params"
        meta = {
            "params": Params,
        }

        def __init__(self, *args, **kwargs):
            kwargs = parse_spider_kwargs(self, kwargs)
            super().__init__(*args, **kwargs)

    spider = get_spider(ParamSpider, kwargs={"foo": "1"})
    assert spider.foo == 1


def test_parse_spider_kwargs_validate():
    class Params(BaseModel):
        foo: bool

    class ParamSpider(Spider):
        name = "params"
        meta = {
            "params": Params,
        }

        def __init__(self, *args, **kwargs):
            kwargs = parse_spider_kwargs(self, kwargs)
            super().__init__(*args, **kwargs)

    with raises(ValidationError):
        get_spider(ParamSpider, kwargs={"foo": "2"})
