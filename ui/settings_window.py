"""Окно настроек конфигурации и учётных данных."""

from pathlib import Path

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

import configuration.credentials as credentials
from configuration.app_config import (
    AppConfig,
    ConfluenceConfig,
    GeneralConfig,
    GrafanaConfig,
    get_config_path,
    load_config,
    save_config,
    save_config_path,
)
from ui.widgets import (
    make_button_row,
    make_form_label,
    make_hint_label,
    make_scrollable,
    make_section_card,
    make_section_title,
)


class SettingsWindow(QDialog):
    """Редактирование config.ini и учётных данных в keyring."""

    config_saved = Signal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Настройки")
        self.setMinimumSize(720, 560)
        self.resize(780, 620)

        self._config_path = get_config_path()
        self._config = load_config(self._config_path)

        self._build_ui()
        self._load_values()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)

        header = make_section_title("Конфигурация приложения")
        root.addWidget(header)
        root.addWidget(
            make_hint_label(
                f"Файл конфигурации: {self._config_path}. "
                "Изменения сохраняются в этот файл, учётные данные — в системное хранилище."
            )
        )

        tabs = QTabWidget()
        tabs.addTab(self._build_grafana_tab(), "Grafana")
        tabs.addTab(self._build_confluence_tab(), "Confluence")
        tabs.addTab(self._build_general_tab(), "Общие")
        tabs.addTab(self._build_credentials_tab(), "Учётные данные")
        root.addWidget(tabs, stretch=1)

        self._config_path_label = QLabel(f"Путь: {self._config_path}")
        self._config_path_label.setObjectName("hintLabel")
        root.addWidget(self._config_path_label)

        browse_button = QPushButton("Выбрать другой config.ini")
        browse_button.setObjectName("ghostButton")
        browse_button.clicked.connect(self._browse_config_path)

        save_button = QPushButton("Сохранить")
        save_button.setObjectName("primaryButton")
        save_button.clicked.connect(self._save_settings)

        close_button = QPushButton("Закрыть")
        close_button.clicked.connect(self.close)

        button_row = make_button_row(browse_button, close_button, save_button)
        root.addLayout(button_row)

    def _build_grafana_tab(self) -> QWidget:
        content = QWidget()
        layout = QVBoxLayout(content)

        card, card_layout = make_section_card("Параметры Grafana")
        form = QFormLayout()
        form.setSpacing(12)
        card_layout.addLayout(form)

        self._grafana_fields = {
            "url": QLineEdit(),
            "width": QLineEdit(),
            "height": QLineEdit(),
            "timeout": QLineEdit(),
            "timezone": QLineEdit(),
            "org_id": QLineEdit(),
            "tmp_dir": QLineEdit(),
            "dashboards_path": QLineEdit(),
            "max_workers": QLineEdit(),
        }

        labels = {
            "url": "URL",
            "width": "Ширина панели (px)",
            "height": "Высота панели (px)",
            "timeout": "Таймаут (сек)",
            "timezone": "Часовой пояс",
            "org_id": "Org ID",
            "tmp_dir": "Временная папка",
            "dashboards_path": "Путь к dashboards.json",
            "max_workers": "Макс. потоков",
        }

        for key, label_text in labels.items():
            form.addRow(make_form_label(label_text), self._grafana_fields[key])

        self._grafana_async_checkbox = QCheckBox("Асинхронно (многопоточное скачивание графиков)")
        form.addRow(make_form_label("Многопоточность"), self._grafana_async_checkbox)

        layout.addWidget(card)
        layout.addStretch()
        return make_scrollable(content)

    def _build_confluence_tab(self) -> QWidget:
        content = QWidget()
        layout = QVBoxLayout(content)

        card, card_layout = make_section_card("Параметры Confluence")
        form = QFormLayout()
        form.setSpacing(12)
        card_layout.addLayout(form)

        self._confluence_fields = {
            "url": QLineEdit(),
            "space_key": QLineEdit(),
            "ssl_certificate_path": QLineEdit(),
            "macro_id": QLineEdit(),
            "max_workers": QLineEdit(),
        }

        labels = {
            "url": "URL",
            "space_key": "Ключ пространства",
            "ssl_certificate_path": "Путь к SSL-сертификату",
            "macro_id": "ID макроса expand",
            "max_workers": "Макс. потоков",
        }

        for key, label_text in labels.items():
            form.addRow(make_form_label(label_text), self._confluence_fields[key])

        self._confluence_async_checkbox = QCheckBox("Асинхронно (многопоточная загрузка вложений)")
        form.addRow(make_form_label("Многопоточность"), self._confluence_async_checkbox)

        layout.addWidget(card)
        layout.addStretch()
        return make_scrollable(content)

    def _build_general_tab(self) -> QWidget:
        content = QWidget()
        layout = QVBoxLayout(content)

        card, card_layout = make_section_card("Общие параметры")
        form = QFormLayout()
        form.setSpacing(12)
        card_layout.addLayout(form)

        self._general_fields = {
            "report_html_template_path": QLineEdit(),
            "qss_path": QLineEdit(),
        }

        form.addRow(make_form_label("Путь к HTML-шаблону"), self._general_fields["report_html_template_path"])
        form.addRow(make_form_label("Путь к QSS-стилям"), self._general_fields["qss_path"])

        layout.addWidget(card)
        layout.addStretch()
        return make_scrollable(content)

    def _build_credentials_tab(self) -> QWidget:
        content = QWidget()
        layout = QVBoxLayout(content)

        confluence_card, confluence_layout = make_section_card("Confluence")
        confluence_form = QFormLayout()
        confluence_form.setSpacing(12)
        confluence_layout.addLayout(confluence_form)
        self._confluence_username = QLineEdit()
        self._confluence_token = QLineEdit()
        self._confluence_token.setEchoMode(QLineEdit.EchoMode.Password)
        confluence_form.addRow(make_form_label("Имя пользователя"), self._confluence_username)
        confluence_form.addRow(make_form_label("API-токен"), self._confluence_token)

        grafana_card, grafana_layout = make_section_card("Grafana")
        grafana_form = QFormLayout()
        grafana_form.setSpacing(12)
        grafana_layout.addLayout(grafana_form)
        self._grafana_username = QLineEdit()
        self._grafana_password = QLineEdit()
        self._grafana_password.setEchoMode(QLineEdit.EchoMode.Password)
        self._grafana_token = QLineEdit()
        self._grafana_token.setEchoMode(QLineEdit.EchoMode.Password)
        grafana_form.addRow(make_form_label("Имя пользователя"), self._grafana_username)
        grafana_form.addRow(make_form_label("Пароль"), self._grafana_password)
        grafana_form.addRow(make_form_label("API-токен (приоритетнее пароля)"), self._grafana_token)

        layout.addWidget(confluence_card)
        layout.addWidget(grafana_card)
        layout.addWidget(
            make_hint_label(
                "Если задан API-токен Grafana, Basic Auth не используется. "
                "Пустые поля при сохранении не перезаписывают существующие значения."
            )
        )
        layout.addStretch()
        return make_scrollable(content)

    def _load_values(self) -> None:
        grafana = self._config.grafana
        confluence = self._config.confluence
        general = self._config.general

        grafana_values = {
            "url": grafana.url,
            "width": grafana.width,
            "height": grafana.height,
            "timeout": grafana.timeout,
            "timezone": grafana.timezone,
            "org_id": grafana.org_id,
            "tmp_dir": grafana.tmp_dir,
            "dashboards_path": grafana.dashboards_path,
            "max_workers": grafana.max_workers,
        }

        for key, value in grafana_values.items():
            self._grafana_fields[key].setText(value)
        self._grafana_async_checkbox.setChecked(grafana.async_enabled)

        confluence_values = {
            "url": confluence.url,
            "space_key": confluence.space_key,
            "ssl_certificate_path": confluence.ssl_certificate_path,
            "macro_id": confluence.macro_id,
            "max_workers": confluence.max_workers,
        }

        for key, value in confluence_values.items():
            self._confluence_fields[key].setText(value)
        self._confluence_async_checkbox.setChecked(confluence.async_enabled)

        self._general_fields["report_html_template_path"].setText(
            general.report_html_template_path
        )
        self._general_fields["qss_path"].setText(general.qss_path)

        self._confluence_username.setText(credentials.get_confluence_username() or "")
        self._confluence_token.setText(credentials.get_confluence_token() or "")
        self._grafana_username.setText(credentials.get_grafana_username() or "")
        self._grafana_password.setText(credentials.get_grafana_password() or "")
        self._grafana_token.setText(credentials.get_grafana_token() or "")

    def _browse_config_path(self) -> None:
        selected, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите config.ini",
            str(self._config_path.parent),
            "INI files (*.ini);;All files (*)",
        )

        if not selected:
            return

        new_path = Path(selected)

        try:
            self._config = load_config(new_path)
        except (FileNotFoundError, RuntimeError) as error:
            QMessageBox.critical(self, "Ошибка", str(error))
            return

        save_config_path(new_path)
        self._config_path = new_path
        self._config_path_label.setText(f"Путь: {self._config_path}")
        self._load_values()

    def _save_settings(self) -> None:
        try:
            updated_config = AppConfig(
                grafana=GrafanaConfig(
                    **{key: field.text().strip() for key, field in self._grafana_fields.items()},
                    async_enabled=self._grafana_async_checkbox.isChecked(),
                ),
                confluence=ConfluenceConfig(
                    **{key: field.text().strip() for key, field in self._confluence_fields.items()},
                    async_enabled=self._confluence_async_checkbox.isChecked(),
                ),
                general=GeneralConfig(
                    report_html_template_path=self._general_fields["report_html_template_path"].text().strip(),
                    qss_path=self._general_fields["qss_path"].text().strip(),
                ),
            )
            save_config(updated_config, self._config_path)
            self._config = updated_config

            confluence_username = self._confluence_username.text().strip()
            confluence_token = self._confluence_token.text().strip()
            if confluence_username and confluence_token:
                credentials.set_confluence_auth(confluence_username, confluence_token)

            grafana_username = self._grafana_username.text().strip()
            grafana_password = self._grafana_password.text().strip()
            if grafana_username and grafana_password:
                credentials.set_grafana_basicauth(grafana_username, grafana_password)

            grafana_token = self._grafana_token.text().strip()
            if grafana_token:
                credentials.set_grafana_token(grafana_token)

            self.config_saved.emit()
            QMessageBox.information(self, "Сохранено", "Настройки успешно сохранены.")
        except Exception as error:
            QMessageBox.critical(self, "Ошибка сохранения", str(error))

    def get_config(self) -> AppConfig:
        """Возвращает текущую конфигурацию окна."""
        return self._config
