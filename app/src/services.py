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

    async def me(self) -> UserOut | None:
        async with get_session() as session:
            async with session.get("users/me") as response:
                if response.status == 200:
                    user_dict = await response.json()
                    return UserOut.model_validate(user_dict)
                return None


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

    async def list(self, user_id: int | None = None, personal: bool | None = None) -> List[OrderOutRel]:
        params = dict()
        if user_id is not None:
            params["user_id"] = user_id
        if personal is not None:
            params["personal"] = "true" if personal else "false"
        async with get_session() as session:
            async with session.get(
                    "api/v1/orders",
                    params=params,
            ) as response:
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
            ) as response:
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
                if response.status == 200:
                    response_dict = await response.json()
                    return ResponseOutRel.model_validate(response_dict)
        return None

    async def list(self) -> List[ResponseOutRel]:
        async with get_session() as session:
            async with session.get(
                "api/v1/responses",
            ) as response:
                if response.status == 200:
                    responses = await response.json()
                    return [ResponseOutRel.model_validate(resp) for resp in responses]
            return list()


class CreditsService(object):
    async def create(self, credit: CreditIn) -> CreditOutRel | None:
        credit_dict = credit.model_dump()
        credit_dict["next_pay_date"] = credit_dict["next_pay_date"].strftime("%Y-%m-%d")
        async with get_session() as session:
            async with session.post(
                "api/v1/credits",
                json=credit_dict,
            ) as response:
                if response.status == 200:
                    return CreditOutRel.model_validate(await response.json())
            return None

    async def get(self, credit_id: int) -> CreditOutRel | None:
        async with get_session() as session:
            async with session.get(
                f"api/v1/credits/{credit_id}"
            ) as response:
                if response.status == 200:
                    return CreditOutRel.model_validate(await response.json())
            return None

    async def list(
            self,
            user_id: int | None = None,
            personal: bool | None = None,
    ) -> List[CreditOutRel]:
        params = {}
        if user_id is not None:
            params["user_id"] = user_id
        if personal is not None:
            params["personal"] = personal
        async with get_session() as session:
            async with session.get(
                f"api/v1/credits",
            ) as response:
                if response.status == 200:
                    credits = await response.json()
                    return [CreditOutRel.model_validate(cred) for cred in credits]
        return list()
