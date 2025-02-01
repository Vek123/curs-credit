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

    async def register(self, user: UserIn) -> bool | str:
        async with get_session() as session:
            user_dict = user.model_dump()
            user_dict["birthday"] = user_dict["birthday"].strftime("%Y-%d-%m")
            async with session.post(
                    "auth/register/", json=user_dict,
            ) as response:
                if response.status == 201:
                    return True
                error = (await response.json()).get(
                    "detail",
                    "Возникла ошибка при регистрации",
                )
                if error == "REGISTER_USER_ALREADY_EXISTS":
                    return "Такой пользователь уже существует"
                elif isinstance(error, dict) and error.get("code", "") == "REGISTER_INVALID_PASSWORD":
                    return "Длина пароля должна быть не менее 3 символов"
                return error

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
