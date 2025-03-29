import logging


def setup_logging(filename='game_log.pgn'):
    """
    Configure global logging.
    :param filename: Name of the log file.
    """
    logging.basicConfig(
        filename=filename,
        level=logging.INFO,
        format='%(message)s'
    )
