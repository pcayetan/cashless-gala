import sys
import logging
from datetime import date
from pathlib import Path

from rich.logging import RichHandler


def init_logging():
    # Get today's date for log names
    today = date.today()

    # Create a logger
    log = logging.getLogger()
    log.setLevel("NOTSET")  # NOTSET = 0 => Does not filter anything

    # Logging handler
    consoleHandler = RichHandler()

    # Check if the log repository exist, if not create it

    if getattr(sys, "frozen", False):
        # If the program has been frozen by cx_freeze
        rootDir = Path(sys.executable).absolute().parents[0]
    else:
        rootDir = Path(__file__).absolute().parents[2]
    dirPath = Path(rootDir, "log")

    fileName = Path("{}.log".format(today.strftime("%d-%m-%y")))
    if not dirPath.is_dir():
        dirPath.mkdir(parents=True, exist_ok=True)

    fileHandler = logging.FileHandler(
        filename=str(dirPath / fileName),
        encoding="utf-8",
        mode="a",
    )

    # Setup handler
    fileHandler.setLevel("DEBUG")  # All logs are stored in file no matter the log level
    consoleHandler.setLevel("DEBUG")

    # Logging formatter
    consoleFormatter = logging.Formatter(
        fmt="%(message)s", datefmt="[%d-%m-%y %H:%M:%S]"
    )
    fileFormatter = logging.Formatter(
        fmt="%(asctime)s - %(levelname)s:  %(message)s", datefmt="[%d-%m-%y %H:%M:%S]"
    )

    # Setup formatter
    consoleHandler.setFormatter(consoleFormatter)
    fileHandler.setFormatter(fileFormatter)

    log.addHandler(consoleHandler)
    log.addHandler(fileHandler)


class InterfaceFilter(logging.Filter):
    def __init__(self, name):
        super().__init__()
        self.name = name

    def filter(self, record: logging.LogRecord):
        return record.getMessage().startswith(self.name)
