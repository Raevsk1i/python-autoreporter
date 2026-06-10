"""Сервис для загрузки дашбордов и скачивания панелей Grafana."""

import json
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import requests
from requests.auth import HTTPBasicAuth

from configuration.app_config import GrafanaConfig
from configuration.credentials import (
    get_grafana_password_for_dashboard,
    get_grafana_token_for_dashboard,
    get_grafana_username_for_dashboard,
)

TIME_FORMAT = "%Y-%m-%d %H:%M:%S"
DOWNLOAD_CHUNK_SIZE = 8192


@dataclass(frozen=True)
class Panel:
    """Панель Grafana с идентификатором и отображаемым именем."""

    panel_id: str
    panel_name: str


@dataclass(frozen=True)
class Dashboard:
    """Дашборд Grafana со списком панелей."""

    name: str
    grafana_url: str
    dashboard_uid: str
    dashboard_slug: str
    panels: list[Panel]


class GrafanaService:
    """Клиент для работы с API рендеринга Grafana."""

    def __init__(
        self,
        config: GrafanaConfig,
        *,
        parallel: bool = False,
        max_workers: int = 4,
    ) -> None:
        """
        Инициализирует сервис параметрами из конфигурации.

        Args:
            config: Секция настроек Grafana из AppConfig.
            parallel: Включить многопоточное скачивание панелей.
            max_workers: Максимальное число потоков при параллельном скачивании.
        """
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        )

        self._config = config
        self._log = logging.getLogger("GrafanaService")
        self._timezone = config.timezone
        self._width = config.width
        self._height = config.height
        self._timeout = float(config.timeout)
        self._org_id = config.org_id
        self._tmp_dir = Path(config.tmp_dir)
        self._dashboards_path = Path(config.dashboards_path)
        self._parallel = parallel
        self._max_workers = max(1, max_workers)

    def load_dashboards(self) -> dict[str, Dashboard]:
        """
        Загружает список дашбордов и их панелей из JSON-файла.

        Returns:
            Словарь {имя_дашборда: Dashboard}.
        """
        with open(self._dashboards_path, encoding="utf-8") as file:
            data = json.load(file)

        dashboards: dict[str, Dashboard] = {}

        for dashboard_name, dashboard_data in data.items():
            panels = [
                Panel(
                    panel_id=panel["panel_id"],
                    panel_name=panel["panel_name"],
                )
                for panel in dashboard_data["panels"]
            ]

            dashboards[dashboard_name] = Dashboard(
                name=dashboard_name,
                grafana_url=dashboard_data["grafana_url"],
                dashboard_uid=dashboard_data["dashboard_uid"],
                dashboard_slug=dashboard_data["dashboard_slug"],
                panels=panels,
            )

        return dashboards

    def _convert_time_to_ms(self, time_str: str) -> int:
        """
        Конвертирует строку даты-времени в Unix timestamp (миллисекунды).

        Args:
            time_str: Дата и время в формате YYYY-MM-DD HH:MM:SS.

        Returns:
            Временная метка в миллисекундах с учётом часового пояса из конфига.
        """
        dt_native = datetime.strptime(time_str, TIME_FORMAT)
        dt_with_tz = dt_native.replace(tzinfo=ZoneInfo(self._timezone))
        return int(dt_with_tz.timestamp() * 1000)

    def _build_render_url(
        self,
        dashboard: Dashboard,
        panel_id: str,
        from_time_ms: int,
        to_time_ms: int,
    ) -> str:
        """Формирует URL для рендеринга отдельной панели Grafana."""
        grafana_url = dashboard.grafana_url.rstrip("/")
        return (
            f"{grafana_url}/render/d-solo/"
            f"{dashboard.dashboard_uid}/{dashboard.dashboard_slug}"
            f"?OrgId={self._org_id}"
            f"&from={from_time_ms}&to={to_time_ms}"
            f"&panelId={panel_id}"
            f"&width={self._width}&height={self._height}"
            f"&tz={self._timezone}"
        )

    def _download_panel_image(self, url: str, dashboard: Dashboard) -> requests.Response:
        """
        Выполняет HTTP-запрос на скачивание изображения панели.

        Использует Bearer-токен дашборда, если он задан, иначе — Basic Auth.
        """
        token = get_grafana_token_for_dashboard(dashboard.name)

        if token is not None:
            headers = {"Authorization": f"Bearer {token}"}
            return requests.get(
                url=url,
                timeout=self._timeout,
                stream=True,
                headers=headers,
            )

        return requests.get(
            url=url,
            timeout=self._timeout,
            auth=HTTPBasicAuth(
                get_grafana_username_for_dashboard(dashboard.name),
                get_grafana_password_for_dashboard(dashboard.name),
            ),
            stream=True,
        )

    def _save_panel_to_disk(self, response: requests.Response, filename: str) -> None:
        """Сохраняет потоковый ответ HTTP в PNG-файл во временной директории."""
        self._tmp_dir.mkdir(parents=True, exist_ok=True)
        file_path = self._tmp_dir / filename

        with open(file_path, "wb") as file:
            for chunk in response.iter_content(chunk_size=DOWNLOAD_CHUNK_SIZE):
                file.write(chunk)

    def _download_single_panel(
        self,
        dashboard: Dashboard,
        panel: Panel,
        from_time_ms: int,
        to_time_ms: int,
    ) -> None:
        """Скачивает одну панель дашборда и сохраняет её на диск."""
        filename = f"panel_{panel.panel_id}_{panel.panel_name}.png"
        self._log.info("Скачивание панели под ID %s...", panel.panel_id)

        url = self._build_render_url(
            dashboard=dashboard,
            panel_id=panel.panel_id,
            from_time_ms=from_time_ms,
            to_time_ms=to_time_ms,
        )

        response = self._download_panel_image(url, dashboard)
        response.raise_for_status()
        self._save_panel_to_disk(response, filename)

    def download_grafana_panel(
        self,
        dashboard: Dashboard,
        from_time: str,
        to_time: str,
    ) -> None:
        """
        Скачивает все панели дашборда в виде PNG-изображений.

        Файлы сохраняются во временную директорию, указанную в конфигурации.
        При включённом многопоточном режиме панели скачиваются параллельно.

        Args:
            dashboard: Дашборд с перечнем панелей для скачивания.
            from_time: Начало временного диапазона (YYYY-MM-DD HH:MM:SS).
            to_time: Конец временного диапазона (YYYY-MM-DD HH:MM:SS).
        """
        from_time_ms = self._convert_time_to_ms(from_time)
        to_time_ms = self._convert_time_to_ms(to_time)

        if not self._parallel or len(dashboard.panels) <= 1:
            for panel in dashboard.panels:
                self._download_single_panel(
                    dashboard=dashboard,
                    panel=panel,
                    from_time_ms=from_time_ms,
                    to_time_ms=to_time_ms,
                )
            return

        with ThreadPoolExecutor(max_workers=self._max_workers) as executor:
            futures = [
                executor.submit(
                    self._download_single_panel,
                    dashboard,
                    panel,
                    from_time_ms,
                    to_time_ms,
                )
                for panel in dashboard.panels
            ]

            for future in as_completed(futures):
                future.result()
