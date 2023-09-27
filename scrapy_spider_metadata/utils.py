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


def _update_old_pydantic(value, /):
    extra = value.pop("json_schema_extra", None)
    if extra:
        value.update(extra)

    if "enum" in value:
        default = value.get("default", None)
        if default is not None:
            value["default"] = default.value


def normalize_param_schema(schema) -> None:
    """Changes the input JSON Schema to normalize it.

    Normalization includes:

    -   Removing some differences between Pydantic 1.x and Pydantic 2.x.

    -   Remove some uses of ``allOf`` + ``$defs`` in favor of a simpler sytnax.
    """
    defs = schema.pop("$defs", None)
    params = schema.get("properties", None)
    if not params:
        return
    for value in params.values():
        _update_old_pydantic(value)
        _unwrap_allof(value, defs)
