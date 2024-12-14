"""Manage kedro credentials."""
from pathlib import Path
from kedro.config import OmegaConfigLoader, MissingConfigException
from kedro.framework.project import settings
from typing import Dict


def root_project() -> Path:
  """Return the root project path."""
  return Path(__file__).parent.parent.parent


def get_credentials() -> Dict[str, Dict]:
  """Obtain the credentials."""
  conf_path = str(root_project() / settings.CONF_SOURCE)
  conf_loader = OmegaConfigLoader(conf_source=conf_path)

  try:
    credentials = conf_loader['credentials']
  except MissingConfigException:
    credentials = {}

  return credentials
