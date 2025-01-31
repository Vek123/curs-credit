from typing import Annotated

from fastapi import Depends, HTTPException
from sqlalchemy import select, update
from sqlalchemy.orm import joinedload, contains_eager
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from db import get_session
from users import current_active_user
from schemas import *
from models import *


class BaseService(object):
    def __init__(
            self,
            session: Annotated[AsyncSession, Depends(get_session)],
            # user: Annotated[User, Depends(current_active_user)],
    ):
        self.session = session


class OrderService(BaseService):
    async def create(self, order: OrderIn) -> OrderOutRel:
        # if user.is_spec is False we need to change order.user_id to user.id
        self.session.add(Order(**order.model_dump()))
        try:
            await self.session.commit()
        except IntegrityError:
            raise HTTPException(
                404, f"User with id {order.user_id} not found"
            )

        query = (select(Order)
                 .options(joinedload(Order.user), joinedload(Order.response))
                 .where(Order.user_id == order.user_id)
                 .order_by(Order.id.desc()).limit(1))
        order_created = (await self.session.execute(query)).scalar_one()
        order_created_pydantic = OrderOutRel.model_validate(
            order_created, from_attributes=True
        )
        return order_created_pydantic

    async def list(self) -> list[OrderOutRel]:
        # if user is not Spec we need to return all orders where Order.user_id == user.id
        query = select(Order).options(
            joinedload(Order.user),
            joinedload(Order.response),
        )
        orders = (await self.session.execute(query)).scalars().all()
        orders_pydantic_list = [
            OrderOutRel.model_validate(order, from_attributes=True) for order in orders
        ]
        return orders_pydantic_list

    async def get(self, order_id: int) -> OrderOutRel:
        query = select(Order).options(joinedload(Order.user),
                                      joinedload(Order.response)).where(
            Order.id == order_id)
        try:
            order = (await self.session.execute(query)).scalar_one()
        except NoResultFound:
            raise HTTPException(404, "Order not found")

        order_pydantic = OrderOutRel.model_validate(order, from_attributes=True)
        return order_pydantic

    async def change_status(self, order_id: int, status: str, new: bool) -> OrderOutRel:
        # and if Order.user_id == user.id if user is not Spec
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
    base_query = (select(Response)
                  .join(Response.order)
                  .join(Order.user)
                  .options(contains_eager(Response.order, Order.user)))

    async def create(self, response: ResponseIn) -> ResponseOutRel:
        # Need to select only those responses where Order.user_id == user.id if User is not Spec
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
        created_response_pydantic = ResponseOutRel.model_validate(created_response,
                                                                  from_attributes=True)

        return created_response_pydantic

    async def list(self) -> list[ResponseOutRel]:
        # Need to check if User is Spec we can get all Responses either only where self.user.id == response.order.user.id
        query = self.base_query
        responses = (await self.session.execute(query)).scalars().all()
        responses_pydantic = [ResponseOutRel.model_validate(resp) for resp in responses]

        return responses_pydantic


class CreditService(BaseService):
    base_query = select(Credit).options(joinedload(Credit.user))

    async def create(self, credit: CreditIn) -> CreditOut:
        self.session.add(Credit(**credit.model_dump()))
        try:
            await self.session.commit()
        except IntegrityError:
            raise HTTPException(404, f"User with id {credit.user_id} not found")
        query = (self.base_query
                 .where(Credit.user_id == credit.user_id)
                 .order_by(Credit.id.desc())
                 .limit(1))
        created_credit = (await self.session.execute(query)).scalar_one()
        created_credit_pydantic = CreditOut.model_validate(
            created_credit, from_attributes=True
        )

        return created_credit_pydantic

    async def list(self) -> list[CreditOut]:
        # Need to get only Specs and Users who own these
        credits = (await self.session.execute(self.base_query)).scalars().all()
        credits_pydantic = [CreditOut.model_validate(cr) for cr in credits]

        return credits_pydantic

    async def get(self, credit_id: int) -> CreditOut:
        # Need to get only Specs and Users who own these
        query = self.base_query.where(Credit.id == credit_id)
        try:
            credit = (await self.session.execute(query)).scalar_one()
        except NoResultFound:
            raise HTTPException(404, "Credit not found")
        credit_pydantic = CreditOut.model_validate(credit, from_attributes=True)

        return credit_pydantic
