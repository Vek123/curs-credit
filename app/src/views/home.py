import flet as ft

from dependency_injector.wiring import Provide, inject
from flet_route import Params, Basket

from deps.containers import Application
from services import AuthService


class HomeView(object):
    @inject
    async def view(
            self,
            page: ft.Page,
            params: Params,
            basket: Basket,
            auth_service: AuthService = Provide[Application.services.auth_service]
    ) -> ft.View:
        is_spec = False
        if not await auth_service.is_authorized():
            page.go("/login")
        if await auth_service.is_spec():
            is_spec = True

        if is_spec:
            specs_menu = ft.Column(
                controls=[
                    ft.ElevatedButton("Заявки", on_click=lambda _: page.go("/specs-orders")),
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
                            controls=[
                                ft.Column(
                                    controls=[

                                    ]
                                ),
                                specs_menu,
                            ]
                        )
                    ]
                )
            ]
        )
