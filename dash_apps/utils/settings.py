"""
Centralized settings utilities for loading JSON configurations (package-safe).
"""
from __future__ import annotations

import json
import os
from functools import lru_cache
from typing import Any, Dict
from jinja2 import Environment, FileSystemLoader

# Determine the base directory of the repository to resolve config paths robustly.
_BASE_DIR = os.path.dirname(os.path.dirname(__file__))  # dash_apps/
_CONFIG_DIR = os.path.join(_BASE_DIR, 'config')
_TEMPLATES_DIR = os.path.join(_BASE_DIR, 'templates')


@lru_cache(maxsize=32)
def load_json_config(filename: str) -> Dict[str, Any]:
    """Load and cache a JSON configuration file from dash_apps/config/ without
    requiring it to be a Python package.

    Args:
        filename: The JSON filename located under dash_apps/config/

    Returns:
        Dict loaded from the JSON file

    Raises:
        FileNotFoundError: if the file does not exist
        json.JSONDecodeError: if the JSON is invalid
    """
    path = os.path.join(_CONFIG_DIR, filename)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


@lru_cache(maxsize=8)
def get_jinja_template(template_name: str) -> Any:
    """Load and cache a Jinja2 template from dash_apps/templates/.

    Args:
        template_name: The template filename located under dash_apps/templates/

    Returns:
        Jinja2 Template object

    Raises:
        FileNotFoundError: if the template does not exist
    """
    env = Environment(loader=FileSystemLoader(_TEMPLATES_DIR))
    return env.get_template(template_name)
