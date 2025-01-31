from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, update
from sqlalchemy.orm import joinedload, contains_eager
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError, NoResultFound

from db import get_session
from models import *
from users import current_active_user
from utils import specs_route
from schemas import *
from services import *

router = APIRouter()


### ORDER
@router.post("/orders", responses={404: {"model": APIException}})
async def create_order(
        order_service: Annotated[OrderService, Depends()],
        order: OrderIn,
) -> OrderOutRel:
    return await order_service.create(order)


@specs_route
@router.get("/orders")
async def list_orders(
        order_service: Annotated[OrderService, Depends()],
) -> list[OrderOutRel]:
    return await order_service.list()


@specs_route
@router.get("/orders/{order_id}", responses={404: {"model": APIException}})
async def get_order(
        order_service: Annotated[OrderService, Depends()],
        order_id: int,
) -> OrderOutRel:
    return await order_service.get(order_id)


@specs_route
@router.patch("/orders/{order_id}", responses={404: {"model": APIException}})
async def patch_order(
        order_service: Annotated[OrderService, Depends()],
        order_id: int,
        status: str,
        active: bool,
) -> OrderOutRel:
    return await order_service.change_status(order_id, status, active)


### RESPONSE
@specs_route
@router.post(
    "/responses",
    responses={404: {"model": APIException}, 409: {"model": APIException}}
)
async def create_response(
        order_service: Annotated[OrderService, Depends()],
        response_service: Annotated[ResponseService, Depends()],
        response: ResponseIn,
) -> ResponseOutRel:
    created_response_pydantic = await response_service.create(response)
    await order_service.change_status(
        created_response_pydantic.order.id, "Обработан", False
    )

    return created_response_pydantic


@router.get("/responses")
async def list_responses(
        response_service: Annotated[ResponseService, Depends()],
) -> list[ResponseOutRel]:
    return await response_service.list()


@specs_route
@router.post("/credits")
async def create_credit(
        credit_service: Annotated[CreditService, Depends()],
        credit: CreditIn
) -> CreditOut:
    return await credit_service.create(credit)


@router.get("/credits")
async def list_credits(
        credit_service: Annotated[CreditService, Depends()],
) -> list[CreditOut]:
    return await credit_service.list()


@router.get("/credits/{credit_id}", responses={404: {"model": APIException}})
async def get_credits(
        credit_service: Annotated[CreditService, Depends()],
        credit_id: int,
) -> CreditOut:
    return await credit_service.get(credit_id)
