from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, update
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError, NoResultFound

from db import get_session
from models import *
from users import current_active_user
from utils import specs_route
from schemas import *


router = APIRouter()


@router.post("/orders", responses={404: {"model": APIException}})
async def create_order(
        session: Annotated[AsyncSession, Depends(get_session)],
        order: OrderIn,
) -> OrderOutRel:
    # if user.is_spec is False we need to change order.user_id to user.id
    session.add(Order(**order.model_dump()))
    try:
        await session.commit()
    except IntegrityError:
        raise HTTPException(
            404, f"User with id {order.user_id} not found"
        )

    query = (select(Order)
             .options(joinedload(Order.user), joinedload(Order.response))
             .where(Order.user_id == order.user_id)
             .order_by(Order.id.desc()).limit(1))
    order_created = (await session.execute(query)).scalar_one()
    order_created_pydantic = OrderOutRel.model_validate(
        order_created, from_attributes=True
    )
    return order_created_pydantic


@specs_route
@router.get("/orders")
async def list_orders(
        session: Annotated[AsyncSession, Depends(get_session)],
        # user: Annotated[User, Depends(current_active_user)],
) -> list[OrderOutRel]:
    # if user is not Spec we need to return all orders where Order.user_id == user.id
    query = select(Order).options(
        joinedload(Order.user),
        joinedload(Order.response),
    )
    orders = (await session.execute(query)).scalars().all()
    orders_pydantic_list = [
        OrderOutRel.model_validate(order, from_attributes=True) for order in orders
    ]
    return orders_pydantic_list


@specs_route
@router.get("/orders/{order_id}", responses={404: {"model": APIException}})
async def get_order(
        session: Annotated[AsyncSession, Depends(get_session)],
        # user: Annotated[User, Depends(current_active_user)],
        order_id: int,
) -> OrderOutRel:
    query = select(Order).options(joinedload(Order.user), joinedload(Order.response)).where(Order.id == order_id)
    try:
        order = (await session.execute(query)).scalar_one()
    except NoResultFound:
        raise HTTPException(404, "Order not found")

    order_pydantic = OrderOutRel.model_validate(order, from_attributes=True)
    return order_pydantic


@specs_route
@router.patch("/orders/{order_id}", responses={404: {"model": APIException}})
async def patch_order(
        session: Annotated[AsyncSession, Depends(get_session)],
        # user: Annotated[User, Depends(current_active_user)],
        order_id: int,
        status: str,
) -> OrderOutRel:
    # and if Order.user_id == user.id if user is not Spec
    stmt = update(Order).where(Order.id == order_id).values(status=status)
    await session.execute(stmt)
    await session.commit()

    # Same if
    query = select(Order).options(joinedload(Order.user), joinedload(Order.response)).where(Order.id == order_id)
    try:
        updated_order = (await session.execute(query)).scalar_one()
    except NoResultFound:
        raise HTTPException(404, "Order not found")

    updated_order_pydantic = OrderOutRel.model_validate(updated_order, from_attributes=True)
    return updated_order_pydantic
