from dependency_injector import containers, providers

from services import *


class Services(containers.DeclarativeContainer):
    config = providers.Configuration()

    auth_service = providers.Singleton(
        AuthService,
    )
    orders_service = providers.Singleton(
        OrdersService,
    )
    responses_service = providers.Singleton(
        ResponsesService,
    )
    credits_service = providers.Singleton(
        CreditsService,
    )


class Application(containers.DeclarativeContainer):
    config = providers.Configuration()

    services = providers.Container(
        Services,
        config=config,
    )
