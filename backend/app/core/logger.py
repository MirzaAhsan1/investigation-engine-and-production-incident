from loguru import logger
import sys

# Remove default logger
logger.remove()

# Console Logger
logger.add(
    sys.stdout,
    level="INFO",
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
           "<level>{level}</level> | "
           "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
           "<level>{message}</level>"
)

# File Logger
logger.add(
    "logs/app.log",
    rotation="10 MB",
    retention="30 days",
    compression="zip",
    level="INFO",
    enqueue=True
)