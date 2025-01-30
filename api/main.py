import contextlib
from typing import AsyncIterator

import uvicorn
from fastapi import FastAPI

from db import db_manager
from users import current_active_user, fastapi_users
from schemas import UserRead, UserCreate, UserUpdate
from settings import settings
from users import auth_backend


@contextlib.asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator:
    db_manager.init(settings.db_url)
    yield
    await db_manager.close()

app = FastAPI(
    title="Credit API",
    lifespan=lifespan,
)

app.include_router(
    fastapi_users.get_auth_router(auth_backend), prefix="/auth/jwt", tags=["auth"]
)
app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_verify_router(UserRead),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)


if __name__ == "__main__":
    try:
        uvicorn.run(app, host=settings.app_host, port=settings.app_port)
    except (RuntimeError, KeyboardInterrupt):
        pass
