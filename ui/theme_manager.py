"""Управление светлой и тёмной темами приложения."""

from enum import Enum

from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QApplication


class Theme(Enum):
    """Доступные темы оформления."""

    LIGHT = "light"
    DARK = "dark"


LIGHT_QSS = """
* {
    font-family: "Segoe UI", "SF Pro Text", "Helvetica Neue", Arial, sans-serif;
    font-size: 13px;
}

QMainWindow, QDialog {
    background-color: #f4f6f9;
}

QWidget {
    color: #1e293b;
}

QGroupBox {
    background-color: #ffffff;
    border: 1px solid #d8dee9;
    border-radius: 10px;
    margin-top: 14px;
    padding: 16px 12px 12px 12px;
    font-weight: 600;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 12px;
    padding: 0 6px;
    color: #334155;
}

QLabel {
    color: #334155;
    background: transparent;
}

QLabel#sectionTitle {
    font-size: 15px;
    font-weight: 700;
    color: #0f172a;
}

QLabel#hintLabel {
    color: #64748b;
    font-size: 12px;
}

QLineEdit, QComboBox, QSpinBox, QDateTimeEdit, QTextEdit, QPlainTextEdit {
    background-color: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 8px;
    padding: 8px 10px;
    selection-background-color: #93c5fd;
    selection-color: #0f172a;
}

QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDateTimeEdit:focus,
QTextEdit:focus, QPlainTextEdit:focus {
    border: 1px solid #3b82f6;
}

QComboBox::drop-down {
    border: none;
    width: 24px;
}

QComboBox QAbstractItemView {
    background-color: #ffffff;
    border: 1px solid #cbd5e1;
    selection-background-color: #dbeafe;
    selection-color: #1e293b;
}

QPushButton {
    background-color: #e2e8f0;
    color: #1e293b;
    border: 1px solid #cbd5e1;
    border-radius: 8px;
    padding: 8px 16px;
    font-weight: 600;
}

QPushButton:hover {
    background-color: #cbd5e1;
}

QPushButton:pressed {
    background-color: #94a3b8;
}

QPushButton#primaryButton {
    background-color: #2563eb;
    color: #ffffff;
    border: 1px solid #1d4ed8;
}

QPushButton#primaryButton:hover {
    background-color: #1d4ed8;
}

QPushButton#primaryButton:pressed {
    background-color: #1e40af;
}

QPushButton#dangerButton {
    background-color: #fef2f2;
    color: #b91c1c;
    border: 1px solid #fecaca;
}

QPushButton#dangerButton:hover {
    background-color: #fee2e2;
}

QPushButton#ghostButton {
    background-color: transparent;
    border: 1px solid #cbd5e1;
}

QRadioButton, QCheckBox {
    spacing: 8px;
}

QRadioButton::indicator, QCheckBox::indicator {
    width: 16px;
    height: 16px;
}

QScrollArea {
    border: none;
    background: transparent;
}

QScrollBar:vertical {
    background: #eef2f7;
    width: 10px;
    margin: 0;
    border-radius: 5px;
}

QScrollBar::handle:vertical {
    background: #cbd5e1;
    min-height: 24px;
    border-radius: 5px;
}

QScrollBar::handle:vertical:hover {
    background: #94a3b8;
}

QListWidget {
    background-color: #ffffff;
    border: 1px solid #d8dee9;
    border-radius: 8px;
    padding: 4px;
}

QListWidget::item {
    padding: 8px 10px;
    border-radius: 6px;
}

QListWidget::item:selected {
    background-color: #dbeafe;
    color: #1e3a8a;
}

QTabWidget::pane {
    border: 1px solid #d8dee9;
    border-radius: 8px;
    background: #ffffff;
    top: -1px;
}

QTabBar::tab {
    background: #e2e8f0;
    color: #475569;
    padding: 8px 16px;
    margin-right: 4px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
}

QTabBar::tab:selected {
    background: #ffffff;
    color: #1e293b;
    font-weight: 600;
}

QStatusBar {
    background: #ffffff;
    color: #64748b;
    border-top: 1px solid #d8dee9;
}

QMenuBar {
    background: #ffffff;
    border-bottom: 1px solid #d8dee9;
}

QMenuBar::item:selected {
    background: #e2e8f0;
}

QMenu {
    background: #ffffff;
    border: 1px solid #d8dee9;
}

QMenu::item:selected {
    background: #dbeafe;
}

QToolBar {
    background: #ffffff;
    border-bottom: 1px solid #d8dee9;
    spacing: 6px;
    padding: 4px;
}

QProgressBar {
    border: 1px solid #cbd5e1;
    border-radius: 6px;
    background: #f1f5f9;
    text-align: center;
    color: #334155;
}

QProgressBar::chunk {
    background: #3b82f6;
    border-radius: 5px;
}
"""

