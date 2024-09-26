from enum import Enum, IntEnum
from typing import TYPE_CHECKING, Any, Dict, Optional, Type, cast

import pytest
from packaging import version
from pydantic import BaseModel, Field, ValidationError
from pydantic.version import VERSION as PYDANTIC_VERSION
from pytest import raises
from scrapy import Spider

from scrapy_spider_metadata import Args, get_spider_metadata

from . import get_spider

if TYPE_CHECKING:
    from pydantic.config import JsonDict


class Params(BaseModel):
    foo: int


class ParamSpider(Args[Params], Spider):
    name = "params"


def get_expected_schema(params: Type[BaseModel]) -> Dict[str, Any]:
    try:
        return params.model_json_schema()
    except AttributeError:  # pydantic 1.x
        return params.schema()


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
    assert ParamSpider.get_param_schema(normalize=True) == {
        "properties": {},
        "title": "Params",
        "type": "object",
    }


PATTERN = r"^(\\([0-9]{3}\\))?[0-9]{3}-[0-9]{4}$"
USING_PYDANTIC_1 = version.parse(str(PYDANTIC_VERSION)) < version.parse("2")
USING_PYDANTIC_29 = version.parse(str(PYDANTIC_VERSION)) >= version.parse("2.9")


@pytest.mark.parametrize(
    "normalize,expected_schema",
    [
        # Expectations for Pydantic 2.9+
        pytest.param(
            False,
            {
                "$defs": {
                    "DessertEnum": {
                        "enum": ["cake", "cookie"],
                        "title": "DessertEnum",
                        "type": "string",
                    },
                    "FruitEnum": {
                        "enum": ["pear", "banana"],
                        "title": "FruitEnum",
                        "type": "string",
                    },
                    "ToolEnum": {
                        "enum": [1, 2],
                        "title": "ToolEnum",
                        "type": "integer",
                    },
                    "WaterEnum": {
                        "enum": ["still", "sparkling"],
                        "title": "WaterEnum",
                        "type": "string",
                    },
                },
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
                    "int_optional": {
                        "title": "Int Optional",
                        "anyOf": [{"type": "integer"}, {"type": "null"}],
                        "default": None,
                    },
                    "int_optional_without_default": {
                        "title": "Int Optional Without Default",
                        "anyOf": [{"type": "integer"}, {"type": "null"}],
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
                        "pattern": PATTERN,
                    },
                    "yesno": {
                        "title": "Yesno",
                        "type": "boolean",
                    },
                    "fruit": {
                        "$ref": "#/$defs/FruitEnum",
                        "title": "Fruit name",
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
                        "$ref": "#/$defs/ToolEnum",
                        "default": 2,
                    },
                    "water": {
                        "$ref": "#/$defs/WaterEnum",
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
                    "dessert_optional": {
                        "anyOf": [{"$ref": "#/$defs/DessertEnum"}, {"type": "null"}],
                        "default": None,
                    },
                    "dessert_required": {
                        "$ref": "#/$defs/DessertEnum",
                    },
                },
                "required": [
                    "int_optional_without_default",
                    "number_without_default",
                    "phone",
                    "yesno",
                    "fruit",
                    "water",
                    "dessert_required",
                ],
                "title": "Params",
                "type": "object",
            },
            marks=pytest.mark.skipif(
                not USING_PYDANTIC_29, reason="Expectations for Pydantic 2.9+"
            ),
        ),
        # Expectations for Pydantic 2.0-2.8
        pytest.param(
            False,
            {
                "$defs": {
                    "DessertEnum": {
                        "enum": ["cake", "cookie"],
                        "title": "DessertEnum",
                        "type": "string",
                    },
                    "FruitEnum": {
                        "enum": ["pear", "banana"],
                        "title": "FruitEnum",
                        "type": "string",
                    },
                    "ToolEnum": {
                        "enum": [1, 2],
                        "title": "ToolEnum",
                        "type": "integer",
                    },
                    "WaterEnum": {
                        "enum": ["still", "sparkling"],
                        "title": "WaterEnum",
                        "type": "string",
                    },
                },
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
                    "int_optional": {
                        "title": "Int Optional",
                        "anyOf": [{"type": "integer"}, {"type": "null"}],
                        "default": None,
                    },
                    "int_optional_without_default": {
                        "title": "Int Optional Without Default",
                        "anyOf": [{"type": "integer"}, {"type": "null"}],
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
                        "pattern": PATTERN,
                    },
                    "yesno": {
                        "title": "Yesno",
                        "type": "boolean",
                    },
                    "fruit": {
                        "allOf": [{"$ref": "#/$defs/FruitEnum"}],
                        "title": "Fruit name",
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
                        "allOf": [{"$ref": "#/$defs/ToolEnum"}],
                        "default": 2,
                    },
                    "water": {
                        "allOf": [{"$ref": "#/$defs/WaterEnum"}],
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
                    "dessert_optional": {
                        "anyOf": [{"$ref": "#/$defs/DessertEnum"}, {"type": "null"}],
                        "default": None,
                    },
                    "dessert_required": {
                        "$ref": "#/$defs/DessertEnum",
                    },
                },
                "required": [
                    "int_optional_without_default",
                    "number_without_default",
                    "phone",
                    "yesno",
                    "fruit",
                    "water",
                    "dessert_required",
                ],
                "title": "Params",
                "type": "object",
            },
            marks=pytest.mark.skipif(
                USING_PYDANTIC_1 or USING_PYDANTIC_29,
                reason="Expectations for Pydantic 2.0-2.8",
            ),
        ),
        # Expectations for Pydantic 1.x
        pytest.param(
            False,
            {
                "definitions": {
                    "DessertEnum": {
                        "enum": ["cake", "cookie"],
                        "title": "DessertEnum",
                        "description": "An enumeration.",
                        "type": "string",
                    },
                    "FruitEnum": {
                        "enum": ["pear", "banana"],
                        "title": "FruitEnum",
                        "description": "An enumeration.",
                        "type": "string",
                    },
                    "ToolEnum": {
                        "enum": [1, 2],
                        "title": "ToolEnum",
                        "description": "An enumeration.",
                        "type": "integer",
                    },
                    "WaterEnum": {
                        "enum": ["still", "sparkling"],
                        "title": "WaterEnum",
                        "description": "An enumeration.",
                        "type": "string",
                    },
                },
                "properties": {
                    "field": {
                        "title": "A Team",
                        "description": "This is a description of the A team.",
                        "type": "integer",
                        "json_schema_extra": {"foo": "bar"},
                        "default": 0,
                    },
                    "int_with_default": {
                        "title": "Int With Default",
                        "type": "integer",
                        "default": 1,
                    },
                    "int_optional": {
                        "title": "Int Optional",
                        "type": "integer",  # https://github.com/pydantic/pydantic/issues/1270
                    },
                    "int_optional_without_default": {
                        "title": "Int Optional Without Default",
                        "type": "integer",  # https://github.com/pydantic/pydantic/issues/1270
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
                        "pattern": PATTERN,
                    },
                    "yesno": {
                        "title": "Yesno",
                        "type": "boolean",
                    },
                    "fruit": {
                        "allOf": [{"$ref": "#/definitions/FruitEnum"}],
                        "title": "Fruit name",
                        "json_schema_extra": {
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
                    },
                    "tool": {
                        "allOf": [{"$ref": "#/definitions/ToolEnum"}],
                        "default": 2,
                    },
                    "water": {
                        "allOf": [{"$ref": "#/definitions/WaterEnum"}],
                        "json_schema_extra": {
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
                    "dessert_optional": {
                        "$ref": "#/definitions/DessertEnum",
                    },
                    "dessert_required": {
                        "$ref": "#/definitions/DessertEnum",
                    },
                },
                "required": [
                    "number_without_default",
                    "phone",
                    "yesno",
                    "fruit",
                    "water",
                    "dessert_required",
                ],
                "title": "Params",
                "type": "object",
            },
            marks=pytest.mark.skipif(
                not USING_PYDANTIC_1, reason="Expectations for Pydantic 1.x"
            ),
        ),
        # Normalized
        (
            True,
            {
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
                    "int_optional": (
                        {
                            "title": "Int Optional",
                            "anyOf": [{"type": "integer"}, {"type": "null"}],
                            "default": None,
                        }
                        if not USING_PYDANTIC_1
                        else {
                            "title": "Int Optional",
                            "type": "integer",
                        }
                    ),
                    "int_optional_without_default": (
                        {
                            "title": "Int Optional Without Default",
                            "anyOf": [{"type": "integer"}, {"type": "null"}],
                        }
                        if not USING_PYDANTIC_1
                        else {
                            "title": "Int Optional Without Default",
                            "type": "integer",
                        }
                    ),
                    "number_without_default": {
                        "title": "Number Without Default",
                        "type": "number",
                    },
                    "phone": {
                        "title": "Phone",
                        "type": "string",
                        "minLength": 3,
                        "maxLength": 100,
                        "pattern": PATTERN,
                    },
                    "yesno": {
                        "title": "Yesno",
                        "type": "boolean",
                    },
                    "fruit": {
                        "title": "Fruit name",
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
                        "title": "Tool",
                        "type": "integer",
                        "enum": [1, 2],
                        "default": 2,
                    },
                    "water": {
                        "title": "Water",
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
                    "dessert_optional": (
                        {
                            "title": "Dessert Optional",
                            "enum": ["cake", "cookie"],
                            "anyOf": [{"type": "string"}, {"type": "null"}],
                            "default": None,
                        }
                        if not USING_PYDANTIC_1
                        else {
                            "title": "Dessert Optional",
                            "enum": ["cake", "cookie"],
                            "type": "string",
                        }
                    ),
                    "dessert_required": {
                        "title": "Dessert Required",
                        "enum": ["cake", "cookie"],
                        "type": "string",
                    },
                },
                "required": (
                    [
                        "int_optional_without_default",
                    ]
                    if not USING_PYDANTIC_1
                    else []
                )
                + [
                    "number_without_default",
                    "phone",
                    "yesno",
                    "fruit",
                    "water",
                    "dessert_required",
                ],
                "title": "Params",
                "type": "object",
            },
        ),
    ],
)
def test_schema(normalize, expected_schema):
    class FruitEnum(str, Enum):
        pear = "pear"
        banana = "banana"

    class ToolEnum(IntEnum):
        spanner = 1
        wrench = 2

    class WaterEnum(str, Enum):
        still = "still"
        sparkling = "sparkling"

    class DessertEnum(str, Enum):
        cake = "cake"
        cookie = "cookie"

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
        int_optional: Optional[int] = None
        int_optional_without_default: Optional[int]
        number_without_default: float
        phone: str = Field(
            min_length=3,
            max_length=100,
            pattern=PATTERN,
            # pydantic 1.x
            # https://github.com/pydantic/pydantic/issues/3753#issuecomment-1060850457
            default=...,
        )
        yesno: bool
        fruit: FruitEnum = Field(
            title="Fruit name",
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
        dessert_optional: Optional[DessertEnum] = None
        dessert_required: DessertEnum

    class ParamSpider(Args[Params], Spider):
        name = "params"

    schema = ParamSpider.get_param_schema(normalize=normalize)
    assert schema == expected_schema

    schema = get_spider_metadata(ParamSpider, normalize=normalize)["param_schema"]
    assert schema == expected_schema


def test_validate(caplog):
    class Params(BaseModel):
        foo: bool

    class ParamSpider(Args[Params], Spider):
        name = "params"

    caplog.clear()
    with raises(ValidationError):
        get_spider(ParamSpider, kwargs={"foo": "2"})
    assert "Spider parameter validation failed:" in caplog.text


def test_param_subclass_set_default():
    class ParentParams(BaseModel):
        a: str = Field()

    class Params(ParentParams):
        a: str = "b"

    class ParamSpider(Args[Params], Spider):
        name = "params"

    schema = ParamSpider.get_param_schema()
    assert schema == {
        "type": "object",
        "title": "Params",
        "properties": {"a": {"default": "b", "title": "A", "type": "string"}},
    }


def test_param_subclass_unset_default():
    try:
        from pydantic.fields import PydanticUndefined
    except ImportError:
        pytest.skip("No pydantic.fields.PydanticUndefined")

    class ParentParams(BaseModel):
        a: str = Field(default="b")

    class Params(ParentParams):
        a: str = PydanticUndefined  # type: ignore[assignment]

    class ParamSpider(Args[Params], Spider):
        name = "params"

    schema = ParamSpider.get_param_schema()
    assert schema == {
        "type": "object",
        "title": "Params",
        "properties": {"a": {"title": "A", "type": "string"}},
        "required": ["a"],
    }


def test_param_subclass_reword_description():
    class ParentParams(BaseModel):
        a: str = Field(description="Parent description")

    class Params(ParentParams):
        a: str = Field(  # type: ignore[misc]
            **{**ParentParams.schema()["properties"]["a"], "description": "Description"}
        )

    class ParamSpider(Args[Params], Spider):
        name = "params"

    schema = ParamSpider.get_param_schema()
    assert schema == {
        "type": "object",
        "title": "Params",
        "properties": {
            "a": {"title": "A", "type": "string", "description": "Description"}
        },
        "required": ["a"],
    }


@pytest.mark.skipif(USING_PYDANTIC_1, reason="Requires Pydantic 2.x")
def test_subclass_config_extension():
    from pydantic import ConfigDict

    class ParentParams(BaseModel):
        model_config = ConfigDict(
            json_schema_extra={
                "a": "b",
            },
        )

    class Params(ParentParams):
        model_config = {
            **ParentParams.model_config,
            **ConfigDict(
                json_schema_extra={
                    **cast(
                        "JsonDict",
                        ParentParams.model_config.get("json_schema_extra", {}),
                    ),
                    "c": "d",
                }
            ),
        }

    class ParamSpider(Args[Params], Spider):
        name = "params"

    schema = ParamSpider.get_param_schema()
    assert schema == {
        "type": "object",
        "title": "Params",
        "properties": {},
        "a": "b",
        "c": "d",
    }
