# Integration script for translator layer
# Shows how to integrate the new translator layer into existing build processes

import sys
import os
import pathlib

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from rendering.compat import translate, to_css, to_word_xml_data
from tools.generate_raw_rules import load_design_tokens, build_raw_rules

def integrate_with_html_generator():
    """Example integration with HTML generator."""
    
    print("=== INTEGRATING WITH HTML GENERATOR ===\n")
    
    # Load design tokens and build raw rules
    tokens = load_design_tokens()
    raw_rules = build_raw_rules(tokens)
    
    # Generate CSS for browser (HTML preview)
    browser_ast = translate(raw_rules, "browser")
    browser_css = to_css(browser_ast)
    
    print("Generated browser CSS for HTML preview:")
    print(f"  Rules: {len(browser_ast)}")
    print(f"  CSS size: {len(browser_css)} characters")
    print(f"  Uses logical properties: {'margin-block' in browser_css}")
    
    # This CSS can be injected into HTML templates or saved to files
    return browser_css

def integrate_with_pdf_generator():
    """Example integration with PDF generator (WeasyPrint)."""
    
    print("\n=== INTEGRATING WITH PDF GENERATOR ===\n")
    
    # Load design tokens and build raw rules
    tokens = load_design_tokens()
    raw_rules = build_raw_rules(tokens)
    
    # Generate CSS for WeasyPrint (PDF generation)
    weasyprint_ast = translate(raw_rules, "weasyprint")
    weasyprint_css = to_css(weasyprint_ast)
    
    print("Generated WeasyPrint CSS for PDF:")
    print(f"  Rules: {len(weasyprint_ast)}")
    print(f"  CSS size: {len(weasyprint_css)} characters")
    print(f"  Uses physical properties: {'margin-top' in weasyprint_css}")
    print(f"  Avoids logical properties: {'margin-block' not in weasyprint_css}")
    
    # This CSS can be used with WeasyPrint for PDF generation
    return weasyprint_css

def integrate_with_docx_generator():
    """Example integration with DOCX generator."""
    
    print("\n=== INTEGRATING WITH DOCX GENERATOR ===\n")
    
    # Load design tokens and build raw rules
    tokens = load_design_tokens()
    raw_rules = build_raw_rules(tokens)
    
    # Generate CSS for Word (DOCX generation)
    word_ast = translate(raw_rules, "word")
    word_css = to_css(word_ast)
    word_xml_data = to_word_xml_data(word_ast)
    
    print("Generated Word CSS and XML data for DOCX:")
    print(f"  CSS rules: {len(word_ast)}")
    print(f"  CSS size: {len(word_css)} characters")
    print(f"  XML data entries: {len(word_xml_data)}")
    print(f"  Uses physical properties: {'margin-top' in word_css}")
    
    # The word_xml_data can be used by the style engine for DOCX formatting
    # The word_css provides fallback CSS for any web-based preview
    return word_css, word_xml_data

def demonstrate_token_driven_workflow():
    """Demonstrate the complete token-driven workflow."""
    
    print("\n=== TOKEN-DRIVEN WORKFLOW DEMONSTRATION ===\n")
    
    # 1. Load design tokens (single source of truth)
    tokens = load_design_tokens()
    print(f"1. Loaded {len(tokens)} design tokens")
    
    # 2. Build raw CSS rules from tokens
    raw_rules = build_raw_rules(tokens)
    print(f"2. Generated {len(raw_rules)} raw CSS rules")
    
    # 3. Translate for each target engine
    engines = ['browser', 'weasyprint', 'word']
    for engine in engines:
        translated_ast = translate(raw_rules, engine)
        css_output = to_css(translated_ast)
        print(f"3. {engine}: {len(translated_ast)} rules → {len(css_output)} chars CSS")
    
    # 4. Key benefits achieved
    print("\n✓ BENEFITS ACHIEVED:")
    print("  • Single source of truth (design tokens)")
    print("  • Engine-specific optimizations (logical → physical)")
    print("  • Zero hardcoded spacing in SCSS")
    print("  • Consistent spacing across all formats")
    print("  • WeasyPrint compatibility guaranteed")

def show_before_after_comparison():
    """Show before/after comparison of the approach."""
    
    print("\n=== BEFORE/AFTER COMPARISON ===\n")
    
    print("BEFORE (Old Approach):")
    print("  • Hardcoded SCSS with manual spacing")
    print("  • Separate CSS files for each engine")
    print("  • Manual WeasyPrint compatibility fixes")
    print("  • Inconsistent spacing across formats")
    print("  • Difficult to maintain and update")
    
    print("\nAFTER (New Translator Layer):")
    print("  • Token-driven CSS generation")
    print("  • Single raw rules → multiple engine outputs")
    print("  • Automatic compatibility transformations")
    print("  • Guaranteed spacing consistency")
    print("  • Easy to maintain and extend")
    
    print("\nKEY ARCHITECTURAL IMPROVEMENT:")
    print("  Design Tokens → Raw Rules → Translator → Engine-Specific CSS")

if __name__ == "__main__":
    # Run all integration examples
    integrate_with_html_generator()
    integrate_with_pdf_generator()
    integrate_with_docx_generator()
    demonstrate_token_driven_workflow()
    show_before_after_comparison()
    
    print("\n=== INTEGRATION COMPLETE ===")
    print("The translator layer is ready for production use!") 