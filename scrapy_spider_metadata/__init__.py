__version__ = "0.0.0"

from collections.abc import Mapping

from pydantic import BaseModel


def _is_subclass(cls, parent):
    try:
        return issubclass(cls, parent)
    except TypeError:
        return False


def parse_spider_kwargs(spider, kwargs):
    meta = getattr(spider, "meta", None)
    if not isinstance(meta, Mapping):
        return kwargs
    param_model = meta.get("params", None)
    if not param_model:
        return kwargs
    if not _is_subclass(param_model, BaseModel):
        spidercls = spider.__class__
        spider_import_path = f"{spidercls.__module__}.{spidercls.__qualname__}"
        raise ValueError(
            f'{spider_import_path}.meta["params"] is not a subclass of '
            f"pydantic.BaseModel"
        )
    parsed_params = param_model(**kwargs)
    return parsed_params.model_dump()
