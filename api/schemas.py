import datetime
import re
from typing_extensions import Self

from datetime import date

from fastapi_users import schemas
from pydantic import Field, model_validator


class BaseUserFields:
    first_name: str = Field(max_length=50)
    second_name: str = Field(max_length=50)
    last_name: str = Field(max_length=50)
    birthday: date
    passport_serial: int
    passport_number: int
    gotten_by: str = Field(max_length=255)
    inn: str = Field(max_length=12, min_length=12)
    registration_address: str = Field(max_length=255)
    current_job: str = Field(max_length=255)
    per_month_profit: float = Field(gt=0)
    phone: str = Field(max_length=20)
    family_status: str = Field(max_length=16)

    @model_validator(mode="after")
    def check_phone(self) -> Self:
        template = re.compile(r"^\+\d{1,2} \(\d{3}\) \d{3}-\d{2}-\d{2}")
        if not template.fullmatch(self.phone):
            return ValueError("Введённый номер телефона некорректен")
        return self

    @model_validator(mode="after")
    def check_birthday(self) -> Self:
        if datetime.date.today() < self.birthday:
            return ValueError("Введённая дата рождения некорректна")
        return self

    @model_validator(mode="after")
    def check_inn(self) -> Self:
        if not self.inn.isdigit():
            return ValueError("ИНН введён некорректно")
        return self


class UserRead(schemas.BaseUser[int], BaseUserFields):
    pass


class UserCreate(schemas.BaseUserCreate, BaseUserFields):
    pass


class UserUpdate(schemas.BaseUserUpdate, BaseUserFields):
    pass
