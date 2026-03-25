import logging
import sys


class _LoggerProxy:
    def __init__(self):
        self._logger = logging.getLogger("video_system.loguru_stub")
        if not self._logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            handler.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))
            self._logger.addHandler(handler)
            self._logger.setLevel(logging.INFO)
            self._logger.propagate = False

    def add(self, *args, **kwargs):
        return 0

    def remove(self, *args, **kwargs):
        return None

    def bind(self, *args, **kwargs):
        return self

    def opt(self, *args, **kwargs):
        return self

    def debug(self, message, *args, **kwargs):
        self._logger.debug(message)

    def info(self, message, *args, **kwargs):
        self._logger.info(message)

    def warning(self, message, *args, **kwargs):
        self._logger.warning(message)

    def error(self, message, *args, **kwargs):
        self._logger.error(message)

    def critical(self, message, *args, **kwargs):
        self._logger.critical(message)

    def success(self, message, *args, **kwargs):
        self._logger.info(message)

    def exception(self, message, *args, **kwargs):
        self._logger.exception(message)


logger = _LoggerProxy()
