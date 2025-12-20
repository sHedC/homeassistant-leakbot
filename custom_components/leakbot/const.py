"""Constants for Leakbot Integration."""

from logging import Logger, getLogger

LOGGER: Logger = getLogger(__package__)

NAME = "Leakbot"
DOMAIN = "leakbot"
VERSION = "1.1.3"
ATTRIBUTION = "Data provided by https://leakbot.io"

DEFAULT_REFRESH = 30
MIN_REFRESH = 15
MAX_REFRESH = 21600
