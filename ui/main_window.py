# ui.main_window.py

from pathlib import Path
from configuration.app_config import load_config
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QFileDialog,
    QVBoxLayout,
    QHBoxLayout,
    QMessageBox,
)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("python-autoreporter")