import logging


def setup_logger():
    """
    Sets up a logger for the application.

    :return: Configured logger instance.
    """
    logger = logging.getLogger("rapidclip_generator")
    logger.setLevel(logging.DEBUG)

    # Create a stream handler to log to the console
    handler = logging.StreamHandler()

    # Define the log format
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    logger.addHandler(handler)

    return logger
