from typing import Optional

from fastapi import APIRouter

from schemas import APIException
from utils import specs_route
from users import current_active_user
from services import *
from models import User

router = APIRouter()


### ORDER
@router.post("/orders", responses={404: {"model": APIException}, 409: {"model": APIException}})
async def create_order(
        order_service: Annotated[OrderService, Depends()],
        user: Annotated[User, Depends(current_active_user)],
        order: OrderIn,
) -> OrderOutRel:
    if not user.is_spec and order.user_id != user.id:
        raise HTTPException(409)
    return await order_service.create(order)


@router.get("/orders")
async def list_orders(
        order_service: Annotated[OrderService, Depends()],
        user: Annotated[User, Depends(current_active_user)],
        new: Optional[bool] = None,
        user_id: Optional[int] = None,
        personal: Optional[bool] = None,
) -> list[OrderOutRel]:
    current_user_id = None
    if not user.is_spec or personal is not None:
        current_user_id = user.id
    elif user_id is not None:
        current_user_id = user_id
    if new is None:
        return await order_service.list(current_user_id)
    else:
        return await order_service.list_new(current_user_id)


@router.get("/orders/{order_id}", responses={404: {"model": APIException}})
async def get_order(
        order_service: Annotated[OrderService, Depends()],
        user: Annotated[User, Depends(current_active_user)],
        order_id: int,
) -> OrderOutRel:
    current_user_id = None
    if not user.is_spec:
        current_user_id = user.id
    return await order_service.get(order_id, current_user_id)


@router.patch("/orders/{order_id}", responses={404: {"model": APIException}})
async def patch_order(
        order_service: Annotated[OrderService, Depends()],
        user: Annotated[User, Depends(current_active_user)],
        order_id: int,
        status: str,
        new: bool,
) -> OrderOutRel:
    return await order_service.change_status(order_id, status, new)


### RESPONSE
@router.post(
    "/responses",
    responses={404: {"model": APIException}, 409: {"model": APIException}}
)
@specs_route
async def create_response(
        response_service: Annotated[ResponseService, Depends()],
        user: Annotated[User, Depends(current_active_user)],
        response: ResponseIn,
) -> ResponseOutRel:
    created_response_pydantic = await response_service.create(response)

    return created_response_pydantic


@router.get("/responses")
async def list_responses(
        response_service: Annotated[ResponseService, Depends()],
        user: Annotated[User, Depends(current_active_user)],
) -> list[ResponseOutRel]:
    current_user = None
    if not user.is_spec:
        current_user = user.id
    return await response_service.list(current_user)


### CREDITS
@router.post("/credits", responses={409: {"models": APIException}})
async def create_credit(
        user: Annotated[User, Depends(current_active_user)],
        credit_service: Annotated[CreditService, Depends()],
        credit: CreditIn,
) -> CreditOutRel:
    if user.id != credit.user_id:
        raise HTTPException(401)
    return await credit_service.create(credit)


@router.get("/credits")
async def list_credits(
        credit_service: Annotated[CreditService, Depends()],
        user: Annotated[User, Depends(current_active_user)],
) -> list[CreditOutRel]:
    current_user = None
    if not user.is_spec:
        current_user = user.id
    return await credit_service.list(current_user)


@router.get("/credits/{credit_id}", responses={404: {"model": APIException}})
async def get_credit(
        credit_service: Annotated[CreditService, Depends()],
        user: Annotated[User, Depends(current_active_user)],
        credit_id: int,
        user_id: Optional[int] = None,
        personal: Optional[bool] = None,
) -> CreditOutRel:
    current_user = None
    if not user.is_spec or personal:
        current_user = user.id
    elif user_id is not None:
        current_user = user_id
    return await credit_service.get(credit_id, current_user)
