# services.confluence_service.py
from pathlib import Path

from atlassian import Confluence
import logging

from configuration.app_config import ConfluenceConfig
from configuration.credentials import get_confluence_token, get_confluence_username
from services.grafana_service import Panel
from utils.helper import panel_filename

_DEFAULT_TEMPLATE_PATH = Path("data/report_template.html")


class ConfluenceService:

    def __init__(self, config: ConfluenceConfig, template_path: str | Path | None = None):
        self._config = config
        self._logger = logging.getLogger("ConfluenceService")
        self._url = config.url
        self._space_key = config.space_key
        self._macro_id = config.macro_id
        self._ssl_certificate_path = config.ssl_certificate_path
        self._template_path = Path(template_path) if template_path else _DEFAULT_TEMPLATE_PATH
        self._template_cache: str | None = None
        self._client = Confluence(
            url=self._url,
            username=get_confluence_username(),
            token=get_confluence_token(),
            verify_ssl=self._ssl_certificate_path,
        )

    def _load_template(self) -> str:
        if self._template_cache is None:
            self._template_cache = self._template_path.read_text(encoding="utf-8")
        return self._template_cache

    def page_exists(self, page_id: str,) -> bool:
        """
        Возвращает True если страница существует
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
            name=panel_filename(panel.panel_id, panel.panel_name),
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

        graphics = "".join(
            f'<h2>{panel.panel_name}</h2>'
            f'<p><ac:image ac:width="1000">'
            f'<ri:attachment ri:filename="{panel_filename(panel.panel_id, panel.panel_name)}" />'
            f'</ac:image></p>'
            for panel in panels
        )

        return self._load_template().replace("{GRAPHICS_GRAFANA_REPLACE_IT}", start + graphics + end)

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
