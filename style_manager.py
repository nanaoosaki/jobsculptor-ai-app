"""Manages access to design tokens and compiled CSS paths."""

import os
import json
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

_TOKENS = None
_TOKENS_PATH = Path(__file__).parent / 'design_tokens.json'

def load_tokens():
    """Loads design tokens from the JSON file."""
    global _TOKENS
    if _TOKENS is None:
        try:
            with open(_TOKENS_PATH, 'r') as f:
                _TOKENS = json.load(f)
            logger.info(f"Successfully loaded design tokens from {_TOKENS_PATH}")
        except FileNotFoundError:
            logger.error(f"Design tokens file not found at {_TOKENS_PATH}")
            _TOKENS = {} # Fallback to empty dict
        except json.JSONDecodeError:
            logger.error(f"Error decoding JSON from {_TOKENS_PATH}")
            _TOKENS = {} # Fallback to empty dict
        except Exception as e:
            logger.error(f"An unexpected error occurred loading tokens: {e}")
            _TOKENS = {}
    return _TOKENS

class StyleManager:
    """Provides access to styling resources."""

    @staticmethod
    def token(key, default=None):
        """Get a design token value by key."""
        tokens = load_tokens()
        value = tokens.get(key, default)
        if value is None:
            logger.warning(f"Design token '{key}' not found.")
        return value

    @staticmethod
    def preview_css_path() -> str:
        """Get the absolute path to the compiled preview CSS file."""
        path = Path(__file__).parent / 'static' / 'css' / 'preview.css'
        if not path.exists():
            logger.warning(f"Preview CSS file not found at {path}. Make sure SCSS is compiled.")
        return str(path.resolve())

    @staticmethod
    def print_css_path() -> str:
        """Get the absolute path to the compiled print CSS file."""
        path = Path(__file__).parent / 'static' / 'css' / 'print.css'
        if not path.exists():
            logger.warning(f"Print CSS file not found at {path}. Make sure SCSS is compiled.")
        return str(path.resolve()) 