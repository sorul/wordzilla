"""Script to handle logging."""

import logging
import socket
from logging.handlers import SysLogHandler

from wordzilla.singleton import Singleton
from wordzilla.credentials import get_credentials


"""URL: https://my.papertrailapp.com/events ."""


class ContextFilter(logging.Filter):
  """Filter to add hostname to log record."""

  hostname = socket.gethostname()

  def filter(self, record):  # noqa
    """Add the hostname 'e.g. raspberrypi' to the log record."""
    record.hostname = ContextFilter.hostname
    return True  # No filtering


class Log(metaclass=Singleton):
  """Class to manage logging."""

  def __init__(self):
    """Initialize the logger."""
    self.logger = logging.getLogger('tradeo')
    self.logger.setLevel(logging.DEBUG)
    cds = get_credentials()

    # Syslog logging
    if cds['syslog'].get('activated', False):
      self._build_log()

  def _build_log(self) -> None:
    cds = get_credentials()
    address = cds['syslog']['address']
    port = int(cds['syslog']['port'])
    handler = SysLogHandler(address=(address, port))

    # Filter
    handler.addFilter(ContextFilter())
    formatter = logging.Formatter(
        '%(asctime)s %(levelname)s trading-bot: %(message)s',
        datefmt='%b %d %H:%M:%S')

    # Format
    handler.setFormatter(formatter)

    # Level
    handler.setLevel(cds['logging'].get('level', 'DEBUG'))

    # Add the handler
    self.logger.addHandler(handler)

  def debug(self, msg: str):
    """Log debug message."""
    self.logger.debug(msg)

  def info(self, msg: str):
    """Log info message."""
    self.logger.info(msg)

  def warning(self, msg: str):
    """Log warning message."""
    self.logger.warning(f'🟡 {msg}')

  def error(self, msg: str):
    """Log error message."""
    msg = msg.replace('\n', ' ')
    self.logger.error(f'🔴 {msg}')


# Singleton instance
log = Log()
