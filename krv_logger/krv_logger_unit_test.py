from krv_logger import KRV_Logger

log_ = KRV_Logger(name="krv_logger_unit_test", file_name="krv_logger_unit_test.log", level="INFO")
LOG = log_.get_logger()

LOG.info("This is a test message")
LOG.debug("This is a debug message")
LOG.warning("This is a warning message")
LOG.error("This is an error message")
LOG.critical("This is a critical message")
