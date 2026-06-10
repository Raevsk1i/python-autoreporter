"""Хранение и получение учётных данных через системное хранилище keyring."""

import keyring

SERVICE_NAME = "python-autoreporter"

_CREDENTIAL_KEYS = (
    "CONFLUENCE_USERNAME",
    "CONFLUENCE_API_TOKEN",
    "GRAFANA_USERNAME",
    "GRAFANA_PASSWORD",
    "GRAFANA_API_TOKEN",
)


def get_confluence_token() -> str | None:
    """Возвращает API-токен Confluence из keyring."""
    return keyring.get_password(SERVICE_NAME, "CONFLUENCE_API_TOKEN")


def get_confluence_username() -> str | None:
    """Возвращает имя пользователя Confluence из keyring."""
    return keyring.get_password(SERVICE_NAME, "CONFLUENCE_USERNAME")


def get_grafana_token() -> str | None:
    """Возвращает API-токен Grafana из keyring."""
    return keyring.get_password(SERVICE_NAME, "GRAFANA_API_TOKEN")


def get_grafana_username() -> str | None:
    """Возвращает имя пользователя Grafana из keyring."""
    return keyring.get_password(SERVICE_NAME, "GRAFANA_USERNAME")


def get_grafana_password() -> str | None:
    """Возвращает пароль Grafana из keyring."""
    return keyring.get_password(SERVICE_NAME, "GRAFANA_PASSWORD")


def set_grafana_token(token: str) -> None:
    """Сохраняет API-токен Grafana в keyring."""
    keyring.set_password(SERVICE_NAME, "GRAFANA_API_TOKEN", token)


def set_confluence_auth(username: str, token: str) -> None:
    """Сохраняет учётные данные Confluence (логин и токен) в keyring."""
    keyring.set_password(SERVICE_NAME, "CONFLUENCE_USERNAME", username)
    keyring.set_password(SERVICE_NAME, "CONFLUENCE_API_TOKEN", token)


def set_grafana_basicauth(username: str, password: str) -> None:
    """Сохраняет учётные данные Grafana (логин и пароль) в keyring."""
    keyring.set_password(SERVICE_NAME, "GRAFANA_USERNAME", username)
    keyring.set_password(SERVICE_NAME, "GRAFANA_PASSWORD", password)


def clear_all_credentials() -> None:
    """Удаляет все учётные данные приложения из keyring."""
    for key in _CREDENTIAL_KEYS:
        try:
            keyring.delete_password(SERVICE_NAME, key)
        except Exception:
            pass
