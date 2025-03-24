from __future__ import annotations

from typing import Any, TypeVar, cast

from scrapy import Spider
from scrapy.utils.test import get_crawler

_SpiderT = TypeVar("_SpiderT", bound=Spider)


def get_spider(
    spidercls: type[_SpiderT],
    settings: dict[str, Any] | None = None,
    kwargs: dict[str, Any] | None = None,
) -> _SpiderT:
    crawler = get_crawler(spidercls, settings or {})
    return cast("_SpiderT", crawler._create_spider(spidercls.name, **(kwargs or {})))
