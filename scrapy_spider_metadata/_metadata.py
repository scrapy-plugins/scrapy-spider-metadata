from typing import Any, Dict, Type

from scrapy import Spider

from scrapy_spider_metadata._params import Args

ATTR_NAME = "metadata"


def get_metadata_for_spider(spider_cls: Type[Spider]) -> Dict[str, Any]:
    """Return the metadata for the spider class.

    :param spider_cls: The spider class.
    :return: The complete spider metadata.
    """
    base_metadata = getattr(spider_cls, ATTR_NAME, {})
    if issubclass(spider_cls, Args):
        param_schema = spider_cls.get_param_schema()
    else:
        param_schema = {}
    result = base_metadata.copy()
    result["param_schema"] = param_schema
    return result
