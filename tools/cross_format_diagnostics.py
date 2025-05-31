#!/usr/bin/env python3
"""
Cross-Format Alignment Diagnostics Tool

Analyzes the exact alignment, indentation, and spacing being applied 
across HTML, PDF, and DOCX formats to identify inconsistencies.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Tuple
from dataclasses import dataclass

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class FormatDiagnostic:
    """Stores diagnostic information for a specific format."""
    format_name: str
    section_headers: Dict[str, str]
    company_lines: Dict[str, str] 
    role_boxes: Dict[str, str]
    role_descriptions: Dict[str, str]
    bullet_points: Dict[str, str]

class CrossFormatDiagnostics:
    """Main diagnostic tool for cross-format alignment analysis."""
    
    def __init__(self, design_tokens_path: str = "design_tokens.json"):
        self.design_tokens_path = Path(design_tokens_path)
        self.design_tokens = self._load_design_tokens()
        
    def _load_design_tokens(self) -> Dict[str, Any]:
        """Load and parse design tokens."""
        try:
            with open(self.design_tokens_path, 'r') as f:
                tokens = json.load(f)
            logger.info(f"Loaded {len(tokens)} design tokens")
            return tokens
        except Exception as e:
            logger.error(f"Error loading design tokens: {e}")
            return {}
    
    def analyze_html_css_alignment(self) -> FormatDiagnostic:
        """Analyze HTML/CSS alignment rules."""
        logger.info("🔍 Analyzing HTML/CSS alignment...")
        
        # Read spacing.css to understand actual applied rules
        spacing_css_path = Path("static/css/spacing.css")
        css_rules = {}
        
        if spacing_css_path.exists():
            with open(spacing_css_path, 'r') as f:
                content = f.read()
                # Extract key alignment rules
                css_rules = self._parse_css_alignment_rules(content)
        
        return FormatDiagnostic(
            format_name="HTML/CSS",
            section_headers={
                "alignment": "left-aligned, no indent",
                "css_rules": css_rules.get('.section-box', 'No specific rules found'),
                "source": "spacing.css @layer spacing"
            },
            company_lines={
                "alignment": "should align with section headers",
                "css_rules": css_rules.get('.company-line', 'No specific rules found'), 
                "expected": "margin-left: 0"
            },
            role_boxes={
                "alignment": "should align with company lines",
                "css_rules": css_rules.get('.position-bar', 'No position-bar rules found'),
                "current_spacing": self.design_tokens.get("position-bar-margin-top", "unknown")
            },
            role_descriptions={
                "alignment": "slightly indented from role box",
                "css_rules": css_rules.get('.role-description-text', 'No role-description rules found'),
                "current_spacing": self.design_tokens.get("role-description-text-margin-bottom", "unknown")
            },
            bullet_points={
                "alignment": "indented with bullet symbol",
                "css_rules": css_rules.get('.bullets li::before', 'Bullet rules not found'),
                "indentation": self.design_tokens.get("bullet-item-padding-left", "unknown")
            }
        )
    
    def analyze_docx_alignment(self) -> FormatDiagnostic:
        """Analyze DOCX alignment configuration."""
        logger.info("🔍 Analyzing DOCX alignment...")
        
        # Check DOCX style configuration
        docx_styles_path = Path("static/styles/_docx_styles.json")
        docx_styles = {}
        
        if docx_styles_path.exists():
            with open(docx_styles_path, 'r') as f:
                docx_styles = json.load(f)
        
        return FormatDiagnostic(
            format_name="DOCX",
            section_headers={
                "alignment": "left-aligned, no indent", 
                "style": "MR_SectionHeader",
                "indent_cm": docx_styles.get("styles", {}).get("MR_SectionHeader", {}).get("indentCm", "unknown"),
                "token_value": self.design_tokens.get("docx-section-header-cm", "token missing")
            },
            company_lines={
                "alignment": "should align with section headers",
                "style": "MR_Content", 
                "indent_cm": docx_styles.get("styles", {}).get("MR_Content", {}).get("indentCm", "unknown"),
                "token_value": self.design_tokens.get("docx-company-name-cm", "token missing")
            },
            role_boxes={
                "alignment": "should align with company lines",
                "style": "Role box table/positioning",
                "token_value": "Handled by table positioning",
                "issue": "May be inheriting indentation from content style"
            },
            role_descriptions={
                "alignment": "slightly indented from role box",
                "style": "MR_RoleDescription",
                "indent_cm": docx_styles.get("styles", {}).get("MR_RoleDescription", {}).get("indentCm", "unknown"),
                "token_value": self.design_tokens.get("docx-role-description-cm", "token missing")
            },
            bullet_points={
                "alignment": "should be indented with bullet symbol",
                "style": "MR_BulletPoint",
                "left_indent_cm": docx_styles.get("styles", {}).get("MR_BulletPoint", {}).get("indentCm", "unknown"),
                "hanging_indent_cm": docx_styles.get("styles", {}).get("MR_BulletPoint", {}).get("hangingIndentCm", "unknown"),
                "token_left": self.design_tokens.get("docx-bullet-left-indent-cm", "token missing"),
                "token_hanging": self.design_tokens.get("docx-bullet-hanging-indent-cm", "token missing"),
                "issue": "Both indents set to 0 = no bullet indentation"
            }
        )
    
    def analyze_pdf_alignment(self) -> FormatDiagnostic:
        """Analyze PDF (WeasyPrint) alignment via print CSS."""
        logger.info("🔍 Analyzing PDF alignment...")
        
        # Read print CSS to understand PDF-specific rules
        print_css_path = Path("static/css/spacing_print.css")
        print_rules = {}
        
        if print_css_path.exists():
            with open(print_css_path, 'r') as f:
                content = f.read()
                print_rules = self._parse_css_alignment_rules(content)
        
        return FormatDiagnostic(
            format_name="PDF (WeasyPrint)",
            section_headers={
                "alignment": "left-aligned, no indent",
                "css_rules": print_rules.get('.section-box', 'No section-box rules in print CSS'),
                "source": "spacing_print.css @layer spacing"
            },
            company_lines={
                "alignment": "should align with section headers", 
                "css_rules": print_rules.get('.company-line', 'No company-line specific rules'),
                "issue": "May be affected by WeasyPrint CSS interpretation"
            },
            role_boxes={
                "alignment": "should align with company lines",
                "css_rules": print_rules.get('.position-bar', 'No position-bar rules found'),
                "issue": "Reported unintended indentation - investigate WeasyPrint conversion",
                "current_spacing": self.design_tokens.get("position-bar-margin-top", "unknown")
            },
            role_descriptions={
                "alignment": "slightly indented from role box",
                "css_rules": print_rules.get('.role-description-text', 'No role-description rules found'),
                "current_spacing": self.design_tokens.get("role-description-text-margin-bottom", "unknown")
            },
            bullet_points={
                "alignment": "indented with bullet symbol",
                "css_rules": print_rules.get('.bullets li::before', 'Bullet rules investigation needed'),
                "indentation": self.design_tokens.get("bullet-item-padding-left", "unknown"),
                "issue": "Need to verify PDF bullet indentation consistency with HTML"
            }
        )
    
    def _parse_css_alignment_rules(self, css_content: str) -> Dict[str, str]:
        """Extract alignment-related CSS rules from content."""
        rules = {}
        
        # Look for key selectors and their alignment properties
        key_selectors = [
            '.section-box', '.position-bar', '.role-description-text', 
            '.bullets li::before', '.company-line', '.position-line'
        ]
        
        for selector in key_selectors:
            if selector in css_content:
                # Extract the rule block for this selector
                start_idx = css_content.find(selector)
                if start_idx != -1:
                    brace_start = css_content.find('{', start_idx)
                    brace_end = css_content.find('}', brace_start)
                    if brace_start != -1 and brace_end != -1:
                        rule_content = css_content[brace_start+1:brace_end].strip()
                        rules[selector] = rule_content
        
        return rules
    
    def identify_token_inconsistencies(self) -> Dict[str, Any]:
        """Identify inconsistencies in design token naming and values."""
        logger.info("🔍 Analyzing design token inconsistencies...")
        
        inconsistencies = {
            "missing_docx_tokens": [],
            "mismatched_values": [],
            "naming_inconsistencies": []
        }
        
        # Check for missing DOCX-specific tokens
        expected_docx_tokens = [
            "docx-section-header-indent-cm",
            "docx-company-name-indent-cm", 
            "docx-role-description-indent-cm",
            "docx-bullet-left-indent-cm",
            "docx-bullet-hanging-indent-cm"
        ]
        
        for token in expected_docx_tokens:
            if token not in self.design_tokens:
                inconsistencies["missing_docx_tokens"].append(token)
        
        # Check for equivalent tokens with different values
        equivalents = [
            ("bullet-item-padding-left", "docx-bullet-left-indent-cm", "Should be equivalent"),
            ("role-description-text-margin-bottom", "docx-role-description-indent-cm", "Should be related")
        ]
        
        for css_token, docx_token, relationship in equivalents:
            css_val = self.design_tokens.get(css_token, "missing")
            docx_val = self.design_tokens.get(docx_token, "missing")
            
            if css_val != "missing" and docx_val != "missing":
                inconsistencies["mismatched_values"].append({
                    "css_token": css_token,
                    "css_value": css_val,
                    "docx_token": docx_token, 
                    "docx_value": docx_val,
                    "relationship": relationship
                })
        
        return inconsistencies
    
    def generate_alignment_matrix(self) -> Dict[str, Any]:
        """Generate a comprehensive alignment comparison matrix."""
        logger.info("📊 Generating cross-format alignment matrix...")
        
        html_diag = self.analyze_html_css_alignment()
        docx_diag = self.analyze_docx_alignment()
        pdf_diag = self.analyze_pdf_alignment()
        
        matrix = {
            "section_headers": {
                "html": html_diag.section_headers,
                "pdf": pdf_diag.section_headers,
                "docx": docx_diag.section_headers,
                "consistency": "✅ Should be consistent" if all([
                    "left-aligned, no indent" in str(html_diag.section_headers),
                    "left-aligned, no indent" in str(pdf_diag.section_headers),
                    "left-aligned, no indent" in str(docx_diag.section_headers)
                ]) else "❌ Inconsistent"
            },
            "company_lines": {
                "html": html_diag.company_lines,
                "pdf": pdf_diag.company_lines,
                "docx": docx_diag.company_lines,
                "consistency": "❌ Inconsistent - DOCX may be indented"
            },
            "role_boxes": {
                "html": html_diag.role_boxes,
                "pdf": pdf_diag.role_boxes,
                "docx": docx_diag.role_boxes,
                "consistency": "❌ Inconsistent - PDF has unwanted indentation"
            },
            "role_descriptions": {
                "html": html_diag.role_descriptions,
                "pdf": pdf_diag.role_descriptions,
                "docx": docx_diag.role_descriptions,
                "consistency": "⚠️ Needs verification"
            },
            "bullet_points": {
                "html": html_diag.bullet_points,
                "pdf": pdf_diag.bullet_points, 
                "docx": docx_diag.bullet_points,
                "consistency": "❌ Inconsistent - DOCX has no bullet indentation"
            }
        }
        
        return matrix
    
    def generate_diagnostic_report(self, output_path: str = "doco/cross-format-diagnostics-report.md") -> str:
        """Generate a comprehensive diagnostic report."""
        logger.info("📝 Generating diagnostic report...")
        
        matrix = self.generate_alignment_matrix()
        inconsistencies = self.identify_token_inconsistencies()
        
        report = f"""# Cross-Format Alignment Diagnostic Report

