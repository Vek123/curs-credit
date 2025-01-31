import datetime
import re
from typing_extensions import Self

from datetime import date

from fastapi_users import schemas
from pydantic import Field, model_validator, BaseModel


class APIException(BaseModel):
    detail: str


class BaseUserFields:
    first_name: str = Field(max_length=50)
    second_name: str = Field(max_length=50)
    last_name: str = Field(max_length=50)
    birthday: date
    passport_serial: int = Field(gt=0)
    passport_number: int = Field(gt=0)
    gotten_by: str = Field(max_length=255)
    inn: str = Field(max_length=12, min_length=12)
    registration_address: str = Field(max_length=255)
    current_job: str = Field(max_length=255)
    per_month_profit: float = Field(gt=0)
    phone: str = Field(max_length=20)
    family_status: str = Field(max_length=16)

    @model_validator(mode="after")
    def check_passport(self) -> Self:
        if len(str(self.passport_serial)) != 4:
            raise ValueError("Серия паспорта должна состоять из 4 цифр")
        elif len(str(self.passport_number)) != 6:
            raise ValueError("Номер паспорта должен состоять из 6 цифр")
        return self

    @model_validator(mode="after")
    def check_phone(self) -> Self:
        template = re.compile(r"^\+\d{1,2} \(\d{3}\) \d{3}-\d{2}-\d{2}")
        if not template.fullmatch(self.phone):
            raise ValueError("Введённый номер телефона некорректен")
        return self

    @model_validator(mode="after")
    def check_birthday(self) -> Self:
        if datetime.date.today() < self.birthday:
            raise ValueError("Введённая дата рождения некорректна")
        today = datetime.datetime.today()
        eighteen_years_ago = (today
                              - datetime.timedelta(days=365 * 18 + 1))
        if today - eighteen_years_ago > today - datetime.datetime.combine(
                self.birthday, datetime.datetime.min.time()
        ):
            raise ValueError("Вам должно быть 18 лет")
        return self

    @model_validator(mode="after")
    def check_inn(self) -> Self:
        if not self.inn.isdigit():
            raise ValueError("ИНН введён некорректно")
        return self


class UserRead(schemas.BaseUser[int], BaseUserFields):
    pass


class UserCreate(schemas.BaseUserCreate, BaseUserFields):
    pass


class UserUpdate(schemas.BaseUserUpdate, BaseUserFields):
    pass


class OrderWoIds(BaseModel):
    credit_size: float = Field(ge=5_000)
    period: int = Field(ge=3)
    target: str = Field(max_length=255)


class OrderIn(OrderWoIds):
    user_id: int


class OrderOutWoId(OrderWoIds):
    id: int
    status: str


class OrderOut(OrderIn):
    id: int
    status: str


class ResponseWoIds(BaseModel):
    percent: float = Field(ge=0)
    monthly_pay: float = Field(ge=0)


class ResponseIn(ResponseWoIds):
    order_id: int


class ResponseOutWoIds(ResponseWoIds):
    id: int


class ResponseOut(ResponseIn):
    id: int


class CreditWoIds(BaseModel):
    next_pay_data: date
    remain_to_pay: float = Field(ge=0)
    monthly_pay: float = Field(ge=0)


class CreditIn(CreditWoIds):
    user_id: int


class CreditOutWoIds(CreditWoIds):
    id: int


class CreditOut(CreditIn):
    id: int


class OrderOutRel(OrderOutWoId):
    user: UserRead


class ResponseOutRel(ResponseOutWoIds):
    order: OrderOutRel


class CreditOutRel(CreditOutWoIds):
    user: UserRead
