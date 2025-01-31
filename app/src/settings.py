from pathlib import Path


class Settings(object):
    api_host: str = "127.0.0.1"
    api_port: int = 8000
    api_base_url: str = f"http://{api_host}:{api_port}/"

    project_root: Path = Path(__name__).parent.resolve()


settings = Settings()
