# Integration Guide: Translator Layer

## 🔗 **Hooking into Existing Systems**

This guide shows how to integrate the new translator layer into your existing HTML generator, PDF exporter, and DOCX style engine.

## 📝 **HTML Generator Integration**

### **Current Integration Point**
In `html_generator.py`, replace hardcoded CSS with translator-generated CSS:

```python
# OLD: Hardcoded CSS file inclusion
def generate_html_with_css():
    css_content = open('static/css/preview.css').read()
    return f"<style>{css_content}</style>"

# NEW: Dynamic CSS generation
from rendering.compat import translate, to_css
from static.css.raw_rules import RAW_RULES

def generate_html_with_css():
    # Generate browser-optimized CSS
    browser_ast = translate(RAW_RULES, "browser")
    css_content = to_css(browser_ast)
    return f"<style>{css_content}</style>"
```

### **Template Integration**
```python
def render_resume_template(resume_data):
    # Generate CSS for browser
    css_content = to_css(translate(RAW_RULES, "browser"))
    
    return render_template('resume.html', 
                         resume=resume_data,
                         css_content=css_content)
```

## 📄 **PDF Exporter Integration**

### **WeasyPrint Integration**
In `pdf_exporter.py`, use WeasyPrint-optimized CSS:

```python
# OLD: Static CSS file
def generate_pdf(html_content):
    css = CSS(filename='static/css/print.css')
    return HTML(string=html_content).write_pdf(stylesheets=[css])

# NEW: Dynamic WeasyPrint CSS
from rendering.compat import translate, to_css
from static.css.raw_rules import RAW_RULES

def generate_pdf(html_content):
    # Generate WeasyPrint-optimized CSS
    weasyprint_ast = translate(RAW_RULES, "weasyprint")
    css_content = to_css(weasyprint_ast)
    
    css = CSS(string=css_content)
    return HTML(string=html_content).write_pdf(stylesheets=[css])
```

### **CSS String Generation**
```python
def get_pdf_css():
    """Get CSS optimized for PDF generation."""
    weasyprint_ast = translate(RAW_RULES, "weasyprint")
    return to_css(weasyprint_ast)

def export_to_pdf(resume_data):
    html = render_resume_html(resume_data)
    css = get_pdf_css()
    
    # WeasyPrint with optimized CSS
    pdf_bytes = HTML(string=html).write_pdf(
        stylesheets=[CSS(string=css)]
    )
    return pdf_bytes
```

## 📋 **DOCX Style Engine Integration**

### **Word XML Data Extraction**
In `style_engine.py`, use Word-specific data:

```python
# NEW: Extract Word XML data from translator
from rendering.compat import translate, to_word_xml_data
from static.css.raw_rules import RAW_RULES

def apply_translator_styles(doc):
    """Apply styles from translator layer to DOCX document."""
    
    # Get Word-optimized CSS and XML data
    word_ast = translate(RAW_RULES, "word")
    word_xml_data = to_word_xml_data(word_ast)
    
    # Apply spacing from translated CSS
    for selector, decls in word_ast.items():
        if selector == ".role-description-text":
            # Apply zero margins from translator
            margin_top = decls.get("margin-top", "0rem")
            margin_bottom = decls.get("margin-bottom", "0rem")
            apply_paragraph_spacing(doc, margin_top, margin_bottom)
    
    return doc
```

### **Spacing Application**
```python
def apply_zero_spacing_from_tokens():
    """Apply zero spacing using translator layer."""
    
    # Get translated rules for Word
    word_ast = translate(RAW_RULES, "word")
    
    spacing_rules = {}
    for selector, decls in word_ast.items():
        if any(prop in decls for prop in ['margin-top', 'margin-bottom']):
            spacing_rules[selector] = {
                'margin_top': decls.get('margin-top', '0rem'),
                'margin_bottom': decls.get('margin-bottom', '0rem')
            }
    
    return spacing_rules
```

## 🔄 **Build Pipeline Integration**

### **Automated CSS Generation**
Create a build script that regenerates CSS when tokens change:

```python
# tools/build_all.py
def build_all_css():
    """Build CSS for all engines when tokens change."""
    
    print("Building CSS for all engines...")
    
    # Generate raw rules from tokens
    from tools.generate_raw_rules import generate_raw_rules_file
    generate_raw_rules_file()
    
    # Build engine-specific CSS
    from tools.build_css import build_css_for_engines
    build_css_for_engines()
    
    print("✓ All CSS files updated")

if __name__ == "__main__":
    build_all_css()
```

