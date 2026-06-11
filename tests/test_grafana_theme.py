import unittest
from dataclasses import replace
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.parse import parse_qs, urlparse

from configuration.app_config import default_config, load_config, save_config
from services.grafana_service import (
    GRAFANA_THEME_DARK,
    GRAFANA_THEME_LIGHT,
    Dashboard,
    GrafanaService,
)


class GrafanaThemeTests(unittest.TestCase):
    def _render_theme_for(self, dark_chart_theme: bool) -> str:
        config = replace(
            default_config().grafana,
            dark_chart_theme=dark_chart_theme,
            timezone="Etc/GMT+3",
        )
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
        self.assertEqual(self._render_theme_for(True), GRAFANA_THEME_DARK)

    def test_render_url_uses_light_theme_by_default(self) -> None:
        self.assertEqual(self._render_theme_for(False), GRAFANA_THEME_LIGHT)

    def test_render_url_encodes_query_parameters(self) -> None:
        config = replace(default_config().grafana, timezone="Etc/GMT+3")
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

        self.assertIn("tz=Etc%2FGMT%2B3", render_url)
        self.assertEqual(parse_qs(urlparse(render_url).query)["tz"], ["Etc/GMT+3"])

    def test_load_config_defaults_theme_to_light_for_legacy_ini(self) -> None:
        with TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "config.ini"
            config_path.write_text(
                """
[grafana]
width =
height =
timeout = 30
timezone = Europe/Moscow
org_id = 1
tmp_dir = tmp/grafana_panels
dashboards_path = data/dashboards.json
async = false
max_workers = 4

[confluence]
url =
space_key =
ssl_certificate_path =
macro_id = macro
async = false
max_workers = 4

[general]
report_html_template_path =
qss_path = data/style.qss
""".lstrip(),
                encoding="utf-8",
            )

            config = load_config(config_path)

        self.assertFalse(config.grafana.dark_chart_theme)

    def test_save_config_round_trips_dark_theme(self) -> None:
        with TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "config.ini"
            default = default_config()
            config = replace(
                default,
                grafana=replace(default.grafana, dark_chart_theme=True),
            )

            save_config(config, config_path)
            reloaded = load_config(config_path)

        self.assertTrue(reloaded.grafana.dark_chart_theme)


if __name__ == "__main__":
    unittest.main()
