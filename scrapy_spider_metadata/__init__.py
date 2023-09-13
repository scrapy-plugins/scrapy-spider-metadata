__version__ = "0.0.0"

from collections.abc import Mapping

from pydantic import BaseModel


def parse_spider_kwargs(spider, kwargs):
    meta = getattr(spider, "meta", None)
    if not isinstance(meta, Mapping):
        return kwargs
    param_model = meta.get("params", None)
    if not param_model:
        return kwargs

    assert issubclass(param_model, BaseModel)

    parsed_params = param_model(**kwargs)
    return parsed_params.model_dump()
