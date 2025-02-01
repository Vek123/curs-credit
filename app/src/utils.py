import contextlib
import datetime
import json
from typing import Awaitable

from aiohttp import ClientSession

from schemas import UserOut
from settings import settings


@contextlib.asynccontextmanager
async def get_session() -> ClientSession:
    token = get_auth_token()
    token_header = f"Bearer {token}"
    async with ClientSession(
            base_url=settings.api_base_url, headers={"Authorization": token_header}
    ) as session:
        yield session


def get_auth_token() -> str:
    with open(settings.project_root / "auth_token", "r") as file:
        return file.read().strip()


def set_auth_token(token: str) -> None:
    with open(settings.project_root / "auth_token", "w") as file:
        file.write(token)


# def get_local_user() -> UserOut | None:
#     with open(settings.project_root / "user.json", "r") as file:
#         user_dict = json.load(file)
#         user_dict["birthday"] = datetime.datetime.fromisoformat(user_dict["birthday"])
#         if user_dict:
#             return UserOut.model_validate(user_dict)
#
#
# def set_local_user(user: UserOut | None) -> None:
#     with open(settings.project_root / "user.json", "w") as file:
#         if user:
#             user_dict = user.model_dump()
#             user_dict["birthday"] = user_dict["birthday"].isoformat()
#             file.write(json.dumps(user_dict))
#         else:
#             file.write("")
