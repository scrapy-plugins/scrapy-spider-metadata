from typing import Generic, TypeVar

import pytest

from scrapy_spider_metadata._utils import get_generic_param

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


class BaseAny(MyGeneric):  # type: ignore[type-arg]
    pass


class Derived(Base):  # type: ignore[type-arg]
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
    ("cls", "param"),
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
def test_get_generic_param(cls: type, param: type) -> None:
    assert get_generic_param(cls, expected=MyGeneric) == param
