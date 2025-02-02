import flet as ft

from dependency_injector.wiring import Provide, inject
from flet_route import Params, Basket
from pydantic import ValidationError

from deps.containers import Application
from schemas import ResponseIn, OrderOutRel
from services import AuthService, OrdersService, ResponsesService


class SpecsOrdersView(object):
    @inject
    async def view(
            self,
            page: ft.Page,
            params: Params,
            basket: Basket,
            auth_service: AuthService = Provide[Application.services.auth_service],
            orders_service: OrdersService = Provide[Application.services.orders_service],
            responses_service: ResponsesService = Provide[Application.services.responses_service],
    ) -> ft.View:
        async def show_user_info(event: ft.ControlEvent):
            user = orders[int(event.control.parent.cells[1].content.value)].user
            user_info = ft.AlertDialog(
                title=ft.Text(f"{user.first_name} {user.second_name} {user.last_name}"),
                content=ft.Column(
                    width=400,
                    scroll=ft.ScrollMode.ALWAYS,
                    controls=[
                        ft.TextField(user.birthday.strftime("%d.%m.%Y"), label="Дата рождения", read_only=True, bgcolor=ft.Colors.WHITE),
                        ft.TextField(str(user.passport_serial), label="Серия паспорта", read_only=True, bgcolor=ft.Colors.WHITE),
                        ft.TextField(str(user.passport_number), label="Номер паспорта", read_only=True, bgcolor=ft.Colors.WHITE),
                        ft.TextField(user.gotten_by, label="Выдан", read_only=True, bgcolor=ft.Colors.WHITE),
                        ft.TextField(user.inn, label="ИНН", read_only=True, bgcolor=ft.Colors.WHITE),
                        ft.TextField(user.registration_address, label="Адрес регистрации", read_only=True, bgcolor=ft.Colors.WHITE),
                        ft.TextField(user.current_job, label="Текущая работа", read_only=True, bgcolor=ft.Colors.WHITE),
                        ft.TextField(f"{user.per_month_profit:.2f}", label="Ежемесячный доход, руб.", read_only=True, bgcolor=ft.Colors.WHITE),
                        ft.TextField(user.phone, label="Номер телефона", read_only=True, bgcolor=ft.Colors.WHITE),
                        ft.TextField(user.family_status, label="Семейный статус", read_only=True, bgcolor=ft.Colors.WHITE),
                        ft.TextField(user.email, label="Эл. почта", read_only=True, bgcolor=ft.Colors.WHITE),
                    ]
                ),
            )
            page.open(user_info)

        async def send_response(event: ft.ControlEvent):
            modal = event.control.parent
            controls = modal.content.controls
            error = controls[-1]
            try:
                order_id = int(controls[0].value)
                percent = float(controls[1].value)
                monthly_pay = float(controls[2].value)
                response = ResponseIn(order_id=order_id, percent=percent, monthly_pay=monthly_pay)
            except (ValidationError, ValueError):
                error.value = "Заявка заполнена некорректно"
                error.visible = True
                page.update()
                return
            result = await responses_service.create(response)
            if result is None:
                error.value = "Ответ не был отправлен"
                error.visible = True
                page.update()
                return
            await orders_service.patch_order(order_id, "Отправлен ответ", "false")
            await update_orders(orders_table)
            page.close(modal)

        async def update_orders(table: ft.DataTable):
            nonlocal orders
            orders = await orders_service.list_new()
            orders = {order.id: order for order in orders}
            table.rows = [
                ft.DataRow(cells=[
                    ft.DataCell(
                        ft.Text(order.date.strftime("%d.%m.%Y %H:%M:%S"),
                                text_align=ft.TextAlign.CENTER, no_wrap=False, width=70,
                                height=60),
                    ),
                    ft.DataCell(
                        ft.Text(str(order.id), text_align=ft.TextAlign.CENTER,
                                no_wrap=False, width=50, height=60),
                    ),
                    ft.DataCell(
                        ft.Text(f"{order.credit_size:.2f}",
                                text_align=ft.TextAlign.CENTER, no_wrap=False,
                                width=120, height=60),
                    ),
                    ft.DataCell(
                        ft.Text(str(order.period), text_align=ft.TextAlign.CENTER,
                                no_wrap=False, width=50, height=60),
                    ),
                    ft.DataCell(
                        ft.Text(order.status, text_align=ft.TextAlign.CENTER,
                                no_wrap=False, width=80, height=60),
                    ),
                    ft.DataCell(
                        ft.Text(
                            f"{order.user.first_name} {order.user.second_name} {order.user.last_name}",
                            style=ft.TextStyle(decoration=ft.TextDecoration.UNDERLINE),
                            text_align=ft.TextAlign.CENTER, no_wrap=False, max_lines=2,
                            overflow=ft.TextOverflow.ELLIPSIS, width=80, height=60),
                        on_tap=show_user_info,
                    ),
                    ft.DataCell(
                        ft.Text(order.target, text_align=ft.TextAlign.CENTER,
                                overflow=ft.TextOverflow.ELLIPSIS, width=80, height=60),
                    ),
                    ft.DataCell(
                        ft.Container(ft.IconButton(ft.Icons.MESSAGE,
                                                   on_click=show_make_response_dialog),
                                     alignment=ft.Alignment(.1, 0))
                    )
                ]) for order in orders.values()
            ]
            page.update()

        def show_make_response_dialog(event: ft.ControlEvent):
            order_id = int(event.control.parent.parent.parent.cells[1].content.value)
            message_dialog = ft.AlertDialog(
                title=ft.Text("Ответ на запрос"),
                content=ft.Column(
                    width=400,
                    controls=[
                        ft.TextField(label="Номер заявки", value=str(order_id), read_only=True, bgcolor=ft.Colors.WHITE),
                        ft.TextField(label="Процент", bgcolor=ft.Colors.WHITE),
                        ft.TextField(label="Ежемесячный платёж", bgcolor=ft.Colors.WHITE),
                        ft.Text(visible=False, color=ft.Colors.RED),
                    ]
                ),
                actions=[
                    ft.TextButton("Ответить", on_click=send_response),
                ]
            )
            page.open(message_dialog)

        if not await auth_service.is_spec():
            page.go("/")

        orders: dict[int, OrderOutRel] = dict()
        orders_table = ft.DataTable(
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
                ft.DataColumn(label=ft.Text("Дата", text_align=ft.TextAlign.CENTER, no_wrap=False, width=70, height=50, offset=ft.Offset(0, 0))),
                ft.DataColumn(label=ft.Text("Номер", text_align=ft.TextAlign.CENTER, no_wrap=False, width=50, height=50)),
                ft.DataColumn(label=ft.Text("Размер кредита, руб.", text_align=ft.TextAlign.CENTER, no_wrap=False, width=120, height=50)),
                ft.DataColumn(label=ft.Text("Срок, мес.", text_align=ft.TextAlign.CENTER, no_wrap=False, width=50, height=50)),
                ft.DataColumn(label=ft.Text("Статус заявки", text_align=ft.TextAlign.CENTER, no_wrap=False, width=80, height=50)),
                ft.DataColumn(label=ft.Text("ФИО заёмщика", text_align=ft.TextAlign.CENTER, no_wrap=False, width=80, height=50)),
                ft.DataColumn(label=ft.Text("Цель кредита", text_align=ft.TextAlign.CENTER, no_wrap=False, width=80, height=50)),
                ft.DataColumn(label=ft.Text("Ответить", text_align=ft.TextAlign.CENTER, no_wrap=False, width=80, height=50)),
            ]
        )

        await update_orders(orders_table)

        return ft.View(
            controls=[
                ft.Column(
                    controls=[
                        ft.Text(value="Заявки клиентов", size=28),
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            vertical_alignment=ft.CrossAxisAlignment.START,
                            controls=[
                                ft.Column(
                                    controls=[
                                        orders_table,
                                    ]
                                ),
                                ft.Column(
                                    controls=[
                                        ft.IconButton(ft.Icons.HOME, on_click=lambda _: page.go("/")),
                                    ]
                                )
                            ]
                        )
                    ]
                )
            ]
        )
