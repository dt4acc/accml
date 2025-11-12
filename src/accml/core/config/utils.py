import logging
from pathlib import Path

logger = logging.getLogger("accml")


def full_data_path(path: Path):
    """ """
    from importlib.resources import files

    full_path = files("accml").joinpath(path)
    # Todo: get a better logging message
    logger.info("Loading data path %s from %s", path, full_path)
    return full_path
