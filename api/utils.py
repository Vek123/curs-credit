from functools import wraps
from typing import Callable

from fastapi import HTTPException

from models import User


def specs_route(func: Callable):
    @wraps(func)
    async def wrapper(*args, user: User | None = None, **kwargs):
        if user is None or not user.is_spec:
            raise HTTPException(401)
        return await func(*args, **kwargs, user=user)
    return wrapper
