# app_config.py подтягивает конфиги в классы

from configparser import ConfigParser
from dataclasses import dataclass
from pathlib import Path

import keyring

from configuration.credentials import SERVICE_NAME


#=====================================================================#
#                           Configuration                             #
#=====================================================================#


@dataclass(frozen=True)
class GrafanaConfig:
    url: str
    width: str
    height: str
    timeout: str
    timezone: str
    org_id: str
    tmp_dir: str
    dashboards_path: str


@dataclass(frozen=True)
class ConfluenceConfig:
    url: str
    space_key: str
    ssl_certificate_path: str


@dataclass(frozen=True)
class GeneralConfig:
    report_html_template_path: str
    qss_path: str


@dataclass(frozen=True)
class AppConfig:
    grafana: GrafanaConfig
    confluence: ConfluenceConfig
    general: GeneralConfig


def get_config_path() -> Path:
    """
    Ищет config.ini в следующем порядке:

    1. Путь из keyring
    2. ./config.ini

    Если файл не найден — выбрасывает FileNotFoundError.
    """

    stored_path = keyring.get_password(
        SERVICE_NAME,
        "CONFIG_PATH",
    )

    if stored_path:
        config_path = Path(stored_path)

        if config_path.is_file():
            return config_path

        try:
            keyring.delete_password(
                SERVICE_NAME,
                "CONFIG_PATH",
            )
        except Exception:
            pass

    local_config = Path("config.ini")

    if local_config.is_file():
        return local_config

    raise FileNotFoundError(
        "Конфигурационный файл не найден."
    )


def save_config_path(path: str | Path) -> None:
    """
    Сохраняет путь к конфигу в keyring.
    """

    keyring.set_password(
        SERVICE_NAME,
        "CONFIG_PATH",
        str(path),
    )


def load_config(config_path: str | Path | None = None,) -> AppConfig:
    """
    Загружает конфигурацию приложения.

    Если путь не указан —
    используется get_config_path().
    """

    if config_path is None:
        config_path = get_config_path()

    config_path = Path(config_path)

    if not config_path.is_file():
        raise FileNotFoundError(
            f"Файл конфигурации не найден: {config_path}"
        )

    parser = ConfigParser()

    files = parser.read(
        config_path,
        encoding="utf-8",
    )

    if not files:
        raise RuntimeError(
            f"Не удалось прочитать конфиг: {config_path}"
        )

    grafana = GrafanaConfig(
        url=parser.get("grafana", "url"),
        width=parser.get("grafana", "width"),
        height=parser.get("grafana", "height"),
        timeout=parser.get("grafana", "timeout"),
        timezone=parser.get("grafana", "timezone"),
        org_id=parser.get("grafana", "org_id"),
        tmp_dir=parser.get("general", "tmp_dir", ),
        dashboards_path=parser.get("general", "dashboards_path", ),
    )

    confluence = ConfluenceConfig(
        url=parser.get("confluence", "url"),
        space_key=parser.get("confluence","space_key",),
        ssl_certificate_path=parser.get("confluence","ssl_certificate_path",),
    )

    general = GeneralConfig(
        report_html_template_path=parser.get("general","report_html_template_path",),
        qss_path=parser.get("general","qss_path",),
    )

    return AppConfig(
        grafana=grafana,
        confluence=confluence,
        general=general,
    )