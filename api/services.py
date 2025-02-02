from typing import Annotated, List

from fastapi import Depends, HTTPException
from sqlalchemy import select, update
from sqlalchemy.orm import joinedload, contains_eager
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from db import get_session
from schemas import (
    CreditOut,
    CreditIn,
    OrderOutRel,
    OrderIn,
    ResponseIn,
    ResponseOutRel, CreditOutRel,
)
from models import Order, Response, Credit


class BaseService(object):
    def __init__(
            self,
            session: Annotated[AsyncSession, Depends(get_session)],
    ):
        self.session = session


class OrderService(BaseService):
    base_query = (
        select(Order)
        .options(joinedload(Order.user), joinedload(Order.response))
    )

    async def create(self, order: OrderIn) -> OrderOutRel:
        self.session.add(Order(**order.model_dump()))
        try:
            await self.session.commit()
        except IntegrityError:
            raise HTTPException(
                404, f"User with id {order.user_id} not found"
            )

        query = (
            self.base_query
            .where(Order.user_id == order.user_id)
            .order_by(Order.id.desc()).limit(1)
        )
        order_created = (await self.session.execute(query)).scalar_one()
        order_created_pydantic = OrderOutRel.model_validate(
            order_created, from_attributes=True
        )
        return order_created_pydantic

    async def list(self, user_id: int | None = None) -> List[OrderOutRel]:
        if user_id is None:
            query = self.base_query
        else:
            query = self.base_query.where(Order.user_id == user_id)
        orders = (await self.session.execute(query)).scalars().all()
        orders_pydantic_list = [
            OrderOutRel.model_validate(order, from_attributes=True) for order in orders
        ]
        return orders_pydantic_list

    async def list_new(self, user_id: int | None = None) -> List[OrderOutRel]:
        query = self.base_query.where(Order.new == True)
        if user_id is not None:
            query = query.where(Order.user_id == user_id)
        orders = (await self.session.execute(query)).scalars().all()
        orders_pydantic_list = [
            OrderOutRel.model_validate(order, from_attributes=True) for order in orders
        ]
        return orders_pydantic_list

    async def get(self, order_id: int, user_id: int | None = None) -> OrderOutRel:
        query = self.base_query.where(Order.id == order_id)
        if user_id is not None:
            query = query.where(Order.user_id == user_id)
        try:
            order = (await self.session.execute(query)).scalar_one()
        except NoResultFound:
            raise HTTPException(404, "Order not found")

        order_pydantic = OrderOutRel.model_validate(order, from_attributes=True)
        return order_pydantic

    async def change_status(self, order_id: int, status: str, new: bool) -> OrderOutRel:
        stmt = update(Order).where(Order.id == order_id).values(
            status=status, new=new
        )
        await self.session.execute(stmt)
        await self.session.commit()

        # Same if
        query = select(Order).options(joinedload(Order.user),
                                      joinedload(Order.response)).where(
            Order.id == order_id)
        try:
            updated_order = (await self.session.execute(query)).scalar_one()
        except NoResultFound:
            raise HTTPException(404, "Order not found")

        updated_order_pydantic = OrderOutRel.model_validate(updated_order,
                                                            from_attributes=True)
        return updated_order_pydantic


class ResponseService(BaseService):
    base_query = (
        select(Response)
        .join(Response.order)
        .join(Order.user)
        .options(contains_eager(Response.order, Order.user))
    )

    async def create(self, response: ResponseIn) -> ResponseOutRel:
        query = select(Response).where(Response.order_id == response.order_id)
        try:
            (await self.session.execute(query)).scalar_one()
        except NoResultFound:
            pass
        else:
            raise HTTPException(
                409, "Response for this order already exists"
            )
        self.session.add(Response(**response.model_dump()))
        try:
            await self.session.commit()
        except IntegrityError:
            raise HTTPException(
                404, f"Order with id {response.order_id} not found"
            )

        query = self.base_query.where(Response.order_id == response.order_id)
        created_response = (await self.session.execute(query)).scalar_one()
        created_response_pydantic = ResponseOutRel.model_validate(
            created_response,
            from_attributes=True,
        )

        return created_response_pydantic

    async def list(self, user_id: int | None = None) -> List[ResponseOutRel]:
        query = self.base_query
        if user_id is not None:
            query = query.where(Response.order.user_id == user_id)
        responses = (await self.session.execute(query)).scalars().all()
        responses_pydantic = [ResponseOutRel.model_validate(resp) for resp in responses]

        return responses_pydantic


class CreditService(BaseService):
    base_query = select(Credit).options(joinedload(Credit.user))

    async def create(self, credit: CreditIn) -> CreditOutRel:
        self.session.add(Credit(**credit.model_dump()))
        try:
            await self.session.commit()
        except IntegrityError:
            raise HTTPException(404, f"User with id {credit.user_id} not found")
        query = (
            self.base_query
            .where(Credit.user_id == credit.user_id)
            .order_by(Credit.id.desc())
            .limit(1)
        )
        created_credit = (await self.session.execute(query)).scalar_one()
        created_credit_pydantic = CreditOutRel.model_validate(
            created_credit, from_attributes=True
        )

        return created_credit_pydantic

    async def list(self, user_id: int | None = None) -> List[CreditOutRel]:
        query = self.base_query
        if user_id is not None:
            query = query.where(Credit.user_id == user_id)
        credits = (await self.session.execute(query)).scalars().all()
        credits_pydantic = [CreditOutRel.model_validate(
            cr, from_attributes=True
        ) for cr in credits]

        return credits_pydantic

    async def get(self, credit_id: int, user_id: int | None = None) -> CreditOutRel:
        query = self.base_query.where(Credit.id == credit_id)
        if user_id is not None:
            query = query.where(Credit.user_id == user_id)
        try:
            credit = (await self.session.execute(query)).scalar_one()
        except NoResultFound:
            raise HTTPException(404, "Credit not found")
        credit_pydantic = CreditOutRel.model_validate(credit, from_attributes=True)

        return credit_pydantic
