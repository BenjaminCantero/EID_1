import logging
import os
from datetime import datetime


class InMemoryLogHandler(logging.Handler):
    """Handler que mantiene un buffer de logs para mostrar en la UI."""

    def __init__(self, max_records=1000):
        super().__init__()
        self.records = []
        self.max_records = max_records

    def emit(self, record):
        log_entry = self.format(record)
        self.records.append(log_entry)
        if len(self.records) > self.max_records:
            self.records.pop(0)

    def get_records(self):
        return list(self.records)

    def clear(self):
        self.records.clear()


_logger = None
_memory_handler = None


def setup_logger(name="EID", level=logging.INFO, logfile=None):
    global _logger, _memory_handler
    if _logger is not None:
        return _logger

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.propagate = False

    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", "%Y-%m-%d %H:%M:%S")

    memory_handler = InMemoryLogHandler()
    memory_handler.setFormatter(formatter)
    logger.addHandler(memory_handler)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    if logfile:
        file_handler = logging.FileHandler(logfile, encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    _logger = logger
    _memory_handler = memory_handler
    logger.info("Logger inicializado")
    return logger


def get_logger():
    global _logger
    if _logger is None:
        return setup_logger()
    return _logger


def get_log_entries():
    global _memory_handler
    if _memory_handler is None:
        setup_logger()
    return _memory_handler.get_records()


def export_logs(path=None):
    global _memory_handler
    if _memory_handler is None:
        setup_logger()
    if path is None:
        path = os.path.abspath("logs_eid.txt")
    with open(path, "w", encoding="utf-8") as f:
        f.write("# Logs de EID\n")
        f.write(f"# Exportado: {datetime.now():%Y-%m-%d %H:%M:%S}\n\n")
        for line in _memory_handler.get_records():
            f.write(line + "\n")
    return path


def clear_logs():
    global _memory_handler
    if _memory_handler is not None:
        _memory_handler.clear()