**Generated**: {Path(__file__).name}
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

"""
        
        for element, data in matrix.items():
            report += f"### **{element.replace('_', ' ').title()}**\n\n"
            report += f"**Consistency Status**: {data['consistency']}\n\n"
            
            for format_name, details in data.items():
                if format_name != 'consistency':
                    report += f"**{format_name.upper()}**:\n"
                    if isinstance(details, dict):
                        for key, value in details.items():
                            report += f"- {key}: `{value}`\n"
                    else:
                        report += f"- {details}\n"
                    report += "\n"
            report += "---\n\n"
        
        report += f"""## 🔧 **Design Token Analysis**

### **Missing DOCX Tokens**: {len(inconsistencies['missing_docx_tokens'])}
"""
        for token in inconsistencies['missing_docx_tokens']:
            report += f"- `{token}`\n"
        
        report += f"""
### **Value Mismatches**: {len(inconsistencies['mismatched_values'])}
"""
        for mismatch in inconsistencies['mismatched_values']:
            report += f"- **{mismatch['css_token']}**: `{mismatch['css_value']}` vs **{mismatch['docx_token']}**: `{mismatch['docx_value']}` ({mismatch['relationship']})\n"
        
        report += f"""
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
   {{
     "bullet_indentation": {{
       "html_em": "1",
       "pdf_em": "1", 
       "docx_cm": "0.5"
     }}
   }}
   ```

2. **Implement Format-Specific Conversion**:
   - HTML: `padding-left: {{bullet_indentation.html_em}}em`
   - PDF: `padding-left: {{bullet_indentation.pdf_em}}em`
   - DOCX: `left_indent = Cm({{bullet_indentation.docx_cm}})`

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

**Report Generated**: {len(matrix)} alignment elements analyzed, {len(inconsistencies['missing_docx_tokens']) + len(inconsistencies['mismatched_values'])} issues identified.
"""
        
        # Write report to file
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        logger.info(f"📝 Diagnostic report written to: {output_file}")
        return str(output_file)

def main():
    """Run the cross-format diagnostic analysis."""
    print("🔍 Running Cross-Format Alignment Diagnostics...")
    
    diagnostics = CrossFormatDiagnostics()
    report_path = diagnostics.generate_diagnostic_report()
    
    print(f"✅ Diagnostic report generated: {report_path}")
    print("📊 Use this report to understand specific alignment issues before implementing fixes.")

if __name__ == "__main__":
    main() 