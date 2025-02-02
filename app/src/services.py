from typing import List

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
            user_dict["birthday"] = user_dict["birthday"].strftime("%Y-%m-%d")
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


class OrdersService(object):
    async def create(self, order: OrderIn) -> OrderOutRel | None:
        async with get_session() as session:
            async with session.post(
                    "api/v1/orders",
                    json=order.model_dump(),
            ) as response:
                if response.status == 200:
                    order_dict = await response.json()
                    return OrderOutRel.model_validate(order_dict)
        return None

    async def list(self) -> List[OrderOutRel]:
        async with get_session() as session:
            async with session.get("api/v1/orders") as response:
                if response.status == 200:
                    orders_list = await response.json()
                    return [OrderOutRel.model_validate(order) for order in orders_list]
        return list()

    async def list_new(self) -> List[OrderOutRel]:
        async with get_session() as session:
            async with session.get(
                    "api/v1/orders",
                    params={"new": "true"},
            ) as response:
                if response.status == 200:
                    orders_list = await response.json()
                    return [OrderOutRel.model_validate(order) for order in orders_list]
        return list()

    async def get(self, order_id: int) -> OrderOutRel | None:
        async with get_session() as session:
            async with session.get(f"api/v1/orders/{order_id}") as response:
                if response.status == 200:
                    order_dict = await response.json()
                    return OrderOutRel.model_validate(order_dict)
        return None

    async def patch_order(
            self,
            order_id: int,
            status: str,
            new: str = "true",
    ) -> OrderOutRel | None:
        async with get_session() as session:
            async with session.patch(
                    f"api/v1/orders/{order_id}?status={status}&new={new}",
            ) as response:)
                if response.status == 200:
                    order_dict = await response.json()
                    return OrderOutRel.model_validate(order_dict)
        return None


class ResponsesService(object):
    async def create(self, response: ResponseIn) -> ResponseOutRel | None:
        async with get_session() as session:
            async with session.post(
                "api/v1/responses",
                json=response.model_dump(),
            ) as response:
                print(response)
                if response.status == 200:
                    response_dict = await response.json()
                    return ResponseOutRel.model_validate(response_dict)
        return None

    async def list(self) -> List[ResponseOutRel]:
        async with get_session() as session:
            async with session.get(
                "api/v1/responses",
            ) as response:
                print(response)
                if response.status == 200:
                    responses = await response.json()
                    return [ResponseOutRel.model_validate(resp) for resp in responses]
            return list()
