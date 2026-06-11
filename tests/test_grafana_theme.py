from dataclasses import replace
from urllib.parse import parse_qs, urlparse
import unittest

from configuration.app_config import default_config
from services.grafana_service import Dashboard, GrafanaService


class GrafanaThemeTests(unittest.TestCase):
    def _render_theme_for(self, dark_chart_theme: bool) -> str:
        config = replace(default_config().grafana, dark_chart_theme=dark_chart_theme)
        service = GrafanaService(config)
        dashboard = Dashboard(
            name="demo",
            grafana_url="https://grafana.example.com/",
            dashboard_uid="uid",
            dashboard_slug="slug",
            panels=[],
        )

        render_url = service._build_render_url(
            dashboard=dashboard,
            panel_id="1",
            from_time_ms=1000,
            to_time_ms=2000,
        )

        query = parse_qs(urlparse(render_url).query)
        return query["theme"][0]

    def test_render_url_uses_dark_theme_when_enabled(self) -> None:
        self.assertEqual(self._render_theme_for(True), "dark")

    def test_render_url_uses_light_theme_by_default(self) -> None:
        self.assertEqual(self._render_theme_for(False), "light")


if __name__ == "__main__":
    unittest.main()
