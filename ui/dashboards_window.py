"""Окно управления дашбордами и панелями в dashboards.json."""

from pathlib import Path

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from configuration.app_config import AppConfig
from ui.widgets import make_button_row, make_hint_label, make_scrollable, make_section_title
from utils.dashboards_store import load_dashboards_data, save_dashboards_data


class DashboardsWindow(QDialog):
    """Добавление, удаление и редактирование дашбордов и панелей."""

    dashboards_saved = Signal()

    def __init__(self, config: AppConfig, parent=None) -> None:
        super().__init__(parent)
        self._config = config
        self._dashboards_path = Path(config.grafana.dashboards_path)
        self._data: dict = {}

        self.setWindowTitle("Дашборды")
        self.setMinimumSize(900, 620)
        self.resize(980, 700)

        self._build_ui()
        self._reload_data()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.addWidget(make_section_title("Управление дашбордами"))
        root.addWidget(
            make_hint_label(
                f"Файл: {self._dashboards_path}. "
                "Выберите дашборд слева, редактируйте панели справа."
            )
        )

        splitter = QSplitter()
        splitter.addWidget(self._build_dashboards_panel())
        splitter.addWidget(self._build_panels_panel())
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)
        root.addWidget(splitter, stretch=1)

        save_button = QPushButton("Сохранить в JSON")
        save_button.setObjectName("primaryButton")
        save_button.clicked.connect(self._save_dashboards)

        close_button = QPushButton("Закрыть")
        close_button.clicked.connect(self.close)

        root.addLayout(make_button_row(close_button, save_button))

    def _build_dashboards_panel(self) -> QWidget:
        panel = QWidget()
        layout = QVBoxLayout(panel)

        group = QGroupBox("Дашборды")
        group_layout = QVBoxLayout(group)

        self._dashboard_list = QListWidget()
        self._dashboard_list.currentItemChanged.connect(self._on_dashboard_selected)
        group_layout.addWidget(self._dashboard_list)

        add_button = QPushButton("Добавить дашборд")
        add_button.clicked.connect(self._add_dashboard)
        remove_button = QPushButton("Удалить дашборд")
        remove_button.setObjectName("dangerButton")
        remove_button.clicked.connect(self._remove_dashboard)

        buttons = QHBoxLayout()
        buttons.addWidget(add_button)
        buttons.addWidget(remove_button)
        group_layout.addLayout(buttons)

        layout.addWidget(group)
        return panel

    def _build_panels_panel(self) -> QWidget:
        content = QWidget()
        layout = QVBoxLayout(content)

        details_group = QGroupBox("Параметры дашборда")
        details_form = QFormLayout(details_group)

        self._dashboard_key_field = QLineEdit()
        self._dashboard_uid_field = QLineEdit()
        self._dashboard_slug_field = QLineEdit()

        details_form.addRow("Ключ", self._dashboard_key_field)
        details_form.addRow("Dashboard UID", self._dashboard_uid_field)
        details_form.addRow("Dashboard Slug", self._dashboard_slug_field)

        apply_details_button = QPushButton("Применить параметры дашборда")
        apply_details_button.clicked.connect(self._apply_dashboard_details)
        details_form.addRow("", apply_details_button)

        layout.addWidget(details_group)

        panels_group = QGroupBox("Панели")
        panels_layout = QVBoxLayout(panels_group)

        self._panels_list = QListWidget()
        panels_layout.addWidget(self._panels_list)

        add_panel_button = QPushButton("Добавить панель")
        add_panel_button.clicked.connect(self._add_panel)
        edit_panel_button = QPushButton("Изменить панель")
        edit_panel_button.clicked.connect(self._edit_panel)
        remove_panel_button = QPushButton("Удалить панель")
        remove_panel_button.setObjectName("dangerButton")
        remove_panel_button.clicked.connect(self._remove_panel)

        panel_buttons = QHBoxLayout()
        panel_buttons.addWidget(add_panel_button)
        panel_buttons.addWidget(edit_panel_button)
        panel_buttons.addWidget(remove_panel_button)
        panels_layout.addLayout(panel_buttons)

        layout.addWidget(panels_group, stretch=1)

        scroll = make_scrollable(content)
        scroll.setMinimumWidth(480)
        return scroll

    def _reload_data(self) -> None:
        self._data = load_dashboards_data(self._dashboards_path)
        self._refresh_dashboard_list()

    def _refresh_dashboard_list(self, select_key: str | None = None) -> None:
        self._dashboard_list.blockSignals(True)
        self._dashboard_list.clear()

        for key in sorted(self._data.keys()):
            item = QListWidgetItem(key)
            item.setData(256, key)
            self._dashboard_list.addItem(item)

        self._dashboard_list.blockSignals(False)

        if select_key and select_key in self._data:
            items = self._dashboard_list.findItems(select_key, 0)
            if items:
                self._dashboard_list.setCurrentItem(items[0])
                return

        if self._dashboard_list.count() > 0:
            self._dashboard_list.setCurrentRow(0)
        else:
            self._clear_panel_fields()

    def _current_dashboard_key(self) -> str | None:
        item = self._dashboard_list.currentItem()
        if item is None:
            return None
        return item.data(256)

    def _on_dashboard_selected(self, current: QListWidgetItem | None, _previous) -> None:
        if current is None:
            self._clear_panel_fields()
            return

        key = current.data(256)
        dashboard = self._data.get(key, {})

        self._dashboard_key_field.setText(key)
        self._dashboard_uid_field.setText(dashboard.get("dashboard_uid", ""))
        self._dashboard_slug_field.setText(dashboard.get("dashboard_slug", ""))

        self._panels_list.clear()
        for panel in dashboard.get("panels", []):
            panel_id = panel.get("panel_id", "")
            panel_name = panel.get("panel_name", "")
            self._panels_list.addItem(f"{panel_id} — {panel_name}")

    def _clear_panel_fields(self) -> None:
        self._dashboard_key_field.clear()
        self._dashboard_uid_field.clear()
        self._dashboard_slug_field.clear()
        self._panels_list.clear()

    def _add_dashboard(self) -> None:
        key, accepted = QInputDialog.getText(self, "Новый дашборд", "Ключ дашборда:")

        if not accepted:
            return

        key = key.strip()
        if not key:
            QMessageBox.warning(self, "Проверка", "Ключ дашборда не может быть пустым.")
            return

        if key in self._data:
            QMessageBox.warning(self, "Проверка", "Дашборд с таким ключом уже существует.")
            return

        self._data[key] = {
            "dashboard_uid": "",
            "dashboard_slug": "",
            "panels": [],
        }
        self._refresh_dashboard_list(select_key=key)

    def _remove_dashboard(self) -> None:
        key = self._current_dashboard_key()
        if key is None:
            return

        answer = QMessageBox.question(
            self,
            "Удаление",
            f"Удалить дашборд «{key}»?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if answer != QMessageBox.StandardButton.Yes:
            return

        del self._data[key]
        self._refresh_dashboard_list()

    def _apply_dashboard_details(self) -> None:
        old_key = self._current_dashboard_key()
        if old_key is None:
            return

        new_key = self._dashboard_key_field.text().strip()
        uid = self._dashboard_uid_field.text().strip()
        slug = self._dashboard_slug_field.text().strip()

        if not new_key:
            QMessageBox.warning(self, "Проверка", "Ключ дашборда не может быть пустым.")
            return

        if new_key != old_key and new_key in self._data:
            QMessageBox.warning(self, "Проверка", "Дашборд с таким ключом уже существует.")
            return

        dashboard = self._data.pop(old_key)
        dashboard["dashboard_uid"] = uid
        dashboard["dashboard_slug"] = slug
        self._data[new_key] = dashboard
        self._refresh_dashboard_list(select_key=new_key)

    def _add_panel(self) -> None:
        key = self._current_dashboard_key()
        if key is None:
            return

        panel = self._prompt_panel()
        if panel is None:
            return

        self._data[key]["panels"].append(panel)
        self._on_dashboard_selected(self._dashboard_list.currentItem(), None)

    def _edit_panel(self) -> None:
        key = self._current_dashboard_key()
        row = self._panels_list.currentRow()

        if key is None or row < 0:
            return

        current = self._data[key]["panels"][row]
        panel = self._prompt_panel(
            panel_id=current.get("panel_id", 0),
            panel_name=current.get("panel_name", ""),
        )

        if panel is None:
            return

        self._data[key]["panels"][row] = panel
        self._on_dashboard_selected(self._dashboard_list.currentItem(), None)

    def _remove_panel(self) -> None:
        key = self._current_dashboard_key()
        row = self._panels_list.currentRow()

        if key is None or row < 0:
            return

        del self._data[key]["panels"][row]
        self._on_dashboard_selected(self._dashboard_list.currentItem(), None)

    def _prompt_panel(
        self,
        panel_id: int = 1,
        panel_name: str = "",
    ) -> dict | None:
        dialog = QDialog(self)
        dialog.setWindowTitle("Панель")
        layout = QVBoxLayout(dialog)

        form = QFormLayout()
        id_spin = QSpinBox()
        id_spin.setRange(1, 999999)
        id_spin.setValue(int(panel_id) if panel_id else 1)
        name_field = QLineEdit(panel_name)
        form.addRow("Panel ID", id_spin)
        form.addRow("Название панели", name_field)
        layout.addLayout(form)

        save_button = QPushButton("Сохранить")
        save_button.setObjectName("primaryButton")
        cancel_button = QPushButton("Отмена")
        layout.addLayout(make_button_row(cancel_button, save_button))

        accepted = {"value": False}

        def accept() -> None:
            if not name_field.text().strip():
                QMessageBox.warning(dialog, "Проверка", "Название панели обязательно.")
                return
            accepted["value"] = True
            dialog.accept()

        save_button.clicked.connect(accept)
        cancel_button.clicked.connect(dialog.reject)

        if dialog.exec() != QDialog.DialogCode.Accepted or not accepted["value"]:
            return None

        return {
            "panel_id": id_spin.value(),
            "panel_name": name_field.text().strip(),
        }

    def _save_dashboards(self) -> None:
        try:
            save_dashboards_data(self._dashboards_path, self._data)
            self.dashboards_saved.emit()
            QMessageBox.information(self, "Сохранено", "Дашборды успешно сохранены.")
        except OSError as error:
            QMessageBox.critical(self, "Ошибка", str(error))

    def update_config(self, config: AppConfig) -> None:
        """Обновляет путь к JSON при смене конфигурации."""
        self._config = config
        self._dashboards_path = Path(config.grafana.dashboards_path)
        self._reload_data()
