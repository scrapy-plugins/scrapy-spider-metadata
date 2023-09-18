from enum import Enum
from typing import Any, Dict, Generic, TypeVar

from ._utils import get_generic_param


def _is_subclass(cls, parent):
    try:
        return issubclass(cls, parent)
    except TypeError:
        return False


def _load_param_model(spidercls, /):
    return get_generic_param(spidercls, Parametrized)


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


def _update_old_pydantic(value, /):
    extra = value.pop("json_schema_extra", None)
    if extra:
        value.update(extra)

    if "enum" in value:
        default = value.get("default", None)
        if default is not None:
            value["default"] = default.value


def _post_process_param_schema(param_schema):
    defs = param_schema.pop("$defs", None)
    params = param_schema.get("properties", None)
    if not params:
        return
    for value in params.values():
        _update_old_pydantic(value)
        _unwrap_allof(value, defs)
        _normalize_enum_meta_keys(value)


def _parse_spider_kwargs(spidercls, kwargs, /):
    param_model = _load_param_model(spidercls)
    if param_model is None:
        return kwargs
    parsed_params = param_model(**kwargs)
    try:
        return parsed_params.model_dump()
    except AttributeError:  # pydantic 1.x
        return parsed_params.dict()


ParamSpecT = TypeVar("ParamSpecT")


class Parametrized(Generic[ParamSpecT]):
    """Validates and type-converts spider arguments according to :ref:`spider
    parameters <define-params>`.

    This is done before they reach the ``__init__`` method of
    :class:`~scrapy.spiders.Spider`, which is the method that then assigns the
    spider arguments to class variables on the spider instance.
    """

    def __init__(self, *args, **kwargs):
        kwargs = _parse_spider_kwargs(self.__class__, kwargs)
        super().__init__(*args, **kwargs)

    @classmethod
    def get_param_schema(cls) -> Dict[Any, Any]:
        """:class:`dict` with the :ref:`parameter definition <define-params>`
        of *spidercls* as `JSON Schema`_.

        .. _JSON Schema: https://json-schema.org/
        """
        param_model = _load_param_model(cls)
        try:
            param_schema = param_model.model_json_schema()
        except AttributeError:  # pydantic 1.x
            param_schema = param_model.schema()
        # TODO: Consider achieving the same using a custom GenerateJsonSchema
        # subclass and passing it to `model_json_schema()` above.
        _post_process_param_schema(param_schema)
        return param_schema
