from enum import Enum, IntEnum
from typing import Any, Dict, Generic, TypeVar

import pytest
from packaging import version
from pydantic import BaseModel, Field
from pydantic.version import VERSION as PYDANTIC_VERSION
from scrapy import Spider

from scrapy_spider_metadata import Args
from scrapy_spider_metadata._utils import get_generic_param
from scrapy_spider_metadata.utils import normalize_param_schema

ItemT = TypeVar("ItemT")


class Item:
    pass


class Item2:
    pass


class MyGeneric(Generic[ItemT]):
    pass


class MyGeneric2(Generic[ItemT]):
    pass


class Base(MyGeneric[ItemT]):
    pass


class BaseSpecialized(MyGeneric[Item]):
    pass


class BaseAny(MyGeneric):
    pass


class Derived(Base):
    pass


class Specialized(BaseSpecialized):
    pass


class SpecializedAdditionalClass(BaseSpecialized, Item2):
    pass


class SpecializedTwice(BaseSpecialized, Base[Item2]):
    pass


class SpecializedTwoGenerics(MyGeneric2[Item2], BaseSpecialized):
    pass


@pytest.mark.parametrize(
    ["cls", "param"],
    [
        (MyGeneric, None),
        (Base, None),
        (BaseAny, None),
        (Derived, None),
        (BaseSpecialized, Item),
        (Specialized, Item),
        (SpecializedAdditionalClass, Item),
        (SpecializedTwice, Item2),
        (SpecializedTwoGenerics, Item),
    ],
)
def test_get_generic_param(cls, param) -> None:
    assert get_generic_param(cls, expected=MyGeneric) == param


USING_PYDANTIC_1 = version.parse(str(PYDANTIC_VERSION)) < version.parse("2")


def test_normalize_param_schema():
    pattern = r"^(\\([0-9]{3}\\))?[0-9]{3}-[0-9]{4}$"

    class FruitEnum(str, Enum):
        pear = "pear"
        banana = "banana"

    class ToolEnum(IntEnum):
        spanner = 1
        wrench = 2

    class WaterEnum(str, Enum):
        still = "still"
        sparkling = "sparkling"

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
        water: WaterEnum = Field(
            json_schema_extra={
                "enumMeta": {
                    "still": {
                        "title": "Still water",
                    },
                    "sparkling": {
                        "title": "Sparkling water",
                        "video": "https://www.youtube.com/clip/UgkxxervFpv38ILyF_cZeHuat3sVNwmCy8pF",
                    },
                },
            },
            # pydantic 1.x
            # https://github.com/pydantic/pydantic/issues/3753#issuecomment-1060850457
            default=...,
        )
        # TODO: Cover nullable values.

    class ParamSpider(Args[Params], Spider):
        name = "params"

    schema = ParamSpider.get_param_schema()

    normalize_param_schema(schema)

    expected_schema: Dict[str, Any] = {
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
            "water": {
                "type": "string",
                "enum": ["still", "sparkling"],
                "enumMeta": {
                    "still": {
                        "title": "Still water",
                    },
                    "sparkling": {
                        "title": "Sparkling water",
                        "video": "https://www.youtube.com/clip/UgkxxervFpv38ILyF_cZeHuat3sVNwmCy8pF",
                    },
                },
            },
        },
        "required": ["number_without_default", "phone", "yesno", "fruit", "water"],
        "title": "Params",
        "type": "object",
    }
    if USING_PYDANTIC_1:
        expected_schema["properties"]["tool"]["title"] = "Tool"
        expected_schema["properties"]["water"]["title"] = "Water"
    assert schema == expected_schema


def test_normalize_param_schema_empty_input():
    schema: Dict[str, Any] = {}
    normalize_param_schema(schema)  # No exception raised.
    assert schema == {}
