import flet as ft
from dependency_injector.wiring import Provide, inject
from flet_route import Params, Basket

from deps.containers import Application
from schemas import UserCreds
from services import AuthService
from pydantic import ValidationError


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

        async def make_login(_: ft.ControlEvent):
            try:
                user_pydantic = UserCreds(username=email.value, password=password.value)
            except ValidationError:
                error.value = "Введённые данные некорректные"
                error.visible = True
                page.update()
                return
            logon = await auth_service.login(user_pydantic)
            if logon:
                page.go("/")
            else:
                error.value = "Введённые данные неверные"
                error.visible = True
            page.update()

        email = ft.TextField(label="Почта")
        password = ft.TextField(label="Пароль", password=True)
        error = ft.Text(color=ft.Colors.RED, size=16, visible=False)

        return ft.View(
            controls=[
                ft.Column(
                    controls=[
                        ft.Text("Авторизация", size=28),
                        ft.Column(
                            width=250,
                            controls=[
                                email,
                                password,
                                error,
                                ft.ElevatedButton("Войти", on_click=make_login),
                                ft.ElevatedButton(
                                    "Зарегистрироваться",
                                    on_click=lambda _: page.go("/register"),
                                )
                            ]
                        )
                    ]
                )
            ]
        )
