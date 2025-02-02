import flet as ft
from flet_route import path, Routing

from deps.containers import Application
from views.credits import CreditsView
from views.login import LoginView
from views.home import HomeView
from views.register import RegisterView
from views.logout import LogoutView
from views.specs_credits import SpecsCreditsView
from views.specs_orders import SpecsOrdersView
from views.orders import OrdersView


APP_ROUTES = [
    path("/", True, HomeView().view),
    path("/login", True, LoginView().view),
    path("/logout", True, LogoutView().view),
    path("/register", True, RegisterView().view),
    path("/specs/orders", True, SpecsOrdersView().view),
    path("/specs/credits", True, SpecsCreditsView().view),
    path("/orders", True, OrdersView().view),
    path("/credits", True, CreditsView().view)
]


def main(page: ft.Page):
    page.title = "Credit Bank"
    page.window.height = 650
    page.window.width = 850

    Routing(page=page, app_routes=APP_ROUTES, async_is=True)
    page.go("/login")


if __name__ == "__main__":
    try:
        application = Application()
        application.wire(packages=["views"])
        ft.app(main)
    except RuntimeError as e:
        print(e)
