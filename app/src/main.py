import flet as ft
from flet_route import path, Routing

from deps.containers import Application
from views.login import LoginView
from views.home import HomeView


APP_ROUTES = [
    path("/", True, HomeView().view),
    path("/login", True, LoginView().view),
]


def main(page: ft.Page):
    page.title = "Credit Bank"
    page.window.height = 600
    page.window.width = 800

    Routing(page=page, app_routes=APP_ROUTES, async_is=True)
    page.go("/login")


if __name__ == "__main__":
    try:
        application = Application()
        application.wire(packages=["views"])
        ft.app(main)
    except RuntimeError as e:
        print(e)
