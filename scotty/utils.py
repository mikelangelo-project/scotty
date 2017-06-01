import logging

from scotty.config import ScottyConfig


def setup_logging():
    log_dir = ScottyConfig().get('logging', 'log_dir', True)
    log_file = ScottyConfig().get('logging', 'log_file')
    log_format = ScottyConfig().get('logging', 'log_format')
    log_level = ScottyConfig().get('logging', 'log_level')

    logging.getLogger().setLevel(log_level.upper())
    file_handler = logging.FileHandler(log_dir + '/' + log_file)
    file_handler.setFormatter(logging.Formatter(log_format))
    logging.getLogger().addHandler(file_handler)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(logging.Formatter(log_format))
    logging.getLogger().addHandler(stream_handler)
