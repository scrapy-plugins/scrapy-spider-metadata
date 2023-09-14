from pydantic import BaseModel, Field, ValidationError
from pytest import raises
from scrapy import Spider

from scrapy_spider_metadata import get_spider_param_schema, parse_spider_kwargs

from . import get_spider


def test_get_spider_param_schema():
    pattern = r"^(\\([0-9]{3}\\))?[0-9]{3}-[0-9]{4}$"

    class Params(BaseModel):
        field: int = Field(
            title="A Team",
            description="This is a description of the A team.",
            json_schema_extra={
                "foo": "bar",
            },
            default=0,
        )
        int_with_default: int = 1
        number_without_default: float
        phone: str = Field(
            min_length=3,
            max_length=100,
            pattern=pattern,
        )
        yesno: bool

    class ParamSpider(Spider):
        name = "params"
        meta = {
            "params": Params,
        }

    schema = get_spider_param_schema(ParamSpider)
    assert schema == {
        "properties": {
            "field": {
                "title": "A Team",
                "description": "This is a description of the A team.",
                "type": "integer",
                "foo": "bar",
                "default": 0,
            },
            "int_with_default": {
                "title": "Int With Default",
                "type": "integer",
                "default": 1,
            },
            "number_without_default": {
                "title": "Number Without Default",
                "type": "number",
            },
            "phone": {
                "title": "Phone",
                "type": "string",
                "minLength": 3,
                "maxLength": 100,
                "pattern": pattern,
            },
            "yesno": {
                "title": "Yesno",
                "type": "boolean",
            },
        },
        "required": ["number_without_default", "phone", "yesno"],
        "title": "Params",
        "type": "object",
    }


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
