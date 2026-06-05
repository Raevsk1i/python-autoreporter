# main.py Основной файл запуска приложения

from pathlib import Path
from configuration.app_config import load_config
from services.confluence_service import ConfluenceService
from services.grafana_service import GrafanaService, Dashboard
from utils.helper import panel_filename
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
    template_path = CONFIG.general.report_html_template_path or None
    confluence_service = ConfluenceService(CONFIG.confluence, template_path=template_path)
    dashboards = grafana_service.load_dashboards()
    dashboard: Dashboard = dashboards.get("leronet")
    grafana_service.download_grafana_panel(
        dashboard=dashboard,
        from_time="2026.11.23 18:03:03",
        to_time="2026.11.23 18:03:03",
    )

    tmp_dir = Path(CONFIG.grafana.tmp_dir)
    for panel in dashboard.panels:
        confluence_service.upload_attachment(
            panel=panel,
            page_id="23232",
            file_path=tmp_dir / panel_filename(panel.panel_id, panel.panel_name),
        )

    html_doc = confluence_service.build_html_page(dashboard.panels)
    confluence_service.update_page(html_doc, "23232323", "srgdzrgdrgdr")

if __name__ == "__main__":
    main()
