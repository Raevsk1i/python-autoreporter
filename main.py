# main.py Основной файл запуска приложения

from pathlib import Path
from configuration.app_config import load_config
from services.confluence_service import ConfluenceService
from services.grafana_service import GrafanaService, Dashboard, Panel
import configuration.credentials as credentials

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

    grafana_service = GrafanaService(CONFIG.grafana)
    confluence_service = ConfluenceService(CONFIG.confluence)
    dashboards = grafana_service.load_dashboards()
    dashboard: Dashboard = dashboards.get("leronet")
    grafana_service.download_grafana_panel(
        dashboard=dashboard,
        from_time="2026.11.23 18:03:03",
        to_time="2026.11.23 18:03:03",
    )

    for panel in dashboard.panels:
        confluence_service.upload_attachment(
            panel=panel,
            page_id="23232",
            file_path=Path("tmp/grafana_panels/".join(f"panel_{panel.panel_id}_{panel.panel_name}.png"))
        )

    html_doc = confluence_service.build_html_page(dashboard.panels)
    confluence_service.update_page(html_doc, "23232323", "srgdzrgdrgdr")

if __name__ == "__main__":
    main()
