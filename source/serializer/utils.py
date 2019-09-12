from typing import Any


def is_typing(typing_instance: Any, typing_generic: Any) -> bool:
    origins_match = getattr(typing_instance, '__origin__', 1) is getattr(typing_generic, '__origin__', 2)
    instance_origin_match = getattr(typing_instance, '__origin__', 1) is typing_generic
    return origins_match or instance_origin_match
