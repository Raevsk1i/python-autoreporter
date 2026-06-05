"""Точка входа приложения python-autoreporter."""

import configuration.credentials as credentials
from configuration.app_config import load_config
from services.report_service import ReportService

CONFIG = load_config()


def main() -> None:
    """Настраивает учётные данные и запускает создание отчёта."""
    credentials.set_confluence_auth(
        username="sds",
        token="dsds",
    )

    credentials.set_grafana_basicauth(
        username="sds",
        password="sds",
    )

    report_service = ReportService(CONFIG)
    report_service.create_report(
        from_time="2026.11.23 18:03:03",
        to_time="2026.11.23 18:03:03",
        dashboard="leronet",
        parent_id="232323",
        title="Отчёт",
    )


if __name__ == "__main__":
    main()
