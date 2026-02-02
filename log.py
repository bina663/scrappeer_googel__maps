import logging
from logging.handlers import RotatingFileHandler
import config

# CONFIG DO LOGS
logger = logging.getLogger("scrapper_logger")
logger.setLevel(logging.DEBUG)

# EVITA QUE O ARQUIVO FIQUE GRANDE
handler = RotatingFileHandler(
    config.LOG_FILE,
    maxBytes=5_000_000,  # 5 MB
    backupCount=5,
    encoding='utf-8'
)

formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%d/%m/%Y %H:%M:%S"
)
handler.setFormatter(formatter)
logger.addHandler(handler)

#RECEBERA MENSAGEM INDICANDO SITUACAO DO BOT e LEVEL QUE INDICA A MENSAGEM
def log(message, level="INFO", exc_info=False):
    level = level.upper()
    
    if level not in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
        level = "INFO"
        message = f"NÍVEL DESCONHECIDO: {message}"

    getattr(logger, level.lower())(message, exc_info=exc_info)
