from functools import wraps
from typing import Callable

from fastapi import HTTPException


def specs_route(func: Callable):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        user = kwargs.get("user", None)
        if user is None or not user.is_spec:
            raise HTTPException(401)
        return await func(*args, **kwargs)
    return wrapper
