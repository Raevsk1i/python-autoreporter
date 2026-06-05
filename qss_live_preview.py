"""
Живой предпросмотр QSS-стилей.

Импортируйте enable_qss_live_preview после создания QApplication.
"""

from pathlib import Path

from PySide6.QtCore import QFileSystemWatcher, QTimer

QSS_PATH = Path("data/style.qss")
QSS_RELOAD_DELAY_MS = 80


def enable_qss_live_preview(
    app,
    qss_path: Path | str = QSS_PATH,
    reload_delay_ms: int = QSS_RELOAD_DELAY_MS,
):
    """
    Включает автоматическую перезагрузку QSS-стилей при изменении файла.

    Args:
        app: Экземпляр QApplication.
        qss_path: Путь к файлу стилей .qss.
        reload_delay_ms: Задержка перед применением стилей после изменения (мс).

    Returns:
        QFileSystemWatcher, отслеживающий файл и директорию стилей.
    """
    qss_path = Path(qss_path)
    watcher = QFileSystemWatcher(app)

    def apply_qss() -> None:
        """Читает QSS-файл и применяет стили к приложению."""
        try:
            app.setStyleSheet(qss_path.read_text(encoding="utf-8"))
        except OSError as error:
            print(f"QSS live preview reload failed: {error}")

    def watch_qss() -> None:
        """Добавляет директорию и файл стилей в список отслеживания."""
        directory = str(qss_path.parent)
        if directory not in watcher.directories():
            watcher.addPath(directory)

        file_path = str(qss_path)
        if qss_path.exists() and file_path not in watcher.files():
            watcher.addPath(file_path)

    def reload_qss(_changed_path=None) -> None:
        """Переподписывается на файл и планирует отложенное применение стилей."""
        watch_qss()
        QTimer.singleShot(reload_delay_ms, apply_qss)

    watcher.fileChanged.connect(reload_qss)
    watcher.directoryChanged.connect(reload_qss)

    watch_qss()
    apply_qss()

    return watcher
