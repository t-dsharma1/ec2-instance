import os.path
from pathlib import Path


def get_package_root_path() -> Path:
    import connectai

    return Path(os.path.realpath(os.path.dirname(connectai.__file__))).parent.parent
