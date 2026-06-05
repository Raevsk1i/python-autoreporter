# main.py Основной файл запуска приложения

from pathlib import Path
from configuration.app_config import load_config
from services.confluence_service import ConfluenceService
from services.grafana_service import GrafanaService, Dashboard, Panel
import configuration.credentials as credentials
from services.report_service import ReportService

CONFIG = load_config()


def main():

    credentials.set_confluence_auth(
        username="sds",
        token="dsds",
    )

    credentials.set_grafana_basicauth(
        username="sds",
        password="sds"
    )

    report_service = ReportService(CONFIG)
    report_service.create_report(
        from_time="2026.11.23 18:03:03",
        to_time="2026.11.23 18:03:03",
        dashboard="leronet",
        parent_id="232323"
    )

if __name__ == "__main__":
    main()
