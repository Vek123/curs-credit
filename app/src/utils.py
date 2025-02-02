import contextlib

import flet as ft
from aiohttp import ClientSession

from schemas import UserOut
from settings import settings


@contextlib.asynccontextmanager
async def get_session() -> ClientSession:
    token = get_auth_token()
    token_header = f"Bearer {token}"
    async with ClientSession(
            base_url=settings.api_base_url, headers={"Authorization": token_header}
    ) as session:
        yield session


def get_auth_token() -> str:
    with open(settings.project_root / "auth_token", "r") as file:
        return file.read().strip()


def set_auth_token(token: str) -> None:
    with open(settings.project_root / "auth_token", "w") as file:
        file.write(token)


def get_user_info_dialog(user: UserOut, read_only: bool = True) -> ft.AlertDialog:
    return ft.AlertDialog(
        title=ft.Text(f"{user.first_name} {user.second_name} {user.last_name}"),
        content=ft.Column(
            width=400,
            scroll=ft.ScrollMode.ALWAYS,
            controls=[
                ft.TextField(user.birthday.strftime("%d.%m.%Y"), label="Дата рождения",
                             read_only=read_only, bgcolor=ft.Colors.WHITE),
                ft.TextField(str(user.passport_serial), label="Серия паспорта",
                             read_only=read_only, bgcolor=ft.Colors.WHITE),
                ft.TextField(str(user.passport_number), label="Номер паспорта",
                             read_only=read_only, bgcolor=ft.Colors.WHITE),
                ft.TextField(user.gotten_by, label="Выдан", read_only=read_only,
                             bgcolor=ft.Colors.WHITE),
                ft.TextField(user.inn, label="ИНН", read_only=read_only,
                             bgcolor=ft.Colors.WHITE),
                ft.TextField(user.registration_address, label="Адрес регистрации",
                             read_only=read_only, bgcolor=ft.Colors.WHITE),
                ft.TextField(user.current_job, label="Текущая работа",
                             read_only=read_only,
                             bgcolor=ft.Colors.WHITE),
                ft.TextField(f"{user.per_month_profit:.2f}",
                             label="Ежемесячный доход, руб.", read_only=read_only,
                             bgcolor=ft.Colors.WHITE),
                ft.TextField(user.phone, label="Номер телефона", read_only=read_only,
                             bgcolor=ft.Colors.WHITE),
                ft.TextField(user.family_status, label="Семейный статус",
                             read_only=read_only, bgcolor=ft.Colors.WHITE),
                ft.TextField(user.email, label="Эл. почта", read_only=read_only,
                             bgcolor=ft.Colors.WHITE),
            ]
        )
    )


def get_empty_orders_table() -> ft.DataTable:
    table = ft.DataTable(
        data_row_max_height=60,
        horizontal_margin=5,
        sort_column_index=4,
        column_spacing=5,
        border=ft.Border(
            ft.BorderSide(1, ft.Colors.BLACK),
            ft.BorderSide(1, ft.Colors.BLACK),
            ft.BorderSide(1, ft.Colors.BLACK),
            ft.BorderSide(1, ft.Colors.BLACK),
        ),
        vertical_lines=ft.BorderSide(.5, ft.Colors.GREY),
        columns=[
            ft.DataColumn(
                label=ft.Text("Дата", text_align=ft.TextAlign.CENTER, no_wrap=False,
                              width=70, height=50, offset=ft.Offset(0, 0))),
            ft.DataColumn(
                label=ft.Text("Номер", text_align=ft.TextAlign.CENTER, no_wrap=False,
                              width=50, height=50)),
            ft.DataColumn(
                label=ft.Text("Размер кредита, руб.", text_align=ft.TextAlign.CENTER,
                              no_wrap=False, width=120, height=50)),
            ft.DataColumn(label=ft.Text("Срок, мес.", text_align=ft.TextAlign.CENTER,
                                        no_wrap=False, width=50, height=50)),
            ft.DataColumn(label=ft.Text("Статус заявки", text_align=ft.TextAlign.CENTER,
                                        no_wrap=False, width=80, height=50)),
            ft.DataColumn(label=ft.Text("ФИО заёмщика", text_align=ft.TextAlign.CENTER,
                                        no_wrap=False, width=80, height=50)),
            ft.DataColumn(label=ft.Text("Цель кредита", text_align=ft.TextAlign.CENTER,
                                        no_wrap=False, width=80, height=50)),
            ft.DataColumn(
                label=ft.Text("Ответить", text_align=ft.TextAlign.CENTER, no_wrap=False,
                              width=80, height=50)),
        ]
    )
    return table


def get_create_order_dialog(user_id: int, error: ft.Text) -> ft.AlertDialog:
    return ft.AlertDialog(
        content=ft.Column(
            controls=[
                ft.TextField(label="Номер пользователя", value=str(user_id),
                             read_only=True, bgcolor=ft.Colors.WHITE),
                ft.TextField(label="Размер кредита", bgcolor=ft.Colors.WHITE),
                ft.TextField(label="Срок, мес.", bgcolor=ft.Colors.WHITE),
                ft.TextField(label="Цель", bgcolor=ft.Colors.WHITE),
                error,
            ]
        ),
    )


def get_empty_credits_table() -> ft.DataTable:
    table = ft.DataTable(
        data_row_max_height=60,
        horizontal_margin=5,
        column_spacing=5,
        border=ft.Border(
            ft.BorderSide(1, ft.Colors.BLACK),
            ft.BorderSide(1, ft.Colors.BLACK),
            ft.BorderSide(1, ft.Colors.BLACK),
            ft.BorderSide(1, ft.Colors.BLACK),
        ),
        vertical_lines=ft.BorderSide(.5, ft.Colors.GREY),
        columns=[
            ft.DataColumn(
                label=ft.Text("Номер", text_align=ft.TextAlign.CENTER, no_wrap=False,
                              width=50, height=50)),
            ft.DataColumn(
                label=ft.Text("Дата след. платежа", text_align=ft.TextAlign.CENTER, no_wrap=False,
                              width=100, height=50, offset=ft.Offset(0, 0))),
            ft.DataColumn(
                label=ft.Text("Осталось заплатить, руб.", text_align=ft.TextAlign.CENTER,
                              no_wrap=False, width=120, height=50)),
            ft.DataColumn(label=ft.Text("Ежемесячный платёж, руб.", text_align=ft.TextAlign.CENTER,
                                        no_wrap=False, width=100, height=50)),
            ft.DataColumn(label=ft.Text("Ставка, %", text_align=ft.TextAlign.CENTER,
                                        no_wrap=False, width=80, height=50)),
        ]
    )
    return table
