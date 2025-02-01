import flet as ft
from dependency_injector.wiring import Provide, inject
from flet_route import Params, Basket

from deps.containers import Application
from services import AuthService
from schemas import UserIn


class RegisterView(object):
    @inject
    async def view(
            self,
            page: ft.Page,
            params: Params,
            basket: Basket,
            auth_service: AuthService = Provide[Application.services.auth_service],
    ) -> ft.View:
        async def make_register(_: ft.ControlEvent):
            try:
                user_dict = {key: UserIn.str_to_field(key, val.value) for key, val in user_data.items()}
                user = UserIn.model_validate(user_dict)
                registered = await auth_service.register(user)
                if registered is True:
                    page.go("/login")
                else:
                    error.value = registered
            except TypeError as e:
                error.value = e
            error.visible = True
            page.update()

        user_data = {
            "email": ft.TextField(label="Эл. почта", value="user2@user.com"),
            "password": ft.TextField(label="Пароль", password=True, value="xxXX1234"),
            "first_name": ft.TextField(label="Имя", value="User"),
            "second_name": ft.TextField(label="Фамилия", value="User"),
            "last_name": ft.TextField(label="Отчество", value="User"),
            "birthday": ft.TextField(label="Дата рождения", hint_text="01.01.1999", value="11.05.2005"),
            "passport_serial": ft.TextField(label="Серия паспорта", hint_text="1234", value="1234"),
            "passport_number": ft.TextField(label="Номер паспорта", hint_text="123456", value="123456"),
            "gotten_by": ft.TextField(label="Кем выдан", value="string"),
            "inn": ft.TextField(label="ИНН", hint_text="123456789012", value="123456789012"),
            "registration_address": ft.TextField(label="Адрес регистрации", value="string"),
            "current_job": ft.TextField(label="Текущая работа", value="string"),
            "per_month_profit": ft.TextField(label="Ежемесячный доход, руб.", value="10500.5"),
            "phone": ft.TextField(label="Телефон", hint_text="+7 (000) 000-00-00", value="+7 (000) 000-00-00"),
            "family_status": ft.TextField(label="Семейное положение", value="string"),
        }
        user_data_len = len(user_data)
        error = ft.Text(visible=False, color=ft.Colors.RED, size=16)
        return ft.View(
            scroll=ft.ScrollMode.AUTO,
            controls=[
                ft.Column(
                    controls=[
                        ft.Text("Регистрация", size=28),
                        ft.Row(
                            vertical_alignment=ft.CrossAxisAlignment.START,
                            controls=[
                                ft.Column(
                                    width=250,
                                    controls=[*user_data.values()][:(user_data_len // 2) + 1],
                                ),
                                ft.Column(
                                    width=250,
                                    controls=[*user_data.values()][(user_data_len // 2) + 1:],
                                )
                            ]
                        ),
                        error,
                        ft.ElevatedButton(
                            text="Зарегистрироваться",
                            on_click=make_register,
                        ),
                        ft.ElevatedButton(
                            text="На главную",
                            on_click=lambda _: page.go("/")
                        )
                    ]
                ),
            ]
        )

