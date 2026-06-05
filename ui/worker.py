"""Фоновые задачи для длительных операций отчётов."""

from PySide6.QtCore import QObject, QRunnable, Signal, Slot


class WorkerSignals(QObject):
    """Сигналы для передачи результата фоновой задачи в UI-поток."""

    finished = Signal()
    error = Signal(str)
    success = Signal(str)


class ReportWorker(QRunnable):
    """Выполняет создание или обновление отчёта в фоновом потоке."""

    def __init__(
        self,
        action: str,
        report_service,
        from_time: str,
        to_time: str,
        dashboard: str,
        title: str,
        target_id: str,
    ) -> None:
        super().__init__()
        self.signals = WorkerSignals()
        self._action = action
        self._report_service = report_service
        self._from_time = from_time
        self._to_time = to_time
        self._dashboard = dashboard
        self._title = title
        self._target_id = target_id

    @Slot()
    def run(self) -> None:
        """Запускает операцию отчёта и отправляет результат через сигналы."""
        try:
            if self._action == "create":
                self._report_service.create_report(
                    from_time=self._from_time,
                    to_time=self._to_time,
                    dashboard=self._dashboard,
                    parent_id=self._target_id,
                    title=self._title,
                )
                self.signals.success.emit("Отчёт успешно создан.")
            else:
                self._report_service.update_report(
                    from_time=self._from_time,
                    to_time=self._to_time,
                    dashboard=self._dashboard,
                    page_id=self._target_id,
                    title=self._title,
                )
                self.signals.success.emit("Отчёт успешно обновлён.")
        except Exception as error:
            self.signals.error.emit(str(error))
        finally:
            self.signals.finished.emit()
