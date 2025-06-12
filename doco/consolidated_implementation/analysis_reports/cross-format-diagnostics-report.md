# Cross-Format Alignment Diagnostic Report

**Generated**: cross_format_diagnostics.py
**Purpose**: Detailed analysis of alignment inconsistencies across HTML, PDF, and DOCX formats

---

## 🎯 **Executive Summary**

Based on diagnostic analysis of the current system:

### **Critical Issues Identified**:
1. **DOCX Bullet Indentation**: Both `left_indent` and `hanging_indent` set to 0cm = no indentation
2. **PDF Role Box Alignment**: Unintended indentation breaking company line alignment  
3. **Design Token Gaps**: Missing format-specific tokens causing inconsistencies

### **Root Cause**: Single design tokens applied to different layout paradigms without format-specific adjustments.

---

## 📊 **Alignment Matrix Analysis**

### **Section Headers**

**Consistency Status**: ✅ Should be consistent

**HTML**:
- alignment: `left-aligned, no indent`
- css_rules: `margin-bottom: 0.5rem;
    border: 2px solid #4a6fdc;
    background: transparent;
    color: #4a6fdc;
    font-weight: 700;
    padding: 1px 12px;
    font-size: 12pt;
    line-height: 1.0;`
- source: `spacing.css @layer spacing`

**PDF**:
- alignment: `left-aligned, no indent`
- css_rules: `margin-bottom: 0.5rem;
    border: 2px solid #4a6fdc;
    background: transparent;
    color: #4a6fdc;
    font-weight: 700;
    padding: 1px 12px;
    font-size: 12pt;
    line-height: 1.0;`
- source: `spacing_print.css @layer spacing`

**DOCX**:
- alignment: `left-aligned, no indent`
- style: `MR_SectionHeader`
- indent_cm: `0.0`
- token_value: `0`

---

### **Company Lines**

**Consistency Status**: ❌ Inconsistent - DOCX may be indented

**HTML**:
- alignment: `should align with section headers`
- css_rules: `No specific rules found`
- expected: `margin-left: 0`

**PDF**:
- alignment: `should align with section headers`
- css_rules: `No company-line specific rules`
- issue: `May be affected by WeasyPrint CSS interpretation`

**DOCX**:
- alignment: `should align with section headers`
- style: `MR_Content`
- indent_cm: `0.0`
- token_value: `0`

---

### **Role Boxes**

**Consistency Status**: ❌ Inconsistent - PDF has unwanted indentation

**HTML**:
- alignment: `should align with company lines`
- css_rules: `margin-top: 0rem;
    margin-bottom: 0rem;
    background: #FFFFFF;
    padding: 0.25rem 0.45rem;`
- current_spacing: `0.1rem`

**PDF**:
- alignment: `should align with company lines`
- css_rules: `margin-top: 0rem;
    margin-bottom: 0rem;
    background: #FFFFFF;
    padding: 0.25rem 0.45rem;`
- issue: `Reported unintended indentation - investigate WeasyPrint conversion`
- current_spacing: `0.1rem`

**DOCX**:
- alignment: `should align with company lines`
- style: `Role box table/positioning`
- token_value: `Handled by table positioning`
- issue: `May be inheriting indentation from content style`

---

### **Role Descriptions**

**Consistency Status**: ⚠️ Needs verification

**HTML**:
- alignment: `slightly indented from role box`
- css_rules: `margin-top: 0rem;
    margin-bottom: 0rem;
    font-style: italic;
    color: #555;
    display: block;
    width: 100%;`
- current_spacing: `0.05rem`

**PDF**:
- alignment: `slightly indented from role box`
- css_rules: `margin-top: 0rem;
    margin-bottom: 0rem;
    font-style: italic;
    color: #555;
    display: block;
    width: 100%;`
- current_spacing: `0.05rem`

**DOCX**:
- alignment: `slightly indented from role box`
- style: `MR_RoleDescription`
- indent_cm: `0.0`
- token_value: `0`

---

### **Bullet Points**

**Consistency Status**: ❌ Inconsistent - DOCX has no bullet indentation

**HTML**:
- alignment: `indented with bullet symbol`
- css_rules: `content: "\2022 ";
    color: #3A3A3A;
    font-weight: normal;`
