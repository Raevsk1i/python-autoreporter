# services.report_service.py
from pathlib import Path

from PySide6.scripts.deploy_lib import Config

from configuration.app_config import AppConfig
from services.confluence_service import ConfluenceService
from services.grafana_service import GrafanaService, Dashboard
import logging


class ReportService:
    def __init__(self,
                 config: AppConfig
                 ):
        self._log = logging.getLogger(__name__)
        self._config = config
        self._confluence_service = ConfluenceService(self._config.confluence)
        self._grafana_service = GrafanaService(self._config.grafana)
        self._dashboards = self._grafana_service.load_dashboards()

    def create_report(self,
                      from_time: str,
                      to_time: str,
                      dashboard: str,
                      parent_id: str,
                      title: str,
    ) -> None:
        dashboard = self._dashboards.get(dashboard)

        if dashboard is None:
            self._log.info("Дашборд не был найден")
            raise EOFError

        self._grafana_service.download_grafana_panel(
            dashboard=dashboard,
            from_time=from_time,
            to_time=to_time,
        )

        html_doc = self._confluence_service.build_html_page(dashboard.panels)
        new_page = self._confluence_service.create_page_with_body(
            html=html_doc,
            title=title,
            parent_id=parent_id
        )

        new_page_id = new_page.get("id")

        for panel in dashboard.panels:
            self._confluence_service.upload_attachment(
                panel=panel,
                page_id=new_page_id,
                file_path=Path(f"{self._config.grafana.tmp_dir}/" + f"panel_{panel.panel_id}_{panel.panel_name}.png")
            )

    def update_report(
            self,
            from_time: str,
            to_time: str,
            dashboard: str,
            page_id: str,
            title: str,
    ):
        dashboard = self._dashboards.get(dashboard)

        if dashboard is None:
            self._log.info("Дашборд не был найден")
            raise EOFError

        self._grafana_service.download_grafana_panel(
            dashboard=dashboard,
            from_time=from_time,
            to_time=to_time,
        )
        html_doc = self._confluence_service.build_html_page(dashboard.panels)

        for panel in dashboard.panels:
            self._confluence_service.upload_attachment(
                panel=panel,
                page_id=page_id,
                file_path=Path(f"{self._config.grafana.tmp_dir}/" + f"panel_{panel.panel_id}_{panel.panel_name}.png")
            )

        self._confluence_service.update_page(
            page_id=page_id,
            title=title,
            html=html_doc,
        )

    def reload_dashboards(self) -> None:
        self._dashboards = self._grafana_service.load_dashboards()

    def get_dashboards(self) -> dict[str, Dashboard]:
        return self._dashboards