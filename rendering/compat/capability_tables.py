# Capability tables defining what each rendering engine supports
# Used by transforms to determine when to apply compatibility fixes
# Adapted for manusResume6 project specific requirements

CAPABILITY = {
    "browser": {
        # Modern logical properties support
        "margin-block": True,
        "padding-block": True,
        "margin-inline": True,
        "padding-inline": True,
        
        # Advanced CSS features
        "color-mix": True,
        "font-feature-settings": True,
        "logical-properties": True,
        "css-grid": True,
        "flexbox": True,
        "calc": True,
        
        # Project-specific features
        "container-queries": True,
        "viewport-units": True,
        "css-variables": True,
        "transforms": True,
        "animations": True,
        
        # Resume-specific layout
        "role-box-layout": True,
        "section-spacing": True,
        "bullet-list-hanging": True,
    },
    
    "weasyprint": {
        # WeasyPrint limitations (as of v60-62)
        "margin-block": False,     # Must convert to physical properties
        "padding-block": False,
        "margin-inline": False,
        "padding-inline": False,
        "logical-properties": False,
        
        # Limited modern features
        "color-mix": False,        
        "font-feature-settings": False,  
        "container-queries": False,
        "viewport-units": "limited",  # Some support but quirky
        
        # Supported features
        "css-grid": True,          # Good support in newer versions
        "flexbox": True,
        "calc": "quirky",          # Supported but has edge cases
        "css-variables": True,
        "transforms": "limited",   # Basic transform support
        "animations": False,       # No animation in PDF
        
        # PDF-specific features
        "page-break": True,
        "orphans-widows": True,
        "pdf-bookmarks": True,
        
        # Resume-specific adaptations
        "role-box-layout": "adapted",      # Needs special handling
        "section-spacing": "physical",     # Must use top/bottom margins
        "bullet-list-hanging": "manual",   # Manual text-indent required
    },
    
    "word": {
        # No CSS support - everything converts to Word XML
        "margin-block": False,     
        "padding-block": False,
        "margin-inline": False,
        "padding-inline": False,
        "logical-properties": False,
        
        # No modern CSS features
        "color-mix": False,        
        "font-feature-settings": "xml",  # Converted to Word XML font features
        "css-grid": False,         
        "flexbox": False,
        "calc": False,             
        "css-variables": False,
        "transforms": False,
        "animations": False,
        "container-queries": False,
        "viewport-units": False,
        
        # Word XML features
        "paragraph-spacing": True,     # Word paragraph spacing
        "numbering-xml": True,         # List numbering support
        "table-layout": True,          # Word table support
        "style-inheritance": True,     # Word style inheritance
        "twips-precision": True,       # 1/20 point precision
        
        # Resume-specific Word features
        "role-box-layout": "word-table",   # Convert to Word table layout
        "section-spacing": "paragraph",    # Use paragraph spacing
        "bullet-list-hanging": "numbering", # Word numbering XML
        "docx-borders": True,              # Native Word borders
        "docx-shading": True,              # Background colors via shading
    },
}

# Engine-specific quirks and workarounds
# Extended with project-specific requirements
ENGINE_QUIRKS = {
    "weasyprint": {
        # Core PDF generation quirks
        "force_physical_properties": True,
        "avoid_zero_calc": True,      # calc(0 * 1px) sometimes fails
        "prefer_longhand": True,      # Shorthand properties can be inconsistent
        "explicit_font_sizes": True,  # Always specify font-size in pt/px
        
        # PDF layout quirks
        "page_break_control": True,   # Careful page break handling
        "table_layout_fixed": True,   # Use table-layout: fixed for stability
        "avoid_flexbox_grow": True,   # flex-grow can cause layout issues
        
        # Resume-specific PDF quirks
        "role_description_spacing": "margin-top",  # Use margin-top, not margin-block
        "bullet_list_reset": True,    # Reset default ul/li spacing
        "section_border_timing": True, # Apply borders after content
        "font_fallback_required": True, # Always provide font fallbacks
        
        # WeasyPrint reset requirements (o3 recommendation)
        "user_agent_reset": True,     # Need explicit UA style reset
        "list_style_reset": True,     # Reset default list styles
    },
    
    "word": {
        # Core Word XML requirements
        "xml_conversion": True,
        "twips_conversion": True,     # Convert to twips (1/20 point)
        "font_to_xml": True,
        "paragraph_properties": True, # Use Word paragraph properties
        
        # Word layout quirks
        "table_cell_spacing": True,   # Handle cell spacing in tables
        "numbering_definition": True, # Complex list numbering setup
        "style_inheritance": True,    # Word style inheritance rules
        "border_precedence": True,    # Border precedence in Word
        
        # Resume-specific Word quirks
        "role_box_as_table": True,    # Convert role boxes to Word tables
        "section_header_styling": True, # Special section header handling
        "bullet_list_numbering": True,  # Use Word numbering for bullets
        "hanging_indent_manual": True,  # Manual hanging indent setup
        
        # Word XML edge cases (o3 identified)
        "list_spacing_xml": True,     # List spacing in numbering XML
        "paragraph_spacing_twips": True, # Paragraph spacing in twips
        "border_width_conversion": True, # Border width pt to twips
    },
    
    "browser": {
        # Modern browser capabilities
        "modern_features": True,
        "logical_properties": True,
        "css_grid_advanced": True,
        "flexbox_gap": True,          # gap property in flexbox
        "css_variables_everywhere": True,
        
        # Resume-specific browser features
        "responsive_design": True,    # Full responsive capability
        "print_media_queries": True,  # @media print support
        "container_queries": True,    # Future-ready layout
        "custom_properties": True,    # CSS custom properties
        
        # Performance optimizations
        "css_containment": True,      # CSS containment for performance
        "will_change": True,          # will-change optimization hints
        "transform_layers": True,     # Hardware acceleration
    }
}

# Project-specific selector mappings
# Maps design token selectors to CSS selectors
SELECTOR_MAPPING = {
    "role-description": ".role-description-text",
    "role-box": ".role-box", 
    "section-header": ".section-header",
    "position-bar": ".position-bar", 
    "job-content": ".job-content",
    "role-list": ".role-list, .role-description ul",
    "bullet-item": ".role-description li",
    "section-box": ".section-box",
    "contact-divider": ".contact-divider",
}

# Engine output format requirements
OUTPUT_FORMATS = {
    "browser": {
        "file_extension": ".css",
        "charset": "utf-8",
        "minify": False,  # Keep readable for development
        "source_maps": True,
    },
    "weasyprint": {
        "file_extension": ".css", 
        "charset": "utf-8",
        "minify": True,   # Minimize for PDF generation
        "source_maps": False,
        "reset_required": True,  # Include UA reset
    },
    "word": {
        "file_extension": ".json",  # Word XML data as JSON
        "charset": "utf-8", 
        "minify": False,
        "source_maps": False,
        "include_twips": True,  # Include twips conversions
    }
} 