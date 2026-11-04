from dataclasses import dataclass
from typing import Any, Literal


@dataclass(frozen=True)
class FromSetting:
    name: str
    default: Any = None
    getter: Literal["get", "getint", "getbool", "getfloat"] = "get"
