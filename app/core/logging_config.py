"""
MedBotX - Structured Logging Configuration
Developed by Bhaskar Shivaji Kumbhar
"""
import logging
import sys
from pathlib import Path
from app.core.config import settings


def setup_logging():
    Path("logs").mkdir(exist_ok=True)

    log_format = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    handlers = [
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(settings.LOG_FILE, encoding="utf-8"),
    ]

    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
        format=log_format,
        datefmt=date_format,
        handlers=handlers,
    )

    # Suppress noisy third-party loggers
    for lib in ("httpx", "httpcore", "openai", "urllib3"):
        logging.getLogger(lib).setLevel(logging.WARNING)

    logger = logging.getLogger("medbotx")
    logger.info("MedBotX logging initialised — Developed by Bhaskar Shivaji Kumbhar")
    return logger


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(f"medbotx.{name}")
