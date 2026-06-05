"""Главное окно приложения python-autoreporter."""

from PySide6.QtWidgets import QMainWindow


class MainWindow(QMainWindow):
    """Основное окно приложения с элементами управления отчётами."""

    def __init__(self) -> None:
        """Инициализирует главное окно и задаёт его заголовок."""
        super().__init__()
        self.setWindowTitle("python-autoreporter")
