"""Загрузка и хранение конфигурации приложения из config.ini."""

from configparser import ConfigParser
from dataclasses import dataclass
from pathlib import Path

import keyring

from configuration.credentials import SERVICE_NAME


@dataclass(frozen=True)
class GrafanaConfig:
    """Параметры подключения к Grafana и рендеринга панелей."""

    width: str
    height: str
    timeout: str
    timezone: str
    org_id: str
    tmp_dir: str
    dashboards_path: str
    async_enabled: bool
    max_workers: str


@dataclass(frozen=True)
class ConfluenceConfig:
    """Параметры подключения к Confluence и публикации отчётов."""

    url: str
    space_key: str
    ssl_certificate_path: str
    macro_id: str
    async_enabled: bool
    max_workers: str


@dataclass(frozen=True)
class GeneralConfig:
    """Общие пути к шаблонам и ресурсам приложения."""

    report_html_template_path: str
    qss_path: str


@dataclass(frozen=True)
class AppConfig:
    """Корневая конфигурация приложения, объединяющая все секции."""

    grafana: GrafanaConfig
    confluence: ConfluenceConfig
    general: GeneralConfig


def default_config() -> AppConfig:
    """Возвращает конфигурацию приложения по умолчанию."""
    return AppConfig(
        grafana=GrafanaConfig(
            width="",
            height="",
            timeout="30",
            timezone="Europe/Moscow",
            org_id="1",
            tmp_dir="tmp/grafana_panels",
            dashboards_path="data/dashboards.json",
            async_enabled=False,
            max_workers="4",
        ),
        confluence=ConfluenceConfig(
            url="",
            space_key="",
            ssl_certificate_path="",
            macro_id="9dbdf19d-b8c1-2g5d-b3e5-7f1e3a84682e",
            async_enabled=False,
            max_workers="4",
        ),
        general=GeneralConfig(
            report_html_template_path="",
            qss_path="data/style.qss",
        ),
    )


def clear_config_path() -> None:
    """Удаляет пользовательский путь к config.ini из keyring."""
    try:
        keyring.delete_password(SERVICE_NAME, "CONFIG_PATH")
    except Exception:
        pass


def get_config_path() -> Path:
    """
    Возвращает путь к файлу config.ini.

    Поиск выполняется в следующем порядке:
    1. Путь, сохранённый в keyring.
    2. Локальный файл ./config.ini.

    Raises:
        FileNotFoundError: Если конфигурационный файл не найден.
    """
    stored_path = keyring.get_password(SERVICE_NAME, "CONFIG_PATH")

    if stored_path:
        config_path = Path(stored_path)

        if config_path.is_file():
            return config_path

        try:
            keyring.delete_password(SERVICE_NAME, "CONFIG_PATH")
        except Exception:
            pass

    local_config = Path("config.ini")

    if local_config.is_file():
        return local_config

    raise FileNotFoundError("Конфигурационный файл не найден.")


def save_config_path(path: str | Path) -> None:
    """Сохраняет путь к конфигурационному файлу в keyring."""
    keyring.set_password(SERVICE_NAME, "CONFIG_PATH", str(path))


def load_config(config_path: str | Path | None = None) -> AppConfig:
    """
    Загружает конфигурацию приложения из INI-файла.

    Args:
        config_path: Путь к config.ini. Если не указан, используется get_config_path().

    Raises:
        FileNotFoundError: Если файл конфигурации не существует.
        RuntimeError: Если файл не удалось прочитать.
    """
    if config_path is None:
        config_path = get_config_path()

    config_path = Path(config_path)

    if not config_path.is_file():
        raise FileNotFoundError(f"Файл конфигурации не найден: {config_path}")

    parser = ConfigParser()
    files = parser.read(config_path, encoding="utf-8")

    if not files:
        raise RuntimeError(f"Не удалось прочитать конфиг: {config_path}")

    legacy_async = parser.getboolean("general", "async", fallback=False)
    legacy_max_workers = parser.get("general", "max_workers", fallback="4")

    grafana = GrafanaConfig(
        width=parser.get("grafana", "width"),
        height=parser.get("grafana", "height"),
        timeout=parser.get("grafana", "timeout"),
        timezone=parser.get("grafana", "timezone"),
        org_id=parser.get("grafana", "org_id"),
        tmp_dir=parser.get("grafana", "tmp_dir"),
        dashboards_path=parser.get("grafana", "dashboards_path"),
        async_enabled=parser.getboolean("grafana", "async", fallback=legacy_async),
        max_workers=parser.get("grafana", "max_workers", fallback=legacy_max_workers),
    )

    confluence = ConfluenceConfig(
        url=parser.get("confluence", "url"),
        space_key=parser.get("confluence", "space_key"),
        ssl_certificate_path=parser.get("confluence", "ssl_certificate_path"),
        macro_id=parser.get("confluence", "macro_id"),
        async_enabled=parser.getboolean("confluence", "async", fallback=legacy_async),
        max_workers=parser.get("confluence", "max_workers", fallback=legacy_max_workers),
    )

    general = GeneralConfig(
        report_html_template_path=parser.get("general", "report_html_template_path"),
        qss_path=parser.get("general", "qss_path"),
    )

    return AppConfig(
        grafana=grafana,
        confluence=confluence,
        general=general,
    )


def save_config(config: AppConfig, config_path: str | Path | None = None) -> Path:
    """
    Сохраняет конфигурацию приложения в INI-файл.

    Args:
        config: Объект конфигурации для записи.
        config_path: Путь к config.ini. Если не указан, используется get_config_path().

    Returns:
        Путь к сохранённому файлу конфигурации.
    """
    if config_path is None:
        config_path = get_config_path()

    config_path = Path(config_path)
    parser = ConfigParser()

    parser["grafana"] = {
        "width": config.grafana.width,
        "height": config.grafana.height,
        "timeout": config.grafana.timeout,
        "timezone": config.grafana.timezone,
        "org_id": config.grafana.org_id,
        "tmp_dir": config.grafana.tmp_dir,
        "dashboards_path": config.grafana.dashboards_path,
        "async": str(config.grafana.async_enabled).lower(),
        "max_workers": config.grafana.max_workers,
    }

    parser["confluence"] = {
        "url": config.confluence.url,
        "space_key": config.confluence.space_key,
        "ssl_certificate_path": config.confluence.ssl_certificate_path,
        "macro_id": config.confluence.macro_id,
        "async": str(config.confluence.async_enabled).lower(),
        "max_workers": config.confluence.max_workers,
    }

    parser["general"] = {
        "report_html_template_path": config.general.report_html_template_path,
        "qss_path": config.general.qss_path,
    }

    with open(config_path, "w", encoding="utf-8") as file:
        parser.write(file)

    return config_path
