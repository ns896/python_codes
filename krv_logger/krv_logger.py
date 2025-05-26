import logging

class KRV_Logger:
    def __init__(self, name: str, file_name: str = None, level: str = "DEBUG"):
        
        
        self.log_level = logging.INFO
        self.log_numeric_value = getattr(logging, level.upper(), None)
        if not isinstance(self.log_numeric_value, int):
            raise ValueError(f"Invalid log level: {level}")
        self.log_level = self.log_numeric_value

        #Remove default logger setting if any
        self.logger = logging.getLogger(name)
        self.logger.setLevel(self.log_level)

        #Remove default handler if any
        if self.logger.hasHandlers():
            self.logger.handlers.clear()

        #Console handler
        self.ch = logging.StreamHandler()
        self.ch.setLevel(self.log_level)
        self.ch_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.ch.setFormatter(self.ch_formatter)
        self.logger.addHandler(self.ch)

        #FileHandler
        if file_name:
            self.fh = logging.FileHandler(file_name)
            self.fh.setLevel(self.log_level)
            self.fh.setFormatter(self.ch_formatter)
            self.logger.addHandler(self.fh)

    def get_logger(self):
        return self.logger
            
            

        