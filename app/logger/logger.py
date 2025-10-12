import logging
from config.config import config

class Logger:

    _instance = None

    def __init__(self):
        self.log_name:str = config.app_name
        self.log_level:str = "INFO"
        self.logger:logging.Logger = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance
    

    def get_logger(self) -> logging.Logger:
        if not self.logger:
            logger = logging.getLogger(self.log_name)
            logger.setLevel(self.log_level)

            fmt_str = "%(asctime)s | %(levelname)s | %(thread)d | %(module)s | %(funcName)s | %(message)s"
            formatter = logging.Formatter(fmt_str)

            console_handler = logging.StreamHandler()
            console_handler.setLevel(self.log_level)
            console_handler.setFormatter(formatter)

            logger.addHandler(console_handler)
            self.logger = logger
        
        return self.logger

logger:logging.Logger = Logger().get_logger()







