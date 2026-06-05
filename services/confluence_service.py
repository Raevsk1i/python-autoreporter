"""Сервис для публикации отчётов и вложений в Confluence."""

import logging
from pathlib import Path

from atlassian import Confluence

from configuration.app_config import ConfluenceConfig
from configuration.credentials import get_confluence_token, get_confluence_username
from services.grafana_service import Panel

REPORT_TEMPLATE_PATH = Path("data/report_template.html")
GRAPHICS_PLACEHOLDER = "{GRAPHICS_GRAFANA_REPLACE_IT}"


class ConfluenceService:
    """Клиент для создания и обновления страниц Confluence."""

    def __init__(self, config: ConfluenceConfig) -> None:
        """
        Инициализирует подключение к Confluence API.

        Args:
            config: Секция настроек Confluence из AppConfig.
        """
        self._config = config
        self._logger = logging.getLogger("ConfluenceService")
        self._url = config.url
        self._space_key = config.space_key
        self._macro_id = config.macro_id
        self._ssl_certificate_path = config.ssl_certificate_path
        self._client = Confluence(
            url=self._url,
            username=get_confluence_username(),
            token=get_confluence_token(),
            verify_ssl=self._ssl_certificate_path,
        )

    def page_exists(self, page_id: str) -> bool:
        """
        Проверяет существование страницы по идентификатору.

        Args:
            page_id: Идентификатор страницы в Confluence.

        Returns:
            True, если страница найдена, иначе False.
        """
        page = self._client.get_page_by_id(page_id=page_id)
        return page is not None

    def upload_attachment(
        self,
        page_id: str,
        panel: Panel,
        file_path: Path,
    ) -> dict:
        """
        Загружает PNG-файл панели как вложение на страницу Confluence.

        Args:
            page_id: Идентификатор целевой страницы.
            panel: Панель, для которой формируется имя вложения.
            file_path: Путь к локальному PNG-файлу.

        Returns:
            Метаданные загруженного вложения от Confluence API.

        Raises:
            FileNotFoundError: Если локальный файл не существует.
        """
        if not file_path.is_file():
            raise FileNotFoundError(f"Файл не найден: {file_path}")

        attachment_name = f"panel_{panel.panel_id}_{panel.panel_name}.png"

        return self._client.attach_file(
            name=attachment_name,
            filename=str(file_path),
            page_id=page_id,
        )

    def _build_panel_html(self, panel: Panel) -> str:
        """Формирует HTML-блок для одной панели с изображением-вложением."""
        attachment_name = f"panel_{panel.panel_id}_{panel.panel_name}.png"

        return (
            f"<h2>{panel.panel_name}</h2>"
            f'<p><ac:image ac:width"1000">'
            f'<ri:attachment ri:filename"{attachment_name}" />'
            f"</ac:image></p>"
        )

    def _build_graphics_macro(self, panels: list[Panel]) -> str:
        """Собирает содержимое макроса «expand» с графиками всех панелей."""
        macro_start = (
            '<ac:structured-macro ac:name="expand" ac:schema-version="1" '
            f'ac:macro-id="{self._macro_id}">'
            '<ac:parameter ac:name="title">Графики</ac:parameter>'
            "<ac:rich-text-body>"
        )
        macro_end = "</ac:rich-text-body></ac:structured-macro>"

        panels_html = "".join(self._build_panel_html(panel) for panel in panels)
        return macro_start + panels_html + macro_end

    def build_html_page(self, panels: list[Panel]) -> str:
        """
        Собирает полный HTML-документ страницы отчёта из шаблона.

        Args:
            panels: Список панелей, которые будут вставлены в шаблон.

        Returns:
            Готовый HTML для публикации в Confluence.
        """
        graphics_html = self._build_graphics_macro(panels)

        with open(REPORT_TEMPLATE_PATH, encoding="utf-8") as file:
            template = file.read()

        return template.replace(GRAPHICS_PLACEHOLDER, graphics_html)

    def create_page_with_body(
        self,
        html: str,
        title: str,
        parent_id: str,
    ) -> dict:
        """
        Создаёт новую страницу Confluence с заданным содержимым.

        Args:
            html: HTML-тело страницы.
            title: Заголовок страницы.
            parent_id: Идентификатор родительской страницы.

        Returns:
            Ответ Confluence API с данными созданной страницы.
        """
        return self._client.create_page(
            space=self._space_key,
            body=html,
            parent_id=parent_id,
            title=title,
        )

    def update_page(self, html: str, page_id: str, title: str) -> None:
        """
        Обновляет существующую страницу Confluence.

        Args:
            html: Новое HTML-тело страницы.
            page_id: Идентификатор обновляемой страницы.
            title: Новый заголовок страницы.
        """
        self._client.update_existing_page(
            page_id=page_id,
            title=title,
            body=html,
        )
