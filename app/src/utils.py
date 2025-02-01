import contextlib

from aiohttp import ClientSession

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
