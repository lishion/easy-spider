import logging.config
from easy_spider.tool import EXE_PATH
from os import path


LOG_SETTING = {
    "version": 1,
    "formatters": {
        "default": {
            "format": "[%(asctime)s] %(levelname)s %(filename)s %(funcName)s(%(lineno)d) %(message)s",
            "datefmt": '%Y-%m-%d %H:%M:%S'
        },
        "colored": {
            '()': 'colorlog.ColoredFormatter',
            'format': "%(log_color)s[%(asctime)s] %(levelname)s %(message)s",
            'datefmt': '%Y-%m-%d %H:%M:%S'
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "colored",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": path.join(EXE_PATH, "easy_spider.log"),
            "level": "WARNING",
            "formatter": "default",
            "maxBytes": 1024,
            "encoding": "utf-8"
        }
    },
    "loggers": {
        "easy_spider.console": {
            "level": "INFO",
            "handlers": ["console"]
        },
        "easy_spider.file": {
            "level": "INFO",
            "handlers": ["file"]
        }
    }
}
logging.config.dictConfig(LOG_SETTING)
console_logger = logging.getLogger("easy_spider.console")
file_logger = logging.getLogger("easy_spider.file")
