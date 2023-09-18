from enum import Enum, IntEnum

from packaging import version
from pydantic import BaseModel, Field, ValidationError
from pydantic.version import VERSION as PYDANTIC_VERSION
from pytest import raises
from scrapy import Spider

from scrapy_spider_metadata import Parameterized

from . import get_spider

USING_PYDANTIC_1 = version.parse(str(PYDANTIC_VERSION)) < version.parse("2")


def test_mixin_convert():
    class Params(BaseModel):
        foo: int

    class ParamSpider(Parameterized[Params], Spider):
        name = "params"

    spider = get_spider(ParamSpider, kwargs={"foo": "1"})
    assert spider.args.foo == 1
    assert spider.foo == "1"


def test_mixin_validate():
    class Params(BaseModel):
        foo: bool

    class ParamSpider(Parameterized[Params], Spider):
        name = "params"

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
            # pydantic 1.x
            # https://github.com/pydantic/pydantic/issues/3753#issuecomment-1060850457
            default=...,
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
            # pydantic 1.x
            # https://github.com/pydantic/pydantic/issues/3753#issuecomment-1060850457
            default=...,
        )
        tool: ToolEnum = ToolEnum.wrench
        # TODO: Cover nullable values.

    class ParamSpider(Parameterized[Params], Spider):
        name = "params"

    schema = ParamSpider.get_param_schema()
    expected_schema = {
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
    if USING_PYDANTIC_1:
        expected_schema["properties"]["tool"]["title"] = "Tool"
    assert schema == expected_schema
