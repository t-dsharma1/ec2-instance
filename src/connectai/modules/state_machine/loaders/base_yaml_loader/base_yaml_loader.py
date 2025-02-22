import os

import yaml


class BaseYAMLLoader:
    """Base class for loading a YAML file."""

    def __init__(self, file_path: str, relative_path: bool = True):
        if relative_path:
            self.file_path = os.path.join(os.path.dirname(__file__), file_path)
        else:
            self.file_path = file_path

    def load(self) -> dict:
        with open(self.file_path) as file:
            return yaml.safe_load(file)
