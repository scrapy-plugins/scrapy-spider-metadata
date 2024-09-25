import copy
from collections import deque
from typing import Any, Dict, Optional, Tuple, TypeVar, Union, get_args


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
    def get_def(ref: str) -> Dict[str, Any]:
        def_id = ref.rsplit("/", maxsplit=1)[1]
        return defs[def_id]

    extra = value.pop("json_schema_extra", None)
    if extra:
        # pydantic 1.x
        value.update(extra)

    allof = value.pop("allOf", None)
    if allof is not None:
        for entry in allof:
            ref = entry.pop("$ref", None)
            if ref:
                entry.update(get_def(ref))
            entry.pop("title", None)
            entry.pop("description", None)
            value.update(entry)

    anyof = value.get("anyOf")
    if anyof is not None:
        for entry in anyof:
            ref = entry.pop("$ref", None)
            if not ref:
                continue
            def_copy = copy.copy(get_def(ref))
            if "type" in def_copy:
                entry["type"] = def_copy.pop("type")
            def_copy.pop("title", None)
            def_copy.pop("description", None)
            value.update(def_copy)

    ref = value.pop("$ref", None)
    if ref:
        def_copy = copy.copy(get_def(ref))
        def_copy.pop("title", None)
        def_copy.pop("description", None)
        value.update(def_copy)

    if "title" not in value:
        value["title"] = key.title().replace("_", " ")


def normalize_param_schema(schema, /):
    params = schema.get("properties", None)
    if not params:
        return
    defs = schema.pop("$defs", None)
    if not defs:
        # pydantic 1.x
        defs = schema.pop("definitions", None)
    for key, value in params.items():
        _normalize_param(key, value, defs)
