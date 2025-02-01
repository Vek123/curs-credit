from schemas import *
from utils import set_auth_token, get_session


class AuthService(object):
    async def is_authorized(self) -> bool:
        async with get_session() as session:
            async with session.get("api/check/") as response:
                if response.status == 200:
                    return True
                return False

    async def is_spec(self) -> bool:
        async with get_session() as session:
            async with session.get("api/check-spec/") as response:
                if response.status == 200:
                    return True
                return False

    async def register(self, user: UserIn) -> bool:
        async with get_session() as session:
            async with session.post(
                    "auth/jwt/register/", data=user.model_dump()
            ) as response:
                print(await response.json())
                if response.status == 201:
                    return True
                return False

    async def login(self, creds: UserCreds) -> bool:
        async with get_session() as session:
            async with session.post(
                    "auth/jwt/login/", data=creds.model_dump()
            ) as response:
                print(await response.json())
                if response.status == 200:
                    data = await response.json()
                    set_auth_token(data["access_token"])
                    return True
                set_auth_token("")
        return False

    async def logout(self):
        async with get_session() as session:
            async with session.post("auth/jwt/logout"):
                set_auth_token("")
