"""Хранение и получение учётных данных через системное хранилище keyring."""

import keyring

SERVICE_NAME = "python-autoreporter"

GRAFANA_DASHBOARD_REGISTRY = "GRAFANA_DASHBOARD_REGISTRY"
GRAFANA_DASHBOARD_FIELDS = ("API_TOKEN", "USERNAME", "PASSWORD")

_LEGACY_GRAFANA_KEYS = (
    "GRAFANA_USERNAME",
    "GRAFANA_PASSWORD",
    "GRAFANA_API_TOKEN",
)

_CREDENTIAL_KEYS = (
    "CONFLUENCE_USERNAME",
    "CONFLUENCE_API_TOKEN",
)


def _safe_delete_password(key: str) -> None:
    try:
        keyring.delete_password(SERVICE_NAME, key)
    except Exception:
        pass


def _grafana_dashboard_cred_key(dashboard_key: str, field: str) -> str:
    return f"GRAFANA__{dashboard_key}__{field}"


def _get_grafana_dashboard_registry() -> set[str]:
    raw = keyring.get_password(SERVICE_NAME, GRAFANA_DASHBOARD_REGISTRY)
    if not raw:
        return set()
    return {key for key in raw.split("\n") if key}


def _save_grafana_dashboard_registry(keys: set[str]) -> None:
    if keys:
        keyring.set_password(
            SERVICE_NAME,
            GRAFANA_DASHBOARD_REGISTRY,
            "\n".join(sorted(keys)),
        )
        return

    _safe_delete_password(GRAFANA_DASHBOARD_REGISTRY)


def _register_grafana_dashboard(dashboard_key: str) -> None:
    keys = _get_grafana_dashboard_registry()
    keys.add(dashboard_key)
    _save_grafana_dashboard_registry(keys)


def _unregister_grafana_dashboard(dashboard_key: str) -> None:
    keys = _get_grafana_dashboard_registry()
    keys.discard(dashboard_key)
    _save_grafana_dashboard_registry(keys)


def get_confluence_token() -> str | None:
    """Возвращает API-токен Confluence из keyring."""
    return keyring.get_password(SERVICE_NAME, "CONFLUENCE_API_TOKEN")


def get_confluence_username() -> str | None:
    """Возвращает имя пользователя Confluence из keyring."""
    return keyring.get_password(SERVICE_NAME, "CONFLUENCE_USERNAME")


def get_grafana_token_for_dashboard(dashboard_key: str) -> str | None:
    """Возвращает API-токен Grafana для указанного дашборда."""
    return keyring.get_password(
        SERVICE_NAME,
        _grafana_dashboard_cred_key(dashboard_key, "API_TOKEN"),
    )


def get_grafana_username_for_dashboard(dashboard_key: str) -> str | None:
    """Возвращает имя пользователя Grafana для указанного дашборда."""
    return keyring.get_password(
        SERVICE_NAME,
        _grafana_dashboard_cred_key(dashboard_key, "USERNAME"),
    )


def get_grafana_password_for_dashboard(dashboard_key: str) -> str | None:
    """Возвращает пароль Grafana для указанного дашборда."""
    return keyring.get_password(
        SERVICE_NAME,
        _grafana_dashboard_cred_key(dashboard_key, "PASSWORD"),
    )


def set_grafana_dashboard_token(dashboard_key: str, token: str) -> None:
    """Сохраняет API-токен Grafana для указанного дашборда."""
    keyring.set_password(
        SERVICE_NAME,
        _grafana_dashboard_cred_key(dashboard_key, "API_TOKEN"),
        token,
    )
    _register_grafana_dashboard(dashboard_key)


def set_grafana_dashboard_basicauth(
    dashboard_key: str,
    username: str,
    password: str,
) -> None:
    """Сохраняет учётные данные Grafana (логин и пароль) для указанного дашборда."""
    keyring.set_password(
        SERVICE_NAME,
        _grafana_dashboard_cred_key(dashboard_key, "USERNAME"),
        username,
    )
    keyring.set_password(
        SERVICE_NAME,
        _grafana_dashboard_cred_key(dashboard_key, "PASSWORD"),
        password,
    )
    _register_grafana_dashboard(dashboard_key)


def clear_grafana_dashboard_credentials(dashboard_key: str) -> None:
    """Удаляет учётные данные Grafana для указанного дашборда из keyring."""
    for field in GRAFANA_DASHBOARD_FIELDS:
        _safe_delete_password(_grafana_dashboard_cred_key(dashboard_key, field))
    _unregister_grafana_dashboard(dashboard_key)


def rename_grafana_dashboard_credentials(old_key: str, new_key: str) -> None:
    """Переносит учётные данные Grafana при переименовании ключа дашборда."""
    if old_key == new_key:
        return

    for field in GRAFANA_DASHBOARD_FIELDS:
        value = keyring.get_password(
            SERVICE_NAME,
            _grafana_dashboard_cred_key(old_key, field),
        )
        if value is not None:
            keyring.set_password(
                SERVICE_NAME,
                _grafana_dashboard_cred_key(new_key, field),
                value,
            )
            _safe_delete_password(_grafana_dashboard_cred_key(old_key, field))

    registry = _get_grafana_dashboard_registry()
    if old_key in registry:
        registry.discard(old_key)
        registry.add(new_key)
        _save_grafana_dashboard_registry(registry)


def clear_all_grafana_dashboard_credentials() -> None:
    """Удаляет учётные данные Grafana для всех зарегистрированных дашбордов."""
    for dashboard_key in list(_get_grafana_dashboard_registry()):
        clear_grafana_dashboard_credentials(dashboard_key)
    _safe_delete_password(GRAFANA_DASHBOARD_REGISTRY)


def set_confluence_auth(username: str, token: str) -> None:
    """Сохраняет учётные данные Confluence (логин и токен) в keyring."""
    keyring.set_password(SERVICE_NAME, "CONFLUENCE_USERNAME", username)
    keyring.set_password(SERVICE_NAME, "CONFLUENCE_API_TOKEN", token)


def clear_all_credentials() -> None:
    """Удаляет все учётные данные приложения из keyring."""
    for key in _CREDENTIAL_KEYS:
        _safe_delete_password(key)

    for key in _LEGACY_GRAFANA_KEYS:
        _safe_delete_password(key)

    clear_all_grafana_dashboard_credentials()
