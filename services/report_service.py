"""Сервис оркестрации создания и обновления отчётов Grafana → Confluence."""

import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from configuration.app_config import AppConfig
from services.confluence_service import ConfluenceService
from services.grafana_service import Dashboard, GrafanaService


class ReportService:
    """Координирует скачивание панелей Grafana и публикацию отчёта в Confluence."""

    def __init__(self, config: AppConfig) -> None:
        """
        Инициализирует сервисы Grafana и Confluence, загружает дашборды.

        Args:
            config: Полная конфигурация приложения.
        """
        self._log = logging.getLogger(__name__)
        self._config = config
        self._confluence_service = ConfluenceService(self._config.confluence)
        self._grafana_service = GrafanaService(
            self._config.grafana,
            parallel=self._config.grafana.async_enabled,
            max_workers=self._get_max_workers(),
        )
        self._dashboards = self._grafana_service.load_dashboards()

    def _get_max_workers(self) -> int:
        """Возвращает максимальное число потоков из конфигурации."""
        try:
            return max(1, int(self._config.general.max_workers))
        except ValueError:
            self._log.warning(
                "Некорректное значение max_workers: %s. Используется 4.",
                self._config.general.max_workers,
            )
            return 4

    def _get_dashboard(self, dashboard_name: str) -> Dashboard:
        """
        Возвращает дашборд по имени или выбрасывает исключение.

        Args:
            dashboard_name: Ключ дашборда из JSON-конфигурации.

        Raises:
            EOFError: Если дашборд с указанным именем не найден.
        """
        dashboard = self._dashboards.get(dashboard_name)

        if dashboard is None:
            self._log.info("Дашборд не был найден: %s", dashboard_name)
            raise EOFError(f"Дашборд не найден: {dashboard_name}")

        return dashboard

    def _panel_file_path(self, panel_id: str, panel_name: str) -> Path:
        """Возвращает путь к PNG-файлу панели во временной директории Grafana."""
        filename = f"panel_{panel_id}_{panel_name}.png"
        return Path(self._config.grafana.tmp_dir) / filename

    def _upload_single_panel(self, panel, page_id: str) -> None:
        """Загружает PNG-файл одной панели как вложение на страницу Confluence."""
        self._confluence_service.upload_attachment(
            panel=panel,
            page_id=page_id,
            file_path=self._panel_file_path(panel.panel_id, panel.panel_name),
        )

    def _upload_panels(self, panels, page_id: str) -> None:
        """Загружает все PNG-файлы панелей как вложения на страницу Confluence."""
        if not self._config.confluence.async_enabled or len(panels) <= 1:
            for panel in panels:
                self._upload_single_panel(panel, page_id)
            return

        max_workers = self._get_max_workers()
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [
                executor.submit(self._upload_single_panel, panel, page_id)
                for panel in panels
            ]

            for future in as_completed(futures):
                future.result()

    def create_report(
        self,
        from_time: str,
        to_time: str,
        dashboard: str,
        parent_id: str,
        title: str,
    ) -> None:
        """
        Создаёт новый отчёт: скачивает панели и публикует страницу в Confluence.

        Args:
            from_time: Начало временного диапазона графиков.
            to_time: Конец временного диапазона графиков.
            dashboard: Имя дашборда из конфигурации.
            parent_id: Идентификатор родительской страницы в Confluence.
            title: Заголовок создаваемой страницы.
        """
        dashboard_obj = self._get_dashboard(dashboard)

        self._grafana_service.download_grafana_panel(
            dashboard=dashboard_obj,
            from_time=from_time,
            to_time=to_time,
        )

        html_doc = self._confluence_service.build_html_page(dashboard_obj.panels)
        new_page = self._confluence_service.create_page_with_body(
            html=html_doc,
            title=title,
            parent_id=parent_id,
        )

        new_page_id = new_page.get("id")
        self._upload_panels(dashboard_obj.panels, new_page_id)

    def update_report(
        self,
        from_time: str,
        to_time: str,
        dashboard: str,
        page_id: str,
        title: str,
    ) -> None:
        """
        Обновляет существующий отчёт: перескачивает панели и обновляет страницу.

        Args:
            from_time: Начало временного диапазона графиков.
            to_time: Конец временного диапазона графиков.
            dashboard: Имя дашборда из конфигурации.
            page_id: Идентификатор существующей страницы в Confluence.
            title: Новый заголовок страницы.
        """
        dashboard_obj = self._get_dashboard(dashboard)

        self._grafana_service.download_grafana_panel(
            dashboard=dashboard_obj,
            from_time=from_time,
            to_time=to_time,
        )

        html_doc = self._confluence_service.build_html_page(dashboard_obj.panels)
        self._upload_panels(dashboard_obj.panels, page_id)

        self._confluence_service.update_page(
            page_id=page_id,
            title=title,
            html=html_doc,
        )

    def reload_dashboards(self) -> None:
        """Перезагружает список дашбордов из JSON-файла конфигурации."""
        self._dashboards = self._grafana_service.load_dashboards()

    def get_dashboards(self) -> dict[str, Dashboard]:
        """
        Возвращает текущий кэш загруженных дашбордов.

        Returns:
            Словарь {имя_дашборда: Dashboard}.
        """
        return self._dashboards
