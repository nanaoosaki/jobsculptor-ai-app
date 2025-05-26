# Transform to handle font-feature-settings compatibility
# Strips or converts font-feature-settings based on engine support

class FontFeaturesTransform:
    """Handles font-feature-settings compatibility across engines."""
    
    @staticmethod
    def should_apply(engine, caps):
        """Apply if engine has special font-feature handling needs."""
        font_support = caps.get("font-feature-settings", True)
        return font_support == False or font_support == "xml"

    @staticmethod
    def run(ast, caps):
        """Transform font-feature-settings based on engine capabilities."""
        new_ast = {}
        
        for selector, decls in ast.items():
            new_decls = decls.copy()
            
            if "font-feature-settings" in new_decls:
                font_support = caps.get("font-feature-settings", True)
                
                if font_support == False:
                    # Engine doesn't support it, remove the property
                    del new_decls["font-feature-settings"]
                elif font_support == "xml":
                    # Word XML conversion - store value for XML processing but remove CSS
                    # The actual Word XML conversion will be handled by the style engine
                    new_decls["_word_font_features"] = new_decls["font-feature-settings"]
                    del new_decls["font-feature-settings"]
            
            new_ast[selector] = new_decls
        
        return new_ast 