from loguru import logger

logger.add(
    "data/logs/app.log",
    rotation="10 MB",
    retention="10 days"
)

app_logger = logger