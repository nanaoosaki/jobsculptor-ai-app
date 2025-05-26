# Compatibility layer for cross-format styling
# Translates CSS rules based on target rendering engine capabilities

from .translator import translate, to_css, to_word_xml_data
from .capability_tables import CAPABILITY

__all__ = ['translate', 'to_css', 'to_word_xml_data', 'CAPABILITY'] 