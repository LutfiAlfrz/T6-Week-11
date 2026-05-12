# Nama  : Lutfi Alfarizi
# NIM   : F1D02310121
# Kelas : C

from typing import Callable, Any
from PySide6.QtCore import QObject, QThread, Signal
from api_service import ApiError

class ApiWorker(QObject):
    finished = Signal(object)
    error    = Signal(str)

    def __init__(self, func: Callable, *args: Any, **kwargs: Any):
        super().__init__()
        self._func   = func
        self._args   = args
        self._kwargs = kwargs

    def run(self) -> None:
        try:
            result = self._func(*self._args, **self._kwargs)
            self.finished.emit(result)
        except ApiError as e:
            self.error.emit(str(e))
        except Exception as e:
            self.error.emit(f"Error tidak terduga: {e}")


def run_worker(worker: ApiWorker) -> QThread:
    thread = QThread()
    worker.moveToThread(thread)

    thread.started.connect(worker.run)

    worker.finished.connect(thread.quit)
    worker.error.connect(thread.quit)

    thread.finished.connect(worker.deleteLater)
    thread.finished.connect(thread.deleteLater)

    thread.start()
    return thread