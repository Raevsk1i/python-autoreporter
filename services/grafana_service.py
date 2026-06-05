# services.grafana_service.py
import json
import os
from dataclasses import dataclass
from pathlib import Path
import logging

import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime
from zoneinfo import ZoneInfo

from configuration.app_config import GrafanaConfig
from configuration.credentials import get_grafana_token, get_grafana_password, get_grafana_username


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
        self._log = logging.getLogger("GrafanaService")
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
                    panel_id=panel["panel_id"],
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

        :param time_str:
        :return:
        """
        dt_native = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
        dt_msk = dt_native.replace(tzinfo=ZoneInfo(self._timezone))
        return int(dt_msk.timestamp() * 1000)

    def download_grafana_panel(self, dashboard: Dashboard, from_time: str, to_time: str) -> None:
        """
        Скачивает панель из Grafana в виде PNG-изображения в папку tmp/grafana/date:timestamp

        :param dashboard:
        :param from_time:
        :param to_time:
        :return:
        """

        for panel in dashboard.panels:
            panel_name = panel.panel_name
            panel_id = panel.panel_id
            dashboard_uid = dashboard.dashboard_uid
            dashboard_slug = dashboard.dashboard_slug
            from_time_ms = self._convert_time_to_ms(from_time)
            to_time_ms = self._convert_time_to_ms(to_time)
            filename = f"panel_{panel_id}_{panel_name}.png"


            self._log.info(f"Скачивание панели под ID {panel_id}...")

            url = (f"{self._grafana_url}/render/d-solo/{dashboard_uid}/{dashboard_slug}?OrgId={self._org_id}"
                   f"&from={from_time_ms}&to={to_time_ms}&panelId={panel_id}&width={self._width}&height={self._height}&tz={self._timezone}")

            if get_grafana_token() is not None:
                headers = {
                    "Authorization": f"Bearer {get_grafana_token()}",
                }
                response = requests.get(url=url, timeout=self._timeout, stream=True, headers=headers)
            else:
                response = requests.get(url=url,
                                        timeout=self._timeout,
                                        auth=HTTPBasicAuth(get_grafana_username(), get_grafana_password()),
                                        stream=True)

            response.raise_for_status()

            Path(self._tmp_dir).parent.mkdir(
                parents=True,
                exist_ok=True,
            )
            file = self._tmp_dir + "/".join(filename)
            with open(file, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)


