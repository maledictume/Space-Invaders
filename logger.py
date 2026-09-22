import logging
import sys
import traceback

logging.basicConfig(
    filename='game_errors.log',
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s\n%(message)s\n' + '-'*40
)

def log_uncaught_exceptions(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    logging.error("Unhandled exception:", exc_info=(exc_type, exc_value, exc_traceback))

sys.excepthook = log_uncaught_exceptions

def log_error(msg, exception=None):
    if exception:
        logging.error(f"{msg}\n{traceback.format_exc()}")
    else:
        logging.error(msg)