import flet as ft

from dependency_injector.wiring import Provide, inject
from flet_route import Params, Basket

from deps.containers import Application
from services import AuthService


class LogoutView(object):
    @inject
    async def view(
            self,
            page: ft.Page,
            params: Params,
            basket: Basket,
            auth_service: AuthService = Provide[Application.services.auth_service],
    ) -> ft.View:
        await auth_service.logout()
        page.go("/login")
        return ft.View()
