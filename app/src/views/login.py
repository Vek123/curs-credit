import flet as ft
from dependency_injector.wiring import Provide, inject
from flet_route import Params, Basket

from deps.containers import Application
from schemas import UserCreds
from services import AuthService


class LoginView(object):
    @inject
    async def view(
            self,
            page: ft.Page,
            params: Params,
            basket: Basket,
            auth_service: AuthService = Provide[Application.services.auth_service]
    ) -> ft.View:
        if await auth_service.is_authorized():
            page.go("/")

        async def make_login(event: ft.ControlEvent):
            user = await auth_service.login(
                UserCreds(username=email.value, password=password.value)
            )
            if user:
                page.go("/")
            else:
                error.value = "Введённые данные не верные"
                error.visible = True
            page.update()

        email = ft.TextField(label="Почта")
        password = ft.TextField(label="Пароль", password=True)
        error = ft.Text(color=ft.Colors.RED, size=24, visible=False)

        return ft.View(
            controls=[
                ft.Column(
                    controls=[
                        ft.Text("Авторизация"),
                        ft.Column(
                            controls=[
                                email,
                                password,
                                error,
                                ft.ElevatedButton("Войти", on_click=make_login)
                            ]
                        )
                    ]
                )
            ]
        )
