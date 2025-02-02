import flet as ft

from dependency_injector.wiring import Provide, inject
from flet_route import Params, Basket

from deps.containers import Application
from services import AuthService, CreditsService
from utils import get_empty_credits_table


class CreditsView(object):
    @inject
    async def view(
            self,
            page: ft.Page,
            params: Params,
            basket: Basket,
            auth_service: AuthService = Provide[Application.services.auth_service],
            credits_service: CreditsService = Provide[Application.services.credits_service],
    ) -> ft.View:
        if not await auth_service.is_authorized():
            page.go("/")

        async def update_credits_table(table: ft.DataTable):
            credits = await credits_service.list(personal=True)
            table.rows = [
                ft.DataRow(
                    cells=[
                        ft.DataCell(
                            ft.Text(str(credit.id), text_align=ft.TextAlign.CENTER,
                                    no_wrap=False, width=50, height=60),
                        ),
                        ft.DataCell(
                            ft.Text(credit.next_pay_date.strftime("%d.%m.%Y"),
                                    text_align=ft.TextAlign.CENTER, no_wrap=False,
                                    width=100,
                                    height=60),
                        ),
                        ft.DataCell(
                            ft.Text(f"{credit.remain_to_pay:.2f}",
                                    text_align=ft.TextAlign.CENTER, no_wrap=False,
                                    width=120, height=60),
                        ),
                        ft.DataCell(
                            ft.Text(str(credit.monthly_pay), text_align=ft.TextAlign.CENTER,
                                    no_wrap=False, width=100, height=60),
                        ),
                        ft.DataCell(
                            ft.Text(str(credit.percent), text_align=ft.TextAlign.CENTER,
                                    no_wrap=False, width=80, height=60),
                        ),
                    ]
                ) for credit in credits
            ]

        credits_table = get_empty_credits_table()
        await update_credits_table(credits_table)
        return ft.View(
            controls=[
                ft.Column(
                    controls=[
                        ft.Text(value="Мои кредиты", size=28),
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            vertical_alignment=ft.CrossAxisAlignment.START,
                            controls=[
                                ft.Column(
                                    scroll=ft.ScrollMode.AUTO,
                                    height=500,
                                    controls=[
                                        credits_table,
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
