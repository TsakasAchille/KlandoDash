"""
Centralized settings utilities for loading JSON configurations.
"""
from __future__ import annotations

import json
import os
from functools import lru_cache
from typing import Any, Dict

# Base directory for config files (this file's directory)
_CONFIG_BASE_DIR = os.path.dirname(__file__)


@lru_cache(maxsize=32)
def load_json_config(filename: str) -> Dict[str, Any]:
    """Load and cache a JSON configuration file from the config directory.

    Args:
        filename: The JSON filename located under dash_apps/config/

    Returns:
        Dict loaded from the JSON file

    Raises:
        FileNotFoundError: if the file does not exist
        json.JSONDecodeError: if the JSON is invalid
    """
    path = os.path.join(_CONFIG_BASE_DIR, filename)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
