from packaging import version
from pydantic import BaseModel, ValidationError
from pydantic.version import VERSION as PYDANTIC_VERSION
from pytest import raises
from scrapy import Spider

from scrapy_spider_metadata import Args

from . import get_spider

USING_PYDANTIC_1 = version.parse(str(PYDANTIC_VERSION)) < version.parse("2")


class Params(BaseModel):
    foo: int


class ParamSpider(Args[Params], Spider):
    name = "params"


def test_convert():
    spider = get_spider(ParamSpider, kwargs={"foo": "1"})
    assert isinstance(spider.args, Params)
    assert spider.args.foo == 1
    assert spider.foo == "1"


def test_no_params():
    class Params(BaseModel):
        pass

    class ParamSpider(Args[Params], Spider):
        name = "params"

    spider = get_spider(ParamSpider, kwargs={"foo": "1"})
    assert isinstance(spider.args, Params)
    assert ParamSpider.get_param_schema() == {
        "properties": {},
        "title": "Params",
        "type": "object",
    }


def test_schema():
    class ParamSpider(Args[Params], Spider):
        name = "params"

    schema = ParamSpider.get_param_schema()
    try:
        expected_schema = Params.model_json_schema()
    except AttributeError:  # pydantic 1.x
        expected_schema = Params.schema()
    assert schema == expected_schema


def test_validate():
    class Params(BaseModel):
        foo: bool

    class ParamSpider(Args[Params], Spider):
        name = "params"

    with raises(ValidationError):
        get_spider(ParamSpider, kwargs={"foo": "2"})
