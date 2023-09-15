from enum import Enum, IntEnum

from pydantic import BaseModel, Field, ValidationError
from pytest import raises
from scrapy import Spider

from scrapy_spider_metadata import ParamSpiderMixin, get_spider_param_schema

from . import get_spider


def test_mixin_convert():
    class Params(BaseModel):
        foo: int

    class ParamSpider(ParamSpiderMixin, Spider):
        name = "params"
        meta = {
            "params": Params,
        }

    spider = get_spider(ParamSpider, kwargs={"foo": "1"})
    assert spider.foo == 1


def test_mixin_validate():
    class Params(BaseModel):
        foo: bool

    class ParamSpider(ParamSpiderMixin, Spider):
        name = "params"
        meta = {
            "params": Params,
        }

    with raises(ValidationError):
        get_spider(ParamSpider, kwargs={"foo": "2"})


def test_schema():
    pattern = r"^(\\([0-9]{3}\\))?[0-9]{3}-[0-9]{4}$"

    class FruitEnum(str, Enum):
        pear = "pear"
        banana = "banana"

    class ToolEnum(IntEnum):
        spanner = 1
        wrench = 2

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
        fruit: FruitEnum = Field(
            title="Fruit",
            json_schema_extra={
                "enumMeta": {
                    FruitEnum.pear: {
                        "title": "Pear",
                        "description": "Pyrus fruit",
                    },
                    FruitEnum.banana: {
                        "title": "Banana",
                        "description": "Love fruit",
                    },
                },
            },
        )
        tool: ToolEnum = ToolEnum.wrench
        # TODO: Cover nullable values.

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
            "fruit": {
                "title": "Fruit",
                "type": "string",
                "enum": ["pear", "banana"],
                "enumMeta": {
                    "pear": {
                        "title": "Pear",
                        "description": "Pyrus fruit",
                    },
                    "banana": {
                        "title": "Banana",
                        "description": "Love fruit",
                    },
                },
            },
            "tool": {
                "type": "integer",
                "enum": [1, 2],
                "default": 2,
            },
        },
        "required": ["number_without_default", "phone", "yesno", "fruit"],
        "title": "Params",
        "type": "object",
    }
