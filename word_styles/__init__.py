"""
Word Styles Package

This package provides a centralized registry and utilities for managing DOCX paragraph styles,
with a focus on properly handling spacing, borders, and other styling attributes consistently
across different Word versions and platforms.
"""

from .registry import ParagraphBoxStyle, StyleRegistry, get_or_create_style
from .xml_utils import make_spacing_node, make_border_node, twips_from_pt, pt_from_twips

__all__ = [
    'ParagraphBoxStyle',
    'StyleRegistry',
    'get_or_create_style',
    'make_spacing_node',
    'make_border_node',
    'twips_from_pt',
    'pt_from_twips',
] 