# Transform to convert logical box properties to physical properties
# Fixes WeasyPrint compatibility issues with margin-block, padding-block

import re

class LogicalBoxTransform:
    """Converts logical box properties to physical equivalents."""
    
    # Properties that need transformation
    logical_props = {
        "margin-block": ["margin-top", "margin-bottom"],
        "margin-inline": ["margin-left", "margin-right"],
        "padding-block": ["padding-top", "padding-bottom"], 
        "padding-inline": ["padding-left", "padding-right"],
    }

    @staticmethod
    def should_apply(engine, caps):
        """Apply if engine doesn't support logical properties."""
        return not caps.get("logical-properties", False)

    @staticmethod 
    def run(ast, caps):
        """Transform logical properties to physical properties."""
        new_ast = {}
        
        for selector, decls in ast.items():
            new_decls = decls.copy()
            
            # Process each logical property
            for logical_prop, physical_props in LogicalBoxTransform.logical_props.items():
                if logical_prop in new_decls:
                    value = new_decls[logical_prop]
                    
                    # Parse the value (could be "0rem", "0.5rem 1rem", etc.)
                    values = value.strip().split()
                    
                    if len(values) == 1:
                        # Single value applies to both properties
                        new_decls[physical_props[0]] = values[0]
                        new_decls[physical_props[1]] = values[0]
                    elif len(values) == 2:
                        # Two values: first to start/top, second to end/bottom  
                        new_decls[physical_props[0]] = values[0]
                        new_decls[physical_props[1]] = values[1]
                    else:
                        # Fallback: use first value for both
                        new_decls[physical_props[0]] = values[0]
                        new_decls[physical_props[1]] = values[0]
                    
                    # Remove the logical property
                    del new_decls[logical_prop]
            
            new_ast[selector] = new_decls
        
        return new_ast 