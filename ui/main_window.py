"""Главное окно приложения python-autoreporter."""

from datetime import datetime

from PySide6.QtCore import QDateTime, QThreadPool, Qt
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QDateTimeEdit,
    QFormLayout,
    QHBoxLayout,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QProgressBar,
    QPushButton,
    QRadioButton,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)

from configuration.app_config import AppConfig, load_config
from services.report_service import ReportService
from ui.dashboards_window import DashboardsWindow
from ui.settings_window import SettingsWindow
from ui.theme_manager import Theme, ThemeManager
from ui.widgets import (
    make_button_row,
    make_form_label,
    make_hint_label,
    make_scrollable,
    make_section_card,
    make_section_title,
)
from ui.worker import ReportWorker


TIME_FORMAT = "yyyy-MM-dd HH:mm:ss"


class MainWindow(QMainWindow):
    """Основное окно с параметрами отчёта и навигацией по разделам."""

    def __init__(self, theme_manager: ThemeManager) -> None:
        super().__init__()
        self._theme_manager = theme_manager
        self._thread_pool = QThreadPool.globalInstance()
        self._settings_window: SettingsWindow | None = None
        self._dashboards_window: DashboardsWindow | None = None

        self.setWindowTitle("python-autoreporter")
        self.setMinimumSize(760, 680)
        self.resize(860, 760)

        try:
            self._config = load_config()
        except (FileNotFoundError, RuntimeError) as error:
            self._config = None
            QMessageBox.warning(
                self,
                "Конфигурация",
                f"{error}\nОткройте «Настройки» и укажите config.ini.",
            )

        self._report_service: ReportService | None = None
        if self._config is not None:
            self._report_service = ReportService(self._config)

        self._build_ui()
        self._refresh_dashboards()
        self._update_mode_fields()

    def _build_ui(self) -> None:
        central = QWidget()
        central.setObjectName("centralWidget")
        central.setAutoFillBackground(True)
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(20, 20, 20, 20)
        root.setSpacing(14)

        header_row = QHBoxLayout()
        header_row.addWidget(make_section_title("Формирование отчёта"))
        header_row.addStretch()

        self._theme_button = QPushButton()
        self._theme_button.setObjectName("ghostButton")
        self._theme_button.clicked.connect(self._toggle_theme)
        self._update_theme_button_text()
        header_row.addWidget(self._theme_button)
        root.addLayout(header_row)

        root.addWidget(
            make_hint_label(
                "Выберите дашборд, укажите период и создайте или обновите страницу в Confluence."
            )
        )

        scroll_content = QWidget()
        scroll_content.setObjectName("scrollContent")
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(14)

        report_card, report_layout = make_section_card("Параметры отчёта")
        report_form = QFormLayout()
        report_form.setSpacing(12)
        report_form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        report_layout.addLayout(report_form)

        self._dashboard_combo = QComboBox()
        self._dashboard_combo.setPlaceholderText("Выберите дашборд")
        report_form.addRow(make_form_label("Дашборд"), self._dashboard_combo)

        self._from_datetime = QDateTimeEdit()
        self._from_datetime.setDisplayFormat(TIME_FORMAT)
        self._from_datetime.setCalendarPopup(True)
        self._from_datetime.setDateTime(QDateTime.currentDateTime().addDays(-1))
        report_form.addRow(make_form_label("Начало периода"), self._from_datetime)

        self._to_datetime = QDateTimeEdit()
        self._to_datetime.setDisplayFormat(TIME_FORMAT)
        self._to_datetime.setCalendarPopup(True)
        self._to_datetime.setDateTime(QDateTime.currentDateTime())
        report_form.addRow(make_form_label("Конец периода"), self._to_datetime)

        self._title_field = QLineEdit()
        self._title_field.setPlaceholderText("Например: Отчёт по мониторингу")
        report_form.addRow(make_form_label("Заголовок страницы"), self._title_field)

        scroll_layout.addWidget(report_card)

        mode_card, mode_layout = make_section_card("Режим публикации")

        mode_buttons = QHBoxLayout()
        self._create_mode_radio = QRadioButton("Создать новую страницу")
        self._update_mode_radio = QRadioButton("Обновить существующую")
        self._create_mode_radio.setChecked(True)
        self._create_mode_radio.toggled.connect(self._update_mode_fields)
        mode_buttons.addWidget(self._create_mode_radio)
        mode_buttons.addWidget(self._update_mode_radio)
        mode_buttons.addStretch()
        mode_layout.addLayout(mode_buttons)

        target_form = QFormLayout()
        target_form.setSpacing(12)
        self._parent_id_field = QLineEdit()
        self._parent_id_field.setPlaceholderText("ID родительской страницы Confluence")
        self._page_id_field = QLineEdit()
        self._page_id_field.setPlaceholderText("ID существующей страницы Confluence")
        self._parent_id_label = make_form_label("Parent ID")
        self._page_id_label = make_form_label("Page ID")
        target_form.addRow(self._parent_id_label, self._parent_id_field)
        target_form.addRow(self._page_id_label, self._page_id_field)
        mode_layout.addLayout(target_form)

        scroll_layout.addWidget(mode_card)

        actions_card, actions_layout = make_section_card("Действия")

        self._run_button = QPushButton("Создать отчёт")
        self._run_button.setObjectName("primaryButton")
        self._run_button.clicked.connect(self._run_report)

        settings_button = QPushButton("Настройки")
        settings_button.clicked.connect(self._open_settings)

        dashboards_button = QPushButton("Дашборды")
        dashboards_button.clicked.connect(self._open_dashboards)

        reload_button = QPushButton("Обновить список дашбордов")
        reload_button.clicked.connect(self._refresh_dashboards)

        actions_layout.addLayout(
            make_button_row(reload_button, dashboards_button, settings_button, self._run_button)
        )
        scroll_layout.addWidget(actions_card)

        log_card, log_layout = make_section_card("Журнал")
        self._log_view = QPlainTextEdit()
        self._log_view.setReadOnly(True)
        self._log_view.setMinimumHeight(140)
        log_layout.addWidget(self._log_view)
        scroll_layout.addWidget(log_card)

        scroll_layout.addStretch()
        root.addWidget(make_scrollable(scroll_content), stretch=1)

        self._progress_bar = QProgressBar()
        self._progress_bar.setRange(0, 0)
        self._progress_bar.setVisible(False)
        root.addWidget(self._progress_bar)

        self.setStatusBar(QStatusBar())
        self.statusBar().showMessage("Готово")

    def _update_theme_button_text(self) -> None:
        if self._theme_manager.theme == Theme.DARK:
            self._theme_button.setText("Светлая тема")
        else:
            self._theme_button.setText("Тёмная тема")

    def _toggle_theme(self) -> None:
        self._theme_manager.toggle()
        self._update_theme_button_text()

    def _update_mode_fields(self) -> None:
        create_mode = self._create_mode_radio.isChecked()
        self._parent_id_label.setEnabled(create_mode)
        self._parent_id_field.setEnabled(create_mode)
        self._page_id_label.setEnabled(not create_mode)
        self._page_id_field.setEnabled(not create_mode)
        self._run_button.setText("Создать отчёт" if create_mode else "Обновить отчёт")

    def _open_settings(self) -> None:
        if self._settings_window is None:
            self._settings_window = SettingsWindow(self)
            self._settings_window.config_saved.connect(self._on_config_saved)

        self._settings_window.show()
        self._settings_window.raise_()
        self._settings_window.activateWindow()

    def _open_dashboards(self) -> None:
        if self._config is None:
            QMessageBox.warning(self, "Конфигурация", "Сначала настройте config.ini.")
            return

        if self._dashboards_window is None:
            self._dashboards_window = DashboardsWindow(self._config, self)
            self._dashboards_window.dashboards_saved.connect(self._refresh_dashboards)
        else:
            self._dashboards_window.update_config(self._config)

        self._dashboards_window.show()
        self._dashboards_window.raise_()
        self._dashboards_window.activateWindow()

    def _on_config_saved(self) -> None:
        if self._settings_window is None:
            return

        self._config = self._settings_window.get_config()
        self._report_service = ReportService(self._config)
        self._refresh_dashboards()

        if self._dashboards_window is not None:
            self._dashboards_window.update_config(self._config)

        self._append_log("Конфигурация обновлена.")

    def _refresh_dashboards(self) -> None:
        if self._report_service is None:
            self._dashboard_combo.clear()
            return

        self._report_service.reload_dashboards()
        dashboards = sorted(self._report_service.get_dashboards().keys())

        current = self._dashboard_combo.currentText()
        self._dashboard_combo.clear()
        self._dashboard_combo.addItems(dashboards)

        if current in dashboards:
            self._dashboard_combo.setCurrentText(current)

        self.statusBar().showMessage(f"Загружено дашбордов: {len(dashboards)}")

    def _append_log(self, message: str) -> None:
        timestamp = datetime.now().strftime("%H:%M:%S")
        self._log_view.appendPlainText(f"[{timestamp}] {message}")

    def _validate_inputs(self) -> tuple[str, str, str, str, str, str] | None:
        if self._report_service is None:
            QMessageBox.warning(self, "Конфигурация", "Сначала настройте config.ini.")
            return None

        dashboard = self._dashboard_combo.currentText().strip()
        title = self._title_field.text().strip()

        if not dashboard:
            QMessageBox.warning(self, "Проверка", "Выберите дашборд.")
            return None

        if not title:
            QMessageBox.warning(self, "Проверка", "Укажите заголовок страницы.")
            return None

        from_time = self._from_datetime.dateTime().toString(TIME_FORMAT)
        to_time = self._to_datetime.dateTime().toString(TIME_FORMAT)

        if self._from_datetime.dateTime() > self._to_datetime.dateTime():
            QMessageBox.warning(self, "Проверка", "Начало периода должно быть раньше конца.")
            return None

        if self._create_mode_radio.isChecked():
            target_id = self._parent_id_field.text().strip()
            if not target_id:
                QMessageBox.warning(self, "Проверка", "Укажите Parent ID.")
                return None
            action = "create"
        else:
            target_id = self._page_id_field.text().strip()
            if not target_id:
                QMessageBox.warning(self, "Проверка", "Укажите Page ID.")
                return None
            action = "update"

        return action, from_time, to_time, dashboard, title, target_id

    def _run_report(self) -> None:
        validated = self._validate_inputs()
        if validated is None:
            return

        action, from_time, to_time, dashboard, title, target_id = validated

        self._set_busy(True)
        self._append_log(
            f"Запуск {'создания' if action == 'create' else 'обновления'} отчёта "
            f"для дашборда «{dashboard}»..."
        )

        worker = ReportWorker(
            action=action,
            report_service=self._report_service,
            from_time=from_time,
            to_time=to_time,
            dashboard=dashboard,
            title=title,
            target_id=target_id,
        )
        worker.signals.success.connect(self._on_report_success)
        worker.signals.error.connect(self._on_report_error)
        worker.signals.finished.connect(lambda: self._set_busy(False))
        self._thread_pool.start(worker)

    def _on_report_success(self, message: str) -> None:
        self._append_log(message)
        self.statusBar().showMessage(message)
        QMessageBox.information(self, "Готово", message)

    def _on_report_error(self, message: str) -> None:
        self._append_log(f"Ошибка: {message}")
        self.statusBar().showMessage("Ошибка выполнения")
        QMessageBox.critical(self, "Ошибка", message)

    def _set_busy(self, busy: bool) -> None:
        self._run_button.setEnabled(not busy)
        self._progress_bar.setVisible(busy)

        if busy:
            self.statusBar().showMessage("Выполнение операции...")
        else:
            self.statusBar().showMessage("Готово")


def run_application() -> int:
    """Создаёт QApplication, применяет тему и запускает главное окно."""
    app = QApplication([])
    app.setApplicationName("python-autoreporter")
    app.setOrganizationName("python-autoreporter")

    theme_manager = ThemeManager(app)
    theme_manager.apply()

    window = MainWindow(theme_manager)
    window.show()

    return app.exec()
