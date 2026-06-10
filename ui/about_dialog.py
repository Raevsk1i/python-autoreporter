"""Диалог «О программе»."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QLabel, QPushButton, QVBoxLayout

from configuration.app_info import ABOUT_TEXT, CREDIT_SHORT, GITHUB_URL
from ui.widgets import make_button_row, make_credit_label


class AboutDialog(QDialog):
    """Отображает информацию о приложении и авторе."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("О программе")
        self.setMinimumWidth(420)

        layout = QVBoxLayout(self)
        layout.setSpacing(14)

        about_label = QLabel(ABOUT_TEXT)
        about_label.setWordWrap(True)
        about_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        layout.addWidget(about_label)

        layout.addWidget(make_credit_label(CREDIT_SHORT))

        github_button = QPushButton("Открыть на GitHub")
        github_button.setObjectName("ghostButton")
        github_button.clicked.connect(self._open_github)

        close_button = QPushButton("Закрыть")
        close_button.clicked.connect(self.accept)

        layout.addLayout(make_button_row(github_button, close_button))

    def _open_github(self) -> None:
        from PySide6.QtGui import QDesktopServices
        from PySide6.QtCore import QUrl

        QDesktopServices.openUrl(QUrl(GITHUB_URL))