### **Development Workflow**
```bash
# When design tokens change:
python tools/build_all.py

# Or individual components:
python tools/generate_raw_rules.py  # Update raw rules
python tools/build_css.py          # Update CSS files
```

## 🧪 **Testing Integration**

### **CSS Validation Tests**
```python
# tests/test_translator_integration.py
def test_html_css_generation():
    """Test HTML CSS generation produces valid output."""
    browser_ast = translate(RAW_RULES, "browser")
    css = to_css(browser_ast)
    
    assert "margin-block: 0rem" in css  # Logical properties preserved
    assert css.count('{') == css.count('}')  # Valid CSS syntax

def test_pdf_css_generation():
    """Test PDF CSS generation converts logical properties."""
    weasyprint_ast = translate(RAW_RULES, "weasyprint")
    css = to_css(weasyprint_ast)
    
    assert "margin-top: 0rem" in css  # Physical properties
    assert "margin-block" not in css  # Logical properties converted

def test_docx_integration():
    """Test DOCX integration extracts correct spacing."""
    word_ast = translate(RAW_RULES, "word")
    
    # Check role description spacing
    role_desc = word_ast.get(".role-description-text", {})
    assert role_desc.get("margin-top") == "0rem"
    assert role_desc.get("margin-bottom") == "0rem"
```

## 🚀 **Production Deployment**

### **Feature Flag Approach**
```python
# config.py
USE_TRANSLATOR_LAYER = True  # Feature flag

# In your generators:
def get_css_content(engine):
    if USE_TRANSLATOR_LAYER:
        # New translator layer
        ast = translate(RAW_RULES, engine)
        return to_css(ast)
    else:
        # Legacy CSS files
        return open(f'static/css/{engine}.css').read()
```

### **Gradual Migration**
1. **Phase 1**: Deploy with feature flag OFF, validate translator output
2. **Phase 2**: Enable for staging environment, test all formats
3. **Phase 3**: Enable for production, monitor for issues
4. **Phase 4**: Remove legacy CSS files and feature flag

## 📊 **Monitoring & Validation**

### **CSS Output Validation**
```python
def validate_css_output():
    """Validate CSS output meets requirements."""
    
    engines = ['browser', 'weasyprint', 'word']
    
    for engine in engines:
        ast = translate(RAW_RULES, engine)
        css = to_css(ast)
        
        # Validate zero spacing
        assert "0rem" in css, f"{engine}: Missing zero spacing"
        
        # Validate engine-specific features
        if engine == "browser":
            assert "margin-block" in css, "Browser: Missing logical properties"
        else:
            assert "margin-top" in css, f"{engine}: Missing physical properties"
            assert "margin-block" not in css, f"{engine}: Logical properties not converted"
        
        print(f"✓ {engine} CSS validation passed")
```

## 🎯 **Quick Start Checklist**

- [ ] **Install translator layer**: Files already created in `rendering/compat/`
- [ ] **Generate raw rules**: `python tools/generate_raw_rules.py`
- [ ] **Build CSS files**: `python tools/build_css.py`
- [ ] **Test integration**: `python test_translator.py`
- [ ] **Update HTML generator**: Replace CSS inclusion with translator calls
- [ ] **Update PDF exporter**: Use WeasyPrint-optimized CSS
- [ ] **Update DOCX engine**: Extract spacing from Word AST
- [ ] **Add tests**: Validate CSS output for each engine
- [ ] **Deploy with feature flag**: Gradual rollout approach

## 🔧 **Troubleshooting**

### **Common Issues**

**CSS not updating**: Run `python tools/build_css.py` after token changes

**WeasyPrint warnings**: Check that logical properties are converted to physical

**DOCX spacing issues**: Verify Word AST contains physical properties

**Missing selectors**: Check that raw rules include all needed CSS selectors

### **Debug Commands**
```bash
# Test translator layer
python test_translator.py

# Validate spacing implementation  
python test_spacing_implementation.py

# Show integration examples
python tools/integrate_translator.py
```

---

**The translator layer is now ready for integration into your existing systems!** 🚀 