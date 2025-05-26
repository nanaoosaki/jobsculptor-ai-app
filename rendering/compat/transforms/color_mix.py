# Transform to handle color-mix() compatibility
# Converts modern color-mix() functions to fallback colors

import re

class ColorMixTransform:
    """Converts color-mix() functions to fallback colors for unsupported engines."""
    
    @staticmethod
    def should_apply(engine, caps):
        """Apply if engine doesn't support color-mix."""
        return not caps.get("color-mix", False)

    @staticmethod
    def run(ast, caps):
        """Transform color-mix() functions to fallback colors."""
        new_ast = {}
        
        # Simple color-mix patterns and their fallbacks
        color_mix_patterns = {
            r'color-mix\(in sRGB, ([^,]+), ([^)]+)\)': r'\1',  # Use first color as fallback
            r'color-mix\([^)]+\)': '#333333',  # Generic fallback for complex color-mix
        }
        
        for selector, decls in ast.items():
            new_decls = {}
            
            for prop, value in decls.items():
                new_value = value
                
                # Check if value contains color-mix()
                for pattern, replacement in color_mix_patterns.items():
                    new_value = re.sub(pattern, replacement, new_value, flags=re.IGNORECASE)
                
                new_decls[prop] = new_value
            
            new_ast[selector] = new_decls
        
        return new_ast 