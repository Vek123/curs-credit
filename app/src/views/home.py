import flet as ft

from dependency_injector.wiring import Provide, inject
from flet_route import Params, Basket

from deps.containers import Application
from services import AuthService, OrdersService


class HomeView(object):
    @inject
    async def view(
            self,
            page: ft.Page,
            params: Params,
            basket: Basket,
            auth_service: AuthService = Provide[Application.services.auth_service],
            orders_service: OrdersService = Provide[Application.services.orders_service],
    ) -> ft.View:
        is_spec = False
        if not await auth_service.is_authorized():
            page.go("/login")
        if await auth_service.is_spec():
            is_spec = True

        if is_spec:
            specs_menu = ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.END,
                controls=[
                    ft.ElevatedButton("Заявки", on_click=lambda _: page.go("/specs/orders")),
                    ft.ElevatedButton("Кредиты", on_click=lambda _: page.go("/specs/credits")),
                ]
            )
        else:
            specs_menu = ft.Column(visible=False)

        return ft.View(
            controls=[
                ft.Column(
                    controls=[
                        ft.Text(value="Главная", size=28),
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            vertical_alignment=ft.CrossAxisAlignment.START,
                            controls=[
                                ft.Column(
                                    controls=[
                                        ft.Row(
                                            controls=[
                                                ft.ElevatedButton(
                                                    text="Мои заявки",
                                                    on_click=lambda _: page.go("/orders"),
                                                ),
                                                ft.ElevatedButton(
                                                    text="Мои кредиты",
                                                    on_click=lambda _: page.go("/credits"),
                                                ),
                                                ft.ElevatedButton(
                                                    text="Выйти",
                                                    on_click=lambda _: page.go("/logout"),
                                                ),
                                            ]
                                        )
                                    ]
                                ),
                                specs_menu,
                            ]
                        )
                    ]
                )
            ]
        )
