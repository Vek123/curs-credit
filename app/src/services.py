from schemas import *
from utils import set_local_user, set_auth_token, get_session


class AuthService(object):
    async def is_authorized(self) -> bool:
        async with get_session() as session:
            async with session.get("api/check/") as response:
                print(await response.json())
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

    async def login(self, creds: UserCreds) -> UserOut | None:
        async with get_session() as session:
            async with session.post(
                    "auth/jwt/login/", data=creds.model_dump()
            ) as response:
                print(await response.json())
                if response.status != 200:
                    return
                token = await response.json()
                set_auth_token(token["access_token"])
        async with get_session() as session:
            async with session.get(
                    "users/me/", headers={"Authorization": f"Bearer {token["access_token"]}"}
            ) as response:
                print(await response.json())
                if response.status == 200:
                    user_pydantic = UserOut.model_validate((await response.json()))
                    set_local_user(user_pydantic)
                    return user_pydantic
        async with get_session() as session:
            async with session.post(
                    "auth/jwt/logout", headers={"Authorization": f"Bearer {token["access_token"]}"}
            ):
                pass

    async def logout(self):
        async with get_session() as session:
            async with session.post("auth/jwt/logout"):
                set_local_user(None)
                pass
