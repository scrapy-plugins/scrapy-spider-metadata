__version__ = "0.0.0"

from collections.abc import Mapping

from pydantic import BaseModel


def _is_subclass(cls, parent):
    try:
        return issubclass(cls, parent)
    except TypeError:
        return False


def _load_param_model(spidercls, /):
    meta = getattr(spidercls, "meta", None)
    if not isinstance(meta, Mapping):
        return None
    param_model = meta.get("params", None)
    if not param_model:
        return None
    if not _is_subclass(param_model, BaseModel):
        spider_import_path = f"{spidercls.__module__}.{spidercls.__qualname__}"
        raise ValueError(
            f'{spider_import_path}.meta["params"] is not a subclass of '
            f"pydantic.BaseModel"
        )
    return param_model


def get_spider_param_schema(spidercls, /):
    param_model = _load_param_model(spidercls)
    return param_model.model_json_schema()


def parse_spider_kwargs(spider, kwargs, /):
    param_model = _load_param_model(spider.__class__)
    if param_model is None:
        return kwargs
    parsed_params = param_model(**kwargs)
    return parsed_params.model_dump()