DARK_QSS = """
* {
    font-family: "Segoe UI", "SF Pro Text", "Helvetica Neue", Arial, sans-serif;
    font-size: 13px;
}

QMainWindow, QDialog {
    background-color: #14141f;
}

QWidget {
    color: #e2e8f0;
}

QGroupBox {
    background-color: #1c1c2b;
    border: 1px solid #2d2d44;
    border-radius: 10px;
    margin-top: 14px;
    padding: 16px 12px 12px 12px;
    font-weight: 600;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 12px;
    padding: 0 6px;
    color: #c4b5fd;
}

QLabel {
    color: #cbd5e1;
    background: transparent;
}

QLabel#sectionTitle {
    font-size: 15px;
    font-weight: 700;
    color: #f5f3ff;
}

QLabel#hintLabel {
    color: #94a3b8;
    font-size: 12px;
}

QLineEdit, QComboBox, QSpinBox, QDateTimeEdit, QTextEdit, QPlainTextEdit {
    background-color: #232336;
    border: 1px solid #3f3f5c;
    border-radius: 8px;
    padding: 8px 10px;
    color: #f1f5f9;
    selection-background-color: #7c3aed;
    selection-color: #ffffff;
}

QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDateTimeEdit:focus,
QTextEdit:focus, QPlainTextEdit:focus {
    border: 1px solid #a855f7;
}

QComboBox::drop-down {
    border: none;
    width: 24px;
}

QComboBox QAbstractItemView {
    background-color: #232336;
    border: 1px solid #5b21b6;
    selection-background-color: #6d28d9;
    selection-color: #ffffff;
}

QPushButton {
    background-color: #2a2a3d;
    color: #e2e8f0;
    border: 1px solid #3f3f5c;
    border-radius: 8px;
    padding: 8px 16px;
    font-weight: 600;
}

QPushButton:hover {
    background-color: #35354d;
    border-color: #7c3aed;
}

QPushButton:pressed {
    background-color: #1f1f30;
}

QPushButton#primaryButton {
    background-color: #7c3aed;
    color: #ffffff;
    border: 1px solid #a855f7;
}

QPushButton#primaryButton:hover {
    background-color: #8b5cf6;
    border-color: #c084fc;
}

QPushButton#primaryButton:pressed {
    background-color: #6d28d9;
}

QPushButton#dangerButton {
    background-color: #3b1f2b;
    color: #fca5a5;
    border: 1px solid #7f1d1d;
}

QPushButton#dangerButton:hover {
    background-color: #4c1d2a;
    border-color: #ef4444;
}

QPushButton#ghostButton {
    background-color: transparent;
    border: 1px solid #4c4c6a;
}

QRadioButton, QCheckBox {
    spacing: 8px;
}

QRadioButton::indicator, QCheckBox::indicator {
    width: 16px;
    height: 16px;
}

QScrollArea {
    border: none;
    background: transparent;
}

QScrollBar:vertical {
    background: #1c1c2b;
    width: 10px;
    margin: 0;
    border-radius: 5px;
}

QScrollBar::handle:vertical {
    background: #5b21b6;
    min-height: 24px;
    border-radius: 5px;
}

QScrollBar::handle:vertical:hover {
    background: #7c3aed;
}

QListWidget {
    background-color: #1c1c2b;
    border: 1px solid #2d2d44;
    border-radius: 8px;
    padding: 4px;
}

QListWidget::item {
    padding: 8px 10px;
    border-radius: 6px;
}

QListWidget::item:selected {
    background-color: #4c1d95;
    color: #f5f3ff;
}

QTabWidget::pane {
    border: 1px solid #2d2d44;
    border-radius: 8px;
    background: #1c1c2b;
    top: -1px;
}

QTabBar::tab {
    background: #232336;
    color: #94a3b8;
    padding: 8px 16px;
    margin-right: 4px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
}

QTabBar::tab:selected {
    background: #1c1c2b;
    color: #e9d5ff;
    font-weight: 600;
    border-bottom: 2px solid #a855f7;
}

QStatusBar {
    background: #1c1c2b;
    color: #94a3b8;
    border-top: 1px solid #2d2d44;
}

QMenuBar {
    background: #1c1c2b;
    border-bottom: 1px solid #2d2d44;
    color: #e2e8f0;
}

QMenuBar::item:selected {
    background: #2a2a3d;
}

QMenu {
    background: #1c1c2b;
    border: 1px solid #3f3f5c;
    color: #e2e8f0;
}

QMenu::item:selected {
    background: #4c1d95;
}

QToolBar {
    background: #1c1c2b;
    border-bottom: 1px solid #2d2d44;
    spacing: 6px;
    padding: 4px;
}

QProgressBar {
    border: 1px solid #3f3f5c;
    border-radius: 6px;
    background: #232336;
    text-align: center;
    color: #e2e8f0;
}

QProgressBar::chunk {
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:0,
        stop:0 #7c3aed, stop:1 #a855f7
    );
    border-radius: 5px;
}
"""


class ThemeManager:
    """Применяет и сохраняет выбранную тему оформления."""

    SETTINGS_KEY = "ui/theme"

    def __init__(self, app: QApplication) -> None:
        self._app = app
        self._settings = QSettings("python-autoreporter", "python-autoreporter")
        stored = self._settings.value(self.SETTINGS_KEY, Theme.DARK.value)
        self._theme = Theme(stored) if stored in Theme._value2member_map_ else Theme.DARK

    @property
    def theme(self) -> Theme:
        """Текущая активная тема."""
        return self._theme

    def apply(self, theme: Theme | None = None) -> None:
        """Применяет тему ко всему приложению."""
        if theme is not None:
            self._theme = theme

        qss = LIGHT_QSS if self._theme == Theme.LIGHT else DARK_QSS
        self._app.setStyleSheet(qss)
        self._settings.setValue(self.SETTINGS_KEY, self._theme.value)

    def toggle(self) -> Theme:
        """Переключает тему и возвращает новую."""
        new_theme = Theme.LIGHT if self._theme == Theme.DARK else Theme.DARK
        self.apply(new_theme)
        return new_theme
