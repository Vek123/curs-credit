from dependency_injector import containers, providers

from services import *


class Services(containers.DeclarativeContainer):
    config = providers.Configuration()

    auth_service = providers.Factory(
        AuthService,
    )


class Application(containers.DeclarativeContainer):
    config = providers.Configuration()

    services = providers.Container(
        Services,
        config=config,
    )
