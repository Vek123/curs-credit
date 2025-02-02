import datetime

import flet as ft

from dependency_injector.wiring import Provide, inject
from flet_route import Params, Basket
from pydantic import ValidationError

from deps.containers import Application
from schemas import OrderOutRel, OrderIn, ResponseOutRel, CreditIn
from services import AuthService, OrdersService, CreditsService

from utils import get_empty_orders_table, get_create_order_dialog


class OrdersView(object):
    @inject
    async def view(
            self,
            page: ft.Page,
            params: Params,
            basket: Basket,
            auth_service: AuthService = Provide[Application.services.auth_service],
            orders_service: OrdersService = Provide[
                Application.services.orders_service],
            credits_service: CreditsService = Provide[Application.services.credits_service],
    ) -> ft.View:
        user = await auth_service.me()
        if not user:
            page.go("/")

        async def create_credit(event: ft.ControlEvent):
            dialog = event.control.parent
            fields = dialog.content.controls
            response_id = int(fields[0].value)
            response = checked_responses[response_id]
            order = orders[response.order_id]
            next_month = (datetime.datetime.today() + datetime.timedelta(days=30)).date()
            data = {
                "monthly_pay": response.monthly_pay,
                "remain_to_pay": order.credit_size,
                "percent": response.percent,
                "next_pay_date": next_month,
                "user_id": order.user.id,
            }
            try:
                credit = CreditIn.model_validate(data)
            except ValidationError:
                return
            resp = await credits_service.create(credit)
            if not resp:
                return
            await orders_service.patch_order(order.id, "Выдан кредит", "false")
            await update_orders(orders_table)
            page.close(dialog)
            page.update()

        async def show_get_response_dialog(event: ft.ControlEvent):
            order_id = event.control.parent.parent.parent.cells[1].content.value
            response = orders[int(order_id)].response
            if response is None:
                response_dialog = ft.AlertDialog(
                    title=ft.Text("Ответ на заявку"),
                    content=ft.Text("Ответа ещё нет"),
                )
            else:
                response_dialog = ft.AlertDialog(
                    title=ft.Text("Ответ на заявку"),
                    content=ft.Column(
                        width=400,
                        controls=[
                            ft.TextField(label="Номер ответа", value=str(response.id),
                                         read_only=True, bgcolor=ft.Colors.WHITE),
                            ft.TextField(label="Процент", bgcolor=ft.Colors.WHITE,
                                         value=str(response.percent), read_only=True),
                            ft.TextField(label="Ежемесячный платёж",
                                         bgcolor=ft.Colors.WHITE,
                                         value=str(response.monthly_pay),
                                         read_only=True),
                        ]
                    ),
                    actions=[
                        ft.TextButton("Оформить кредит", on_click=create_credit)
                    ]
                )
                checked_responses[response.id] = response
            page.open(response_dialog)

        async def create_order(event: ft.ControlEvent):
            dialog = event.control.parent
            fields = dialog.content.controls
            try:
                data = {
                    "user_id": int(fields[0].value),
                    "credit_size": float(fields[1].value),
                    "period": int(fields[2].value),
                    "target": fields[3].value,
                }
                order = OrderIn.model_validate(data)
            except (ValidationError, ValueError):
                error.value = "Ответ заполнен некорректно"
                error.visible = True
                page.update()
                return
            response = await orders_service.create(order)
            if not response:
                error.value = "Возникла ошибка при создании заявки"
                error.visible = True
            else:
                await update_orders(orders_table)
            page.close(dialog)
            page.update()

        async def show_create_order_dialog(_: ft.ControlEvent):
            dialog = get_create_order_dialog(user.id, error)
            dialog.actions = [
                ft.TextButton("Создать", on_click=create_order)
            ]
            page.open(dialog)

        async def update_orders(table: ft.DataTable):
            nonlocal orders
            orders = await orders_service.list(personal=True)
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
                    ),
                    ft.DataCell(
                        ft.Text(order.target, text_align=ft.TextAlign.CENTER,
                                overflow=ft.TextOverflow.ELLIPSIS, width=80, height=60),
                    ),
                    ft.DataCell(
                        ft.Container(ft.IconButton(ft.Icons.MESSAGE,
                                                   on_click=show_get_response_dialog),
                                     alignment=ft.Alignment(.1, 0))
                    )
                ]) for _, order in orders.items()
            ]

        orders: dict[int, OrderOutRel] = dict()
        checked_responses: dict[int, ResponseOutRel] = dict()
        orders_table = get_empty_orders_table()
        error = ft.Text(visible=False, color=ft.Colors.RED)

        await update_orders(orders_table)

        return ft.View(
            controls=[
                ft.Column(
                    controls=[
                        ft.Text(value="Мои заявки", size=28),
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            vertical_alignment=ft.CrossAxisAlignment.START,
                            controls=[
                                ft.Column(
                                    scroll=ft.ScrollMode.AUTO,
                                    height=500,
                                    controls=[
                                        ft.ElevatedButton(
                                            text="Создать заявку",
                                            on_click=show_create_order_dialog,
                                        ),
                                        orders_table,
                                    ]
                                ),
                                ft.Column(
                                    controls=[
                                        ft.IconButton(ft.Icons.HOME,
                                                      on_click=lambda _: page.go("/")),
                                    ]
                                )
                            ]
                        )
                    ]
                )
            ]
        )
