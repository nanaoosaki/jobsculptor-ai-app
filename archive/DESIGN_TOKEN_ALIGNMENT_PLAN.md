# Design Token Alignment Implementation Plan

## Strategy Overview

**Goal**: Preserve existing hardcoded styling (which works well) by moving those values into design tokens, then refactor code to use the centralized tokens instead of hardcoded values.

**Approach**: One-by-one implementation with testing between each step to ensure no visual regressions.

**Principle**: Hardcoded values → Design tokens → Code refactoring → Testing → Next item

---

## 📋 Implementation Sequence

### **Step 1: Role Description Spacing** 
**Priority**: Critical (Active override)  
**Files**: `design_tokens.json`, `utils/docx_builder.py`

#### Current State
```python
# utils/docx_builder.py - Line 739-740
role_para.paragraph_format.space_before = Pt(6)   # HARDCODED
role_para.paragraph_format.space_after = Pt(0)    # HARDCODED
```
```json
// design_tokens.json - Current
"paragraph-spacing-roledesc-before": "0",
"paragraph-spacing-roledesc-after": "0"
```

#### Step 1a: Update Design Tokens
```json
// design_tokens.json - Update to match hardcoded values
"paragraph-spacing-roledesc-before": "6",  // Change from "0" to "6"
"paragraph-spacing-roledesc-after": "0"    // Keep as "0"
```

#### Step 1b: Regenerate Style Files
```bash
python tools/generate_tokens.py
```

#### Step 1c: Update Code to Use Design Tokens
```python
# utils/docx_builder.py - Replace hardcoded values
def add_role_description(doc, text, docx_styles):
    if not text:
        return None
    
    role_para = doc.add_paragraph(text, style='MR_RoleDescription')
    
    # USE DESIGN TOKENS instead of hardcoded values
    if docx_styles and 'MR_RoleDescription' in docx_styles:
        # Get spacing from the style configuration (which comes from design tokens)
        style_config = docx_styles['MR_RoleDescription']
        space_before = style_config.get('spaceBeforePt', 0)
        space_after = style_config.get('spaceAfterPt', 0)
        
        role_para.paragraph_format.space_before = Pt(space_before)
        role_para.paragraph_format.space_after = Pt(space_after)
        
        logger.info(f"Applied design token spacing: before={space_before}pt, after={space_after}pt")
    else:
        # Fallback to design tokens directly if style config not available
        from style_engine import StyleEngine
        design_tokens = StyleEngine.load_tokens()
        space_before = int(design_tokens.get("paragraph-spacing-roledesc-before", "0"))
        space_after = int(design_tokens.get("paragraph-spacing-roledesc-after", "0"))
        
        role_para.paragraph_format.space_before = Pt(space_before)
        role_para.paragraph_format.space_after = Pt(space_after)
    
    logger.info(f"Applied MR_RoleDescription with design token spacing to: {str(text)[:30]}...")
    return role_para
```

#### Step 1d: Testing Checklist
- [ ] Generate a test resume with role descriptions
- [ ] Verify role descriptions have 6pt spacing before (same as before)
- [ ] Verify role descriptions have 0pt spacing after
- [ ] Confirm no visual changes from previous behavior
- [ ] Test with different design token values to verify centralized control works

---

### **Step 2: Bullet Point XML Indentation**
**Priority**: Critical (XML hardcodes)  
**Files**: `design_tokens.json`, `word_styles/numbering_engine.py`

#### Current State
```python
# word_styles/numbering_engine.py - Lines 298-299
left_indent = "331"    # ~0.23" for table compatibility (HARDCODED TWIPS)
hanging_indent = "187" # ~0.13" hanging indent (HARDCODED TWIPS)
```
```json
// design_tokens.json - Current
"docx-bullet-left-indent-cm": "0.33",
"docx-bullet-hanging-indent-cm": "0.33"
```

#### Step 2a: Calculate Current Values in CM
```
331 twips ÷ 567 twips/cm = 0.584 cm
187 twips ÷ 567 twips/cm = 0.330 cm
```

#### Step 2b: Update Design Tokens to Match
```json
// design_tokens.json - Update to match actual hardcoded values
"docx-bullet-left-indent-cm": "0.584",     // Was "0.33", now matches 331 twips
"docx-bullet-hanging-indent-cm": "0.330"   // Was "0.33", now matches 187 twips
```

#### Step 2c: Update Code to Use Design Tokens
```python
# word_styles/numbering_engine.py - Replace hardcoded values
def get_or_create_numbering_definition(self, doc: Document, num_id: int = 100, abstract_num_id: Optional[int] = None) -> bool:
    # ... existing code ...
    
    # B2: Use design tokens instead of hardcoded values
    from style_engine import StyleEngine
    design_tokens = StyleEngine.load_tokens()
    
    # Convert design token cm values to twips for XML
    left_indent_cm = float(design_tokens.get("docx-bullet-left-indent-cm", "0.584"))
    hanging_indent_cm = float(design_tokens.get("docx-bullet-hanging-indent-cm", "0.330"))
    
    left_indent = str(self.cm_to_twips(left_indent_cm))
    hanging_indent = str(self.cm_to_twips(hanging_indent_cm))
    
    logger.info(f"Using design token bullet indentation: left={left_indent_cm}cm ({left_indent} twips), hanging={hanging_indent_cm}cm ({hanging_indent} twips)")
    
    # ... rest of XML creation using calculated values ...
```

