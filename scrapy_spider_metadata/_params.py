from enum import Enum
from typing import Any, Dict, Generic, TypeVar

from pydantic import BaseModel

from ._utils import get_generic_param


def _unwrap_allof(value, defs, /):
    allof = value.pop("allOf", None)
    if allof is None:
        return
    for entry in allof:
        ref = entry.pop("$ref", None)
        if ref:
            def_id = ref.rsplit("/", maxsplit=1)[1]
            entry.update(defs[def_id])
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


ParamSpecT = TypeVar("ParamSpecT")


class Parameterized(Generic[ParamSpecT]):
    """Validates and type-converts :ref:`spider arguments <spiderargs>` into
    the :attr:`args` instance attribute according to the :ref:`spider parameter
    specification <define-params>`.
    """

    def __init__(self, *args, **kwargs):
        param_model = get_generic_param(self.__class__, Parameterized)
        #: :ref:`Spider arguments <spiderargs>` parsed according to the
        #: :ref:`spider parameter specification <define-params>`.
        self.args: BaseModel = param_model(**kwargs)
        super().__init__(*args, **kwargs)

    @classmethod
    def get_param_schema(cls) -> Dict[Any, Any]:
        """Return a :class:`dict` with the :ref:`parameter definition
        <define-params>` as `JSON Schema`_.

        .. _JSON Schema: https://json-schema.org/
        """
        param_model = get_generic_param(cls, Parameterized)
        try:
            param_schema = param_model.model_json_schema()
        except AttributeError:  # pydantic 1.x
            param_schema = param_model.schema()
        # TODO: Consider achieving the same using a custom GenerateJsonSchema
        # subclass and passing it to `model_json_schema()` above.
        _post_process_param_schema(param_schema)
        return param_schema
