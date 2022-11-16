from core import config
from core import utils

TRACE = 'TRACE'
DEBUG = 'DEBUG'
WARNING = 'WARNING'
INFO = 'INFO'
ERROR = 'ERROR'
CRITICAL = 'CRITICAL'

LEVELS = {
  TRACE: 1,
  DEBUG: 2,
  WARNING: 3,
  INFO: 4,
  ERROR: 5,
  CRITICAL: 6,
}

NAME = utils.getenv('LOGGING_NAME', default=config.NAME)
LEVEL = utils.getenv('LOGGING_LEVEL', default=TRACE)
GCP_PROJECT_ID = utils.getenv('LOGGING_GCP_PROJECT_ID', required=False)
formatter = utils.load_class(
  f"core.logging.formatter.{utils.getenv('LOGGING_FORMATTER', 'JSONFormatter')}"
)


def is_enabled(level):
  return LEVELS[level] >= LEVELS[LEVEL]
