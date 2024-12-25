"""Manage kedro credentials."""
from pathlib import Path
from kedro.config import OmegaConfigLoader, MissingConfigException
from kedro.framework.project import settings
from omegaconf.errors import OmegaConfBaseException
from typing import Dict, Any
import yaml
import os
import re


def root_project() -> Path:
  """Return the root project path."""
  return Path(__file__).parent.parent.parent


def get_credentials() -> Dict[str, Dict]:
  """Obtain the credentials."""
  conf_path = str(root_project() / settings.CONF_SOURCE)
  conf_loader = OmegaConfigLoader(conf_source=conf_path)
  try:
    credentials = conf_loader['credentials']
  except (MissingConfigException, OmegaConfBaseException):
    credentials = _load_env_config_from_yaml(
        yaml_path=os.path.join(conf_path, 'local/credentials.yml')
    )

  return credentials


def _load_env_config_from_yaml(yaml_path: str) -> Dict[str, Any]:
  # Regular expression to search for variables in the format ${oc.env:VAR}
  pattern = re.compile(r'\$\{oc\.env:([A-Za-z0-9_]+)\}')

  # Function to replace values in the YAML structure
  def replace_env_vars(value: Any) -> Any:
    result = None
    if isinstance(value, str):
      match = pattern.search(value)
      if match:
        env_key = match.group(1)  # Get the variable name
        # Replace with the env variable or an empty string
        result = os.getenv(env_key, '')
    elif isinstance(value, dict):
      result = {k: replace_env_vars(v) for k, v in value.items()}
    elif isinstance(value, list):
      result = [replace_env_vars(v) for v in value]
    else:
      result = value
    return result

  # Load the YAML structure
  with open(yaml_path, 'r') as file:
    yaml_config = yaml.safe_load(file)

  # Replace variables
  return replace_env_vars(yaml_config)
