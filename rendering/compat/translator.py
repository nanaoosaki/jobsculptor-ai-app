# Main translator entry point
# Coordinates transforms and provides serialization

from .capability_tables import CAPABILITY, ENGINE_QUIRKS
from .transforms import registry

def translate(raw_rules: dict[str, dict[str, str]], engine: str) -> dict[str, dict[str, str]]:
    """
    Translate CSS rules based on target engine capabilities.
    
    Args:
        raw_rules: Dictionary of CSS selectors to declarations
        engine: Target engine ('browser', 'weasyprint', 'word')
        
    Returns:
        Translated CSS rules ready for serialization
    """
    if engine not in CAPABILITY:
        raise ValueError(f"Unknown engine: {engine}. Supported engines: {list(CAPABILITY.keys())}")
    
    caps = CAPABILITY[engine]
    quirks = ENGINE_QUIRKS.get(engine, {})
    
    # Start with raw rules
    ast = raw_rules.copy()
    
    # Apply each transform in sequence
    for transform_class in registry:
        if transform_class.should_apply(engine, caps):
            ast = transform_class.run(ast, caps)
    
    return ast

def to_css(ast: dict[str, dict[str, str]]) -> str:
    """
    Serialize CSS AST to CSS string.
    
    Args:
        ast: CSS rules as selector -> declarations dict
        
    Returns:
        CSS string ready for output
    """
    lines = []
    
    for selector, decls in ast.items():
        if not decls:  # Skip empty declaration blocks
            continue
            
        # Filter out internal properties (starting with _)
        css_decls = {k: v for k, v in decls.items() if not k.startswith('_')}
        
        if not css_decls:  # Skip if no CSS declarations after filtering
            continue
            
        # Format declarations
        body = "; ".join(f"{prop}: {value}" for prop, value in css_decls.items())
        
        # Add selector block
        lines.append(f"{selector} {{ {body}; }}")
    
    return "\n".join(lines)

def to_word_xml_data(ast: dict[str, dict[str, str]]) -> dict[str, dict[str, str]]:
    """
    Extract Word XML-specific data from translated CSS.
    
    Args:
        ast: Translated CSS rules
        
    Returns:
        Word XML data for style engine processing
    """
    word_data = {}
    
    for selector, decls in ast.items():
        # Extract internal Word-specific properties
        word_props = {k: v for k, v in decls.items() if k.startswith('_word_')}
        
        if word_props:
            word_data[selector] = word_props
    
    return word_data 