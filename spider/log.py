import logging.config

LOG_SETTING = {
    "version": 1,
    "formatters": {
        "default": {
            "format": "%(asctime)s %(filename)s %(funcName)s %(lineno)d %(message)s",
            "datefmt": '%Y-%m-%d %H:%M:%S'
        },
        "colored": {
            '()': 'colorlog.ColoredFormatter',
            'format': "%(log_color)s [%(asctime)s] %(levelname)-8s %(filename)s %(funcName)s(%(lineno)d) %(message)s",
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
            "filename": "spider.log",
            "level": "WARNING",
            "formatter": "default",
            "maxBytes": 1024,
            "encoding": "utf-8"
        }
    },
    "loggers": {
        "custom": {
            "level": "INFO",
            "handlers": ["console", "file"]
        }
    }
}
logging.config.dictConfig(LOG_SETTING)
logger = logging.getLogger("custom")