# services.confluence_service.py
from pathlib import Path

from atlassian import Confluence
import logging

from configuration.app_config import ConfluenceConfig
from configuration.credentials import get_confluence_token, get_confluence_username
from services.grafana_service import Panel


class ConfluenceService:

    def __init__(self, config: ConfluenceConfig):
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

    def page_exists(self, page_id: str,) -> bool:
        """
        Возвращает True если страница существует

        :param page_id:
        :return:
        """

        page = self._client.get_page_by_id(
            page_id=page_id
        )

        return page is not None

    def upload_attachment(self, page_id: str, panel: Panel, file_path: Path) -> dict:
        """
        Загружает файл на страницу Confluence.

        Возвращает информацию о вложении.
        """

        if not file_path.is_file():
            raise FileNotFoundError(
                f"Файл не найден: {file_path}"
            )

        return self._client.attach_file(
            name=f"panel_{panel.panel_id}_{panel.panel_name}.png",
            filename=str(file_path),
            page_id=page_id,
        )

    def build_html_page(self, panels: list[Panel]) -> str:
        start = (
            '<ac:structured-macro ac:name="expand" ac:schema-version="1" '
            f'ac:macro-id="{self._macro_id}">'
            '<ac:parameter ac:name="title">Графики</ac:parameter>'
            '<ac:rich-text-body>'
        )
        end = '</ac:rich-text-body></ac:structured-macro>'
        table_chunk = []
        for panel in panels:
            table_chunk.append(f"<h2>{panel.panel_name}</h2><p><ac:image ac:width\"1000\"><ri:attachment ri:filename\"panel_{panel.panel_id}_{panel.panel_name}.png\" /></ac:image></p>")

        result = start + "".join(table_chunk) + end

        with open("data/report_template.html", "r") as file:
            template = file.read()

        return template.replace("{GRAPHICS_GRAFANA_REPLACE_IT}", result)

    def create_page_with_body(self, html: str, title: str, parent_id: str) -> None:
        self._client.create_page(
            space=self._space_key,
            body=html,
            parent_id=parent_id,
            title=title,
        )

    def update_page(self, html: str, page_id: str, title: str) -> None:
        self._client.update_existing_page(
            page_id=page_id,
            title=title,
            body=html)