from functools import wraps
from typing import Callable


def specs_route(func: Callable):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        return await func(*args, **kwargs)
    return wrapper
