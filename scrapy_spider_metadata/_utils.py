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
