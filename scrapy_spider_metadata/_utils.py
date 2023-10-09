import copy
from collections import deque
from typing import Optional, Tuple, TypeVar, Union, get_args


def get_generic_param(
    cls: type, expected: Union[type, Tuple[type, ...]]
) -> Optional[type]:
    """Search the base classes recursively breadth-first for a generic class and return its param.

    Returns the param of the first found class that is a subclass of ``expected``.
    """
    visited = set()
    queue = deque([cls])
    while queue:
        node = queue.popleft()
        visited.add(node)
        for base in getattr(node, "__orig_bases__", []):
            origin = getattr(base, "__origin__", None)
            if origin and issubclass(origin, expected):
                result = get_args(base)[0]
                if not isinstance(result, TypeVar):
                    return result
            queue.append(base)
    return None


def _normalize_param(key, value, defs, /):
    extra = value.pop("json_schema_extra", None)
    if extra:
        value.update(extra)

    allof = value.pop("allOf", None)
    if allof is not None:
        for entry in allof:
            ref = entry.pop("$ref", None)
            if ref:
                def_id = ref.rsplit("/", maxsplit=1)[1]
                entry.update(defs[def_id])
            entry.pop("title", None)
            value.update(entry)

    anyof = value.get("anyOf")
    if anyof is not None:
        for entry in anyof:
            ref = entry.pop("$ref", None)
            if not ref:
                continue
            def_id = ref.rsplit("/", maxsplit=1)[1]
            def_copy = copy.copy(defs[def_id])
            if "type" in def_copy:
                entry["type"] = def_copy.pop("type")
            def_copy.pop("title", None)
            value.update(def_copy)

    ref = value.pop("$ref", None)
    if ref:
        def_id = ref.rsplit("/", maxsplit=1)[1]
        value.update(defs[def_id])
        value.pop("title", None)

    if "title" not in value:
        value["title"] = key.title().replace("_", " ")


def normalize_param_schema(schema, /):
    params = schema.get("properties", None)
    if not params:
        return
    defs = schema.pop("$defs", None)
    for key, value in params.items():
        _normalize_param(key, value, defs)
