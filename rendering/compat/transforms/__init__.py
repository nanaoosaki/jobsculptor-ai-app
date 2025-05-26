# Transform registry for CSS compatibility fixes
# Transforms are applied in sequence based on engine capabilities

from .logical_box import LogicalBoxTransform
from .color_mix import ColorMixTransform  
from .font_features import FontFeaturesTransform

# Registry of all available transforms
registry = [
    LogicalBoxTransform,
    ColorMixTransform,
    FontFeaturesTransform,
]

def register(transform_class):
    """Decorator to register a new transform."""
    registry.append(transform_class)
    return transform_class

__all__ = ['registry', 'register'] 