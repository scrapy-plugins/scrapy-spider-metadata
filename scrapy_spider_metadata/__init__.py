__version__ = "0.0.0"

from collections.abc import Mapping
from enum import Enum

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


def _unwrap_allof(value, defs, /):
    allof = value.pop("allOf", None)
    if allof is None:
        return
    for entry in allof:
        ref = entry.pop("$ref", None)
        if ref:
            def_id = ref.rsplit("/", maxsplit=1)[1]
            entry.update(defs[def_id])
        if "type" in value and "type" in entry:
            new_type = entry.pop("type")
            value["type"] = [value["type"], new_type]
        entry.pop("title", None)
        value.update(entry)


def _normalize_enum_meta_keys(value, /):
    enum_meta = value.get("enumMeta", None)
    if not enum_meta:
        return
    for key in list(enum_meta.keys()):
        if not isinstance(key, Enum):
            continue
        enum_meta[key.value] = enum_meta.pop(key)


def _post_process_param_schema(param_schema):
    defs = param_schema.pop("$defs", None)
    params = param_schema.get("properties", None)
    if not params:
        return
    for value in params.values():
        _unwrap_allof(value, defs)
        _normalize_enum_meta_keys(value)


def get_spider_param_schema(spidercls, /):
    param_model = _load_param_model(spidercls)
    param_schema = param_model.model_json_schema()
    # TODO: Consider achieving the same using a custom GenerateJsonSchema
    # subclass and passing it to `model_json_schema()` above.
    _post_process_param_schema(param_schema)
    return param_schema


def parse_spider_kwargs(spider, kwargs, /):
    param_model = _load_param_model(spider.__class__)
    if param_model is None:
        return kwargs
    parsed_params = param_model(**kwargs)
    return parsed_params.model_dump()
