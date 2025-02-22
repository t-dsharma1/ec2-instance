import base64
import gzip
import io
import pickle
import re

from genie_core.utils import logging
from genie_dao.datamodel.chatbot_db_model import (
    FlowContext,
    FlowStateMachine,
    FlowStateMetadata,
)

_log = logging.get_or_create_logger(logger_name="Helpers")


# Helper function to paginate a list of data
def paginate(data, current_page, page_size):
    """Paginates a list of data.

    Parameters:
        data (list): The list of data to paginate.
        current_page (int): The current page number.
        page_size (int): The number of items per page.

    Returns:
        dict: A dictionary containing the paginated data with current page, next page number,
              previous page number, and the paginated data.
    """
    # Calculate total number of pages
    total_pages = (len(data) + page_size - 1) // page_size

    # Ensure current_page is within valid range
    current_page = max(1, min(current_page, total_pages))

    # Calculate start and end index for current page
    start_idx = (current_page - 1) * page_size
    end_idx = min(start_idx + page_size, len(data))

    # Get current page data
    current_page_data = data[start_idx:end_idx]

    # Calculate next page number
    next_page = current_page + 1 if current_page < total_pages else None

    # Calculate previous page number
    prev_page = current_page - 1 if current_page > 1 else None

    # Return paginated data
    return {"current_page": current_page, "next_page": next_page, "prev_page": prev_page, "data": current_page_data}


# Helper function to create a sort key function for sorting a list of dictionaries or objects
def create_sort_key_function(sort_obj):
    def get_sort_key(x):
        # Logic using sort_obj captured from the enclosing scope
        first_level = x.get(sort_obj[0]) if isinstance(x, dict) else getattr(x, sort_obj[0], None)

        if isinstance(first_level, dict):
            return first_level.get(sort_obj[1], None)
        else:
            return getattr(first_level, sort_obj[1], None)

    return get_sort_key


def is_base64(s: str) -> bool:
    """Checks if the given string is base64 encoded.

    Args:
        s (str): The string to check.
    Returns:
        bool: True if the string is base64 encoded, False otherwise.
    """
    if isinstance(s, str):
        try:
            if len(s) % 4 == 0 and re.match("^[A-Za-z0-9+/]*={0,2}$", s):
                base64.b64decode(s, validate=True)
                return True
        except Exception:
            _log.error("Error while checking if string is base64 encoded")
            return False
    return False


def compress_data(data: FlowStateMachine | dict[str, FlowStateMetadata] | dict[str, FlowContext]) -> str:
    """Compresses and serializes the given data.

    Args:
        data (object): The data to compress and serialize.
    Returns:
        str: The compressed and serialized data.
    """
    serialized = pickle.dumps(data)
    compressed = gzip.compress(serialized)
    encoded = base64.b64encode(compressed).decode("utf-8")
    return encoded


class ConnectAiToGenieUnpickler(pickle.Unpickler):
    """Unpickler that handles old flows, which were pickled before we moved data models
    to a separate package."""

    def find_class(self, module: str, name: str):
        if module == "connectai.modules.datamodel.storage.chatbot_db_model.models":
            module = "genie_dao.datamodel.chatbot_db_model.models"
        return super().find_class(module, name)


def decompress_data(data: str | dict) -> dict:
    """Decompresses and deserializes the given data.

    Args:
        data (str): The data to decompress and deserialize.
    Returns:
        dict: The decompressed and deserialized data.
    """
    if isinstance(data, str) and is_base64(data):
        decoded = base64.b64decode(data.encode("utf-8"))
        decompressed = gzip.decompress(decoded)
        return ConnectAiToGenieUnpickler(io.BytesIO(decompressed)).load()
    else:
        # Handle old data format (assuming it is already deserialized)
        return data


def safe_decompress_data(data: dict, key: str) -> dict:
    """Safely decompresses data using the specified key.

    Args:
        data (dict): The dictionary containing the data.
        key (str): The key to access the data.
    Returns:
        dict: The decompressed data.
    Raises:
        KeyError: If the specified key is not found in the data.
        RuntimeError: If there is an error while decompressing the data.
    """
    try:
        return decompress_data(data[key])
    except KeyError:
        raise KeyError(f"Key '{key}' not found in data")
    except Exception as e:
        raise RuntimeError(f"Error decompressing '{key}': {str(e)}")


def flatten_nested_dict(d: dict[str, any], parent_key: str = "", sep: str = ".") -> dict[str, any]:
    """Flattens a nested dictionary by concatenating nested keys into a single key,
    separated by a specified separator.

    Args:
        d (Dict[str, Any]): The nested dictionary to flatten.
        parent_key (str): The base key string, used during the recursive calls.
        sep (str): The separator to use between concatenated keys.

    Returns:
        Dict[str, Any]: A flattened dictionary with concatenated keys.
    """
    flattened = {}
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            flattened.update(flatten_nested_dict(v, new_key, sep=sep))
        else:
            flattened[new_key] = v
    return flattened