#### Step 2d: Testing Checklist
- [ ] Generate a test resume with bullet points
- [ ] Verify bullet indentation matches previous behavior exactly
- [ ] Test that changing design token values affects bullet indentation
- [ ] Confirm bullet alignment works in different contexts

---

### **Step 3: Resume Styler Color Alignment**
**Priority**: High (Color inconsistency)  
**Files**: `design_tokens.json`, `resume_styler.py`

#### Current State
```python
# resume_styler.py - Lines 68, 184
font.color.rgb = RGBColor(0, 0, 102)  # Dark blue - HARDCODED
```
```json
// design_tokens.json - Current
"color-primary-blue": "#1F497D"
```

#### Step 3a: Convert RGB to Hex
```
RGBColor(0, 0, 102) = #000066
```

#### Step 3b: Update Design Token
```json
// design_tokens.json - Update to match hardcoded color
"color-primary-blue": "#000066"  // Was "#1F497D", now matches RGBColor(0,0,102)
```

#### Step 3c: Update Code to Use Design Token
```python
# resume_styler.py - Replace hardcoded color
from style_engine import StyleEngine

def _create_styles(self):
    design_tokens = StyleEngine.load_tokens()
    primary_blue_hex = design_tokens.get("color-primary-blue", "#000066")
    primary_blue_rgb = StyleEngine.hex_to_rgb(primary_blue_hex)
    
    # Section header style
    header_style = self.document.styles.add_style('SectionHeader', WD_STYLE_TYPE.PARAGRAPH)
    # ... other properties ...
    font.color.rgb = RGBColor(*primary_blue_rgb)  # Use design token color
```

#### Step 3d: Testing Checklist
- [ ] Generate test resume with section headers
- [ ] Verify section header color matches previous dark blue exactly
- [ ] Test changing design token color affects section headers
- [ ] Check color consistency across all text elements

---

### **Step 4: Resume Styler Spacing Values**
**Priority**: Medium (Multiple spacing hardcodes)  
**Files**: `design_tokens.json`, `resume_styler.py`

#### Current State Analysis
```python
# resume_styler.py - Current hardcoded values
contact_style.paragraph_format.space_after = Pt(6)    # Line 60
header_style.paragraph_format.space_after = Pt(6)     # Line 70  
bullet_style.paragraph_format.space_after = Pt(4)     # Line 82
role_style.paragraph_format.space_after = Pt(3)       # Line 90
date_style.paragraph_format.space_after = Pt(4)       # Line 98
```

#### Step 4a: Update Design Tokens
```json
// design_tokens.json - Add missing tokens or update existing ones
"paragraph-spacing-contact-after": "6",
"paragraph-spacing-section-after": "6", 
"paragraph-spacing-bullet-after": "4",
"paragraph-spacing-role-after": "3",
"paragraph-spacing-date-after": "4"
```

#### Step 4b: Update Code Implementation
```python
# resume_styler.py - Use design tokens for all spacing
def _create_styles(self):
    design_tokens = StyleEngine.load_tokens()
    
    # Contact style
    contact_style = self.document.styles.add_style('Contact', WD_STYLE_TYPE.PARAGRAPH)
    contact_after = int(design_tokens.get("paragraph-spacing-contact-after", "6"))
    contact_style.paragraph_format.space_after = Pt(contact_after)
    
    # Header style  
    header_style = self.document.styles.add_style('SectionHeader', WD_STYLE_TYPE.PARAGRAPH)
    header_after = int(design_tokens.get("paragraph-spacing-section-after", "6"))
    header_style.paragraph_format.space_after = Pt(header_after)
    
    # Bullet style
    bullet_style = self.document.styles.add_style('BulletPoint', WD_STYLE_TYPE.PARAGRAPH)
    bullet_after = int(design_tokens.get("paragraph-spacing-bullet-after", "4"))
    bullet_style.paragraph_format.space_after = Pt(bullet_after)
    
    # Role style
    role_style = self.document.styles.add_style('CompanyRole', WD_STYLE_TYPE.PARAGRAPH)
    role_after = int(design_tokens.get("paragraph-spacing-role-after", "3"))
    role_style.paragraph_format.space_after = Pt(role_after)
    
    # Date style
    date_style = self.document.styles.add_style('DateRange', WD_STYLE_TYPE.PARAGRAPH)
    date_after = int(design_tokens.get("paragraph-spacing-date-after", "4"))
    date_style.paragraph_format.space_after = Pt(date_after)
```

---

## 🔄 Testing Protocol

After each step:
1. **Generate Test Resume**: Use a real user resume with multiple sections
2. **Visual Comparison**: Compare before/after screenshots  
3. **Design Token Test**: Temporarily change the design token value and verify it affects output
4. **Rollback Verification**: Restore original design token value and confirm it returns to baseline
5. **Multi-Section Test**: Ensure the change works across different resume sections

## 📋 Implementation Checklist

### Ready for Step 1 (Role Description Spacing)
- [ ] Update `design_tokens.json`: `"paragraph-spacing-roledesc-before": "6"`
- [ ] Run `python tools/generate_tokens.py`
- [ ] Update `utils/docx_builder.py` to use design tokens
- [ ] Test with user resume
- [ ] Verify no visual changes
- [ ] Confirm centralized control works

**Ready to proceed with Step 1?** Let me know when you'd like to start, and I'll implement the first change for testing. 