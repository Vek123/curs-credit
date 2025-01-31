from datetime import datetime, date
from typing import Annotated

from fastapi_users.db import SQLAlchemyBaseUserTable
from sqlalchemy import text, MetaData, String, Date, Enum, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


convention = {
    "all_column_names": lambda constraint, table: "_".join(
        [column.name for column in constraint.columns.values()]
    ),
    "ix": "ix__%(table_name)s__%(all_column_names)s",
    "uq": "uq__%(table_name)s__%(all_column_names)s",
    "ck": "ck__%(table_name)s__%(constraint_name)s",
    "fk": "fk__%(table_name)s__%(all_column_names)s__%(referred_table_name)s",
    "pk": "pk__%(table_name)s",
}

int_pk = Annotated[int, mapped_column(primary_key=True)]
created_at = Annotated[datetime, mapped_column(server_default=text("TIMEZONE('utc', now())"))]
updated_at = Annotated[datetime, mapped_column(server_default=text("TIMEZONE('utc', now())"), onupdate=datetime.utcnow)]
str_uniq = Annotated[str, mapped_column(unique=True, nullable=False)]
str_null_true = Annotated[str, mapped_column(nullable=True)]


class BaseOrm(DeclarativeBase):
    metadata = MetaData(naming_convention=convention)


class User(SQLAlchemyBaseUserTable, BaseOrm):
    id: Mapped[int_pk]
    is_spec: Mapped[bool] = mapped_column(default=False)
    first_name: Mapped[str] = mapped_column(String(50))
    second_name: Mapped[str] = mapped_column(String(50))
    last_name: Mapped[str] = mapped_column(String(50))
    birthday: Mapped[date] = mapped_column(Date)
    passport_serial: Mapped[int]
    passport_number: Mapped[int]
    gotten_by: Mapped[str] = mapped_column(String(255))
    inn: Mapped[str] = mapped_column(String(12))
    registration_address: Mapped[str] = mapped_column(String(255))
    current_job: Mapped[str] = mapped_column(String(255))
    per_month_profit: Mapped[float]
    phone: Mapped[str] = mapped_column(String(20))
    family_status: Mapped[str] = mapped_column(String(16))
    orders: Mapped[list["Order"]] = relationship(back_populates="user")
    credits: Mapped[list["Credit"]] = relationship(back_populates="user")


class Order(BaseOrm):
    __tablename__ = "order"

    id: Mapped[int_pk]
    date: Mapped[created_at]
    credit_size: Mapped[float]
    period: Mapped[int]
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    user: Mapped[User] = relationship(back_populates="orders")
    target: Mapped[str] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(32), default="Отправлена")
    response: Mapped["Response"] = relationship(back_populates="order")


class Response(BaseOrm):
    __tablename__ = "response"

    id: Mapped[int_pk]
    order_id: Mapped[int] = mapped_column(ForeignKey("order.id"))
    order: Mapped[Order] = relationship(back_populates="response")
    percent: Mapped[float]
    monthly_pay: Mapped[float]


class Credit(BaseOrm):
    __tablename__ = "credit"

    id: Mapped[int_pk]
    next_pay_data: Mapped[date]
    remain_to_pay: Mapped[float]
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    user: Mapped[User] = relationship(back_populates="credits")
    monthly_pay: Mapped[float]
