# configuration.credentials.py

import keyring

SERVICE_NAME = "python-autoreporter"

# def set_value(token: str, value: str) -> None:
#     keyring.set_password(SERVICE_NAME, token, value)
#
# def get_value(token: str) -> str | None:
#     return keyring.get_password(SERVICE_NAME, token)

def get_confluence_token() -> str | None:
    return keyring.get_password(SERVICE_NAME, "CONFLUENCE_API_TOKEN")

def get_confluence_username() -> str | None:
    return keyring.get_password(SERVICE_NAME, "CONFLUENCE_USERNAME")

def get_grafana_token() -> str | None:
    return keyring.get_password(SERVICE_NAME, "GRAFANA_API_TOKEN")

def get_grafana_username() -> str | None:
    return keyring.get_password(SERVICE_NAME, "GRAFANA_USERNAME")

def get_grafana_password() -> str | None:
    return keyring.get_password(SERVICE_NAME, "GRAFANA_PASSWORD")

def set_grafana_token(token: str) -> None:
    keyring.set_password(SERVICE_NAME, "GRAFANA__API_TOKEN", token)

def set_confluence_auth(username: str, token: str) -> None:
    keyring.set_password(SERVICE_NAME, "CONFLUENCE_USERNAME", username)
    keyring.set_password(SERVICE_NAME, "CONFLUENCE_API_TOKEN", token)

def set_grafana_basicauth(username: str, password: str) -> None:
    keyring.set_password(SERVICE_NAME, "GRAFANA_USERNAME", username)
    keyring.set_password(SERVICE_NAME, "GRAFANA_PASSWORD", password)

