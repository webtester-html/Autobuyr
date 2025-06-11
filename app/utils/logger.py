import datetime
import logging
import sys

SUCCESS_LEVEL = 25
logging.addLevelName(SUCCESS_LEVEL, "SUCCESS")

# TODO: Simplify logger structure — minimize duplication, streamline level handling, and separate formatting concerns more cleanly

class SimpleFormatter(logging.Formatter):
    def format(self, record):
        timestamp = datetime.datetime.now().strftime("%d.%m.%y %H:%M:%S")
        record.levelname = f"[{timestamp}] - [{record.levelname}]: "
        return super().format(record)


class CustomLogger(logging.Logger):
    def success(self, msg, *args, **kwargs):
        self.isEnabledFor(SUCCESS_LEVEL) and self._log(SUCCESS_LEVEL, msg, args, **kwargs)


logging.setLoggerClass(CustomLogger)
logger = logging.getLogger("gifts_buyer")
logger.setLevel(logging.DEBUG)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
handler.setFormatter(SimpleFormatter('%(levelname)s %(message)s'))
logger.addHandler(handler)


class LoggerInterface:
    @staticmethod
    def info(message: str) -> None:
        print("\r", end="")
        logger.info(message)

    @staticmethod
    def warn(message: str) -> None:
        print("\r", end="")
        logger.warning(message)

    @staticmethod
    def error(message: str) -> None:
        print("\r", end="")
        logger.error(message)

    @staticmethod
    def success(message: str) -> None:
        print("\r", end="")
        logger.success(message) if isinstance(logger, CustomLogger) else logger.info(f"[SUCCESS] {message}")

    @staticmethod
    def log_same_line(message: str, level: str = "INFO") -> None:
        timestamp = datetime.datetime.now().strftime("%d.%m.%y %H:%M:%S")
        print(f"\r[{timestamp}] - [{level.upper()}]: {message}", end="", flush=True)


info = LoggerInterface.info
warn = LoggerInterface.warn
error = LoggerInterface.error
success = LoggerInterface.success
log_same_line = LoggerInterface.log_same_line
