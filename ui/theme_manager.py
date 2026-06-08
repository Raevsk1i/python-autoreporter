"""Управление светлой и тёмной темами приложения."""

import re
from enum import Enum
from pathlib import Path

from PySide6.QtCore import QSettings
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication

DEFAULT_QSS_PATH = Path("data/style.qss")
THEME_MARKER = re.compile(r"/\*\s*===\s*THEME:(\w+)\s*===\s*\*/")


class Theme(Enum):
    """Доступные темы оформления."""

    LIGHT = "light"
    DARK = "dark"


def _parse_theme_sections(qss_text: str) -> dict[str, str]:
    """Разбирает QSS-файл на секции по маркерам тем."""
    sections: dict[str, str] = {}
    current_theme: str | None = None
    buffer: list[str] = []

    for line in qss_text.splitlines():
        marker = THEME_MARKER.match(line.strip())
        if marker:
            if current_theme is not None:
                sections[current_theme] = "\n".join(buffer).strip()
            current_theme = marker.group(1).lower()
            buffer = []
            continue

        if current_theme is not None:
            buffer.append(line)

    if current_theme is not None:
        sections[current_theme] = "\n".join(buffer).strip()

    return sections


def load_theme_qss(theme: Theme, qss_path: Path | str = DEFAULT_QSS_PATH) -> str:
    """
    Загружает стили указанной темы из QSS-файла.

    Args:
        theme: Тема оформления.
        qss_path: Путь к файлу style.qss с секциями тем.

    Returns:
        Строка QSS для выбранной темы.

    Raises:
        FileNotFoundError: Если файл стилей не найден.
        ValueError: Если секция темы отсутствует в файле.
    """
    path = Path(qss_path)

    if not path.is_file():
        raise FileNotFoundError(f"Файл стилей не найден: {path}")

    sections = _parse_theme_sections(path.read_text(encoding="utf-8"))
    theme_key = theme.value

    if theme_key not in sections:
        raise ValueError(f"Секция темы «{theme_key}» не найдена в {path}")

    return sections[theme_key]


class ThemeManager:
    """Применяет и сохраняет выбранную тему оформления."""

    SETTINGS_KEY = "ui/theme"

    def __init__(
        self,
        app: QApplication,
        qss_path: Path | str = DEFAULT_QSS_PATH,
    ) -> None:
        self._app = app
        self._qss_path = Path(qss_path)
        self._settings = QSettings("python-autoreporter", "python-autoreporter")
        stored = self._settings.value(self.SETTINGS_KEY, Theme.LIGHT.value)
        self._theme = Theme(stored) if stored in Theme._value2member_map_ else Theme.LIGHT

    @property
    def theme(self) -> Theme:
        """Текущая активная тема."""
        return self._theme

    @property
    def qss_path(self) -> Path:
        """Путь к файлу стилей."""
        return self._qss_path

    def _apply_font(self) -> None:
        """Задаёт сглаженный системный шрифт."""
        font = QFont()
        font.setFamilies(["Segoe UI Variable", "Segoe UI", "Helvetica Neue", "sans-serif"])
        font.setPointSize(10)
        font.setWeight(QFont.Weight.Normal)
        font.setHintingPreference(QFont.HintingPreference.PreferNoHinting)
        font.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
        self._app.setFont(font)

    def apply(self, theme: Theme | None = None) -> None:
        """Применяет тему ко всему приложению."""
        if theme is not None:
            self._theme = theme

        self._apply_font()
        qss = load_theme_qss(self._theme, self._qss_path)
        self._app.setStyleSheet(qss)
        self._settings.setValue(self.SETTINGS_KEY, self._theme.value)

    def toggle(self) -> Theme:
        """Переключает тему и возвращает новую."""
        new_theme = Theme.LIGHT if self._theme == Theme.DARK else Theme.DARK
        self.apply(new_theme)
        return new_theme

    def reset(self) -> None:
        """Сбрасывает тему оформления к значению по умолчанию."""
        self.apply(Theme.LIGHT)
