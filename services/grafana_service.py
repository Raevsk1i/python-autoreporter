# services.grafana_service.py
import json
from dataclasses import dataclass
from pathlib import Path
import logging

import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime
from zoneinfo import ZoneInfo

from configuration.app_config import GrafanaConfig
from configuration.credentials import get_grafana_token, get_grafana_password, get_grafana_username
from utils.helper import panel_filename

logger = logging.getLogger("GrafanaService")

_TIME_FORMATS = ("%Y-%m-%d %H:%M:%S", "%Y.%m.%d %H:%M:%S")


@dataclass(frozen=True)
class Panel:
    panel_id: str
    panel_name: str


@dataclass(frozen=True)
class Dashboard:
    name: str
    dashboard_uid: str
    dashboard_slug: str
    panels: list[Panel]


class GrafanaService:

    def __init__(self, config: GrafanaConfig):
        self._config = config
        self._log = logger
        self._grafana_url = config.url
        self._timezone = config.timezone
        self._width = config.width
        self._height = config.height
        self._timeout = float(config.timeout)
        self._org_id = config.org_id
        self._tmp_dir = Path(config.tmp_dir)
        self._dashboards_path = Path(config.dashboards_path)

    def load_dashboards(self) -> dict[str, Dashboard]:
        """
        Загружает список дашбордов и панелей из JSON.
        """

        with open(self._dashboards_path, encoding="utf-8") as f:
            data = json.load(f)

        result = {}
        for dashboard_name, dashboard_data in data.items():
            panels = [
                Panel(
                    panel_id=str(panel["panel_id"]),
                    panel_name=panel["panel_name"]
                )
                for panel in dashboard_data["panels"]
            ]

            result[dashboard_name] = Dashboard(
                name=dashboard_name,
                dashboard_uid=dashboard_data["dashboard_uid"],
                dashboard_slug=dashboard_data["dashboard_slug"],
                panels=panels,
            )

        return result

    def _convert_time_to_ms(self, time_str: str) -> int:
        """
        Конвертирует дату с часами в unix ms Timestamp в tz Europe/Moscow
        """

        for time_format in _TIME_FORMATS:
            try:
                dt_native = datetime.strptime(time_str, time_format)
                break
            except ValueError:
                continue
        else:
            raise ValueError(
                f"Неподдерживаемый формат даты: {time_str}. "
                f"Ожидается один из: {', '.join(_TIME_FORMATS)}"
            )

        dt_msk = dt_native.replace(tzinfo=ZoneInfo(self._timezone))
        return int(dt_msk.timestamp() * 1000)

    def _create_session(self) -> requests.Session:
        session = requests.Session()
        token = get_grafana_token()

        if token is not None:
            session.headers["Authorization"] = f"Bearer {token}"
        else:
            session.auth = HTTPBasicAuth(
                get_grafana_username(),
                get_grafana_password(),
            )

        return session

    def _build_render_url(
        self,
        dashboard: Dashboard,
        panel_id: str,
        from_time_ms: int,
        to_time_ms: int,
    ) -> str:
        return (
            f"{self._grafana_url}/render/d-solo/{dashboard.dashboard_uid}/"
            f"{dashboard.dashboard_slug}?OrgId={self._org_id}"
            f"&from={from_time_ms}&to={to_time_ms}&panelId={panel_id}"
            f"&width={self._width}&height={self._height}&tz={self._timezone}"
        )

    def download_grafana_panel(self, dashboard: Dashboard, from_time: str, to_time: str) -> None:
        """
        Скачивает панель из Grafana в виде PNG-изображения в папку tmp/grafana/date:timestamp
        """

        from_time_ms = self._convert_time_to_ms(from_time)
        to_time_ms = self._convert_time_to_ms(to_time)
        self._tmp_dir.mkdir(parents=True, exist_ok=True)

        with self._create_session() as session:
            for panel in dashboard.panels:
                self._log.info(f"Скачивание панели под ID {panel.panel_id}...")

                url = self._build_render_url(
                    dashboard,
                    panel.panel_id,
                    from_time_ms,
                    to_time_ms,
                )

                response = session.get(url=url, timeout=self._timeout, stream=True)
                response.raise_for_status()

                file_path = self._tmp_dir / panel_filename(panel.panel_id, panel.panel_name)
                with open(file_path, "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
