from typing import Any, Dict, Type

from scrapy import Spider

from scrapy_spider_metadata._params import Args

ATTR_NAME = "metadata"


def get_spider_metadata(
    spider_cls: Type[Spider], *, normalize: bool = False
) -> Dict[str, Any]:
    """Return the metadata for the spider class.

    Return a copy of the ``metadata`` dict. If the spider class defines
    :ref:`spider parameters <params>`, the returned dict will have an
    additional ``param_schema`` key which value is the :ref:`JSON Schema
    <params-schema>` for the parameters.

    :param spider_cls: The spider class.
    :param normalize: Normalize the returned schema.
    :return: The complete spider metadata.
    """
    base_metadata = getattr(spider_cls, ATTR_NAME, {})
    result = base_metadata.copy()
    if issubclass(spider_cls, Args):
        result["param_schema"] = spider_cls.get_param_schema(normalize=normalize)
    return result