- indentation: `1em`

**PDF**:
- alignment: `indented with bullet symbol`
- css_rules: `content: "\2022 ";
    color: #3A3A3A;
    font-weight: normal;`
- indentation: `1em`
- issue: `Need to verify PDF bullet indentation consistency with HTML`

**DOCX**:
- alignment: `should be indented with bullet symbol`
- style: `MR_BulletPoint`
- left_indent_cm: `0.5`
- hanging_indent_cm: `0.5`
- token_left: `0.5`
- token_hanging: `0.5`
- issue: `Both indents set to 0 = no bullet indentation`

---

## 🔧 **Design Token Analysis**

### **Missing DOCX Tokens**: 3
- `docx-section-header-indent-cm`
- `docx-company-name-indent-cm`
- `docx-role-description-indent-cm`

### **Value Mismatches**: 1
- **bullet-item-padding-left**: `1em` vs **docx-bullet-left-indent-cm**: `0.5` (Should be equivalent)

---

## 🎯 **Specific Issues to Fix**

### **1. DOCX Bullet Indentation**
**Current State**:
```json
"docx-bullet-left-indent-cm": "0",
"docx-bullet-hanging-indent-cm": "0"
```

**CSS Equivalent**:
```json
"bullet-item-padding-left": "1em"
```

**Issue**: DOCX bullets have no indentation while HTML bullets are properly indented.

**Solution**: Set DOCX bullet tokens to create equivalent visual indentation:
```json
"docx-bullet-left-indent-cm": "0.5",
"docx-bullet-hanging-indent-cm": "0.5"
```

### **2. PDF Role Box Indentation**
**Issue**: Role/period boxes showing unintended indentation in PDF output.
**Investigation Needed**: Check WeasyPrint CSS interpretation of `@layer spacing` rules.

### **3. DOCX Company Line Alignment**
**Issue**: Company lines may be indented when they should align with section headers.
**Current Token**: `docx-company-name-cm: "0"`
**Verification Needed**: Confirm this token is being applied correctly.

---

## 🔬 **Investigation Recommendations**

### **Phase 1: Format-Specific Token Design**
1. **Create Format Namespace Structure**:
   ```json
   {
     "bullet_indentation": {
       "html_em": "1",
       "pdf_em": "1", 
       "docx_cm": "0.5"
     }
   }
   ```

2. **Implement Format-Specific Conversion**:
   - HTML: `padding-left: {bullet_indentation.html_em}em`
   - PDF: `padding-left: {bullet_indentation.pdf_em}em`
   - DOCX: `left_indent = Cm({bullet_indentation.docx_cm})`

### **Phase 2: Cross-Format Validation**
1. **Create Alignment Test Suite**: Generate sample outputs and verify pixel-perfect alignment
2. **Implement Automated Checks**: Validate that design token changes maintain cross-format consistency

---

## 🛠️ **Implementation Plan**

### **Step 1: Fix DOCX Bullet Indentation (Immediate)**
```bash
# Update design tokens
python tools/update_docx_bullet_tokens.py

# Regenerate DOCX styles  
python tools/regenerate_docx_styles.py

# Test output
python tools/test_cross_format_alignment.py
```

### **Step 2: Investigate PDF Issues (Next)**
```bash
# Generate PDF with debug output
python tools/debug_pdf_alignment.py

# Compare CSS rule application
python tools/analyze_weasyprint_conversion.py
```

### **Step 3: Implement Format-Specific Tokens (Future)**
```bash
# Migrate to format-specific token architecture
python tools/migrate_to_format_specific_tokens.py

# Validate cross-format consistency  
python tools/validate_format_alignment.py
```

---

## 📈 **Success Metrics**

### **Visual Consistency**:
- ✅ Company lines align with section headers across all formats
- ✅ Role/period boxes align with company lines across all formats
- ✅ Bullet indentation visually equivalent across all formats

### **Technical Quality**:
- ✅ Single source of truth for alignment concepts
- ✅ Format-specific implementation while maintaining logical consistency
- ✅ Automated validation prevents regression

---

**Report Generated**: 5 alignment elements analyzed, 4 issues identified.
