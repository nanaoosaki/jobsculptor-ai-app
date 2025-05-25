# Known Issues

Current issues with the resume application as of latest role box implementation.

## Current Active Issues

### 1. Missing Contact Information Section
**Status**: ✅ **RESOLVED**  
**Priority**: ~~High~~ → Completed

**Description**: 
The DOCX output was missing the contact information section that should appear directly below the name header. This included phone, email, location, and other contact details.

**Root Cause Analysis**:
The issue was in the contact parsing logic in `utils/docx_builder.py`. The contact data was successfully loaded from JSON files with this structure:
```json
{
  "content": "John (Jo) Doe\n\n☎  123.456.7890 ✉ john.doe@email.com  github.com/jodo"
}
```

The DOCX builder's contact parsing logic had several bugs:

1. **Empty Line Handling**: The logic split by `\n` but didn't handle empty lines (`\n\n`) properly
2. **Separator Mismatch**: The parser looked for `|` separators but the actual format used spaces and Unicode symbols (`☎`, `✉`)
3. **Symbol Recognition**: The parser didn't recognize Unicode contact symbols used in the data
4. **Parsing Logic Gap**: The contact detail extraction failed because it expected pipe-separated values but got space-separated values with symbols

**✅ Implementation Completed**:

**Phase 1: Fixed Contact String Parsing** ✅
- ✅ Updated contact parsing logic in `utils/docx_builder.py` lines ~515-540
- ✅ Added `parse_contact_string()` helper function
- ✅ Handle empty lines by filtering out empty strings after split
- ✅ Improved contact detail extraction to handle space-separated format with Unicode symbols
- ✅ Added regex patterns to identify phone numbers, emails, and URLs more reliably

**Phase 2: Added Robust Contact Field Detection** ✅
- ✅ Created helper function to parse contact strings with multiple format support
- ✅ Added detection for Unicode symbols: `☎`, `✉`, etc.
- ✅ Handle both pipe-separated and space-separated contact formats
- ✅ Added fallback parsing for unstructured contact text

**Phase 3: Testing & Validation** ✅
- ✅ Tested with current contact data format
- ✅ Verified contact section appears in DOCX output
- ✅ Confirmed proper formatting and alignment
- ✅ Validated against HTML/PDF output for consistency

**Technical Implementation Details**:
- **File**: `utils/docx_builder.py`
- **Function**: `parse_contact_string()` (new helper function) + `build_docx()` contact section
- **Key Changes Applied**: 
  - ✅ Added regex-based parsing: `re.split(r'\s{2,}|(?<=\S)\s+(?=[☎✉📧📞🌐])|(?<=[☎✉📧📞🌐])\s+', line)`
  - ✅ Added Unicode symbol detection and removal: `re.sub(r'[☎✉📧📞🌐]', '', part)`
  - ✅ Filter empty strings: `[line for line in lines if line.strip()]`
  - ✅ Improved email/phone/URL regex patterns with validation
  - ✅ Enhanced field detection for location, GitHub, LinkedIn, etc.

**Result**: 
✅ Contact information now appears correctly in DOCX output, including name, phone, email, and other contact details properly parsed from the Unicode symbol format. The section is formatted consistently with HTML/PDF outputs.

**Logs Evidence of Success**:
```
INFO:utils.docx_builder:Extracted name: John (Jo) Doe
INFO:utils.docx_builder:Processing contact line: ☎  123.456.7890 ✉ john.doe@email.com  github.com/jodo
INFO:utils.docx_builder:Found email: john.doe@email.com
INFO:utils.docx_builder:Found phone: 123.456.7890
INFO:utils.docx_builder:Found GitHub: github.com/jodo
```

---

### 2. Font Size Inconsistencies Across Formats
**Status**: Unresolved  
**Priority**: High

**Description**: 
Font sizes for various resume elements (section headers, body text, role titles, role descriptions, bullet points) are not consistent between HTML/PDF and DOCX formats. The formats appear to be using different font sizing systems instead of sharing a single source of truth through `design_tokens.json`.

**Current Evidence**:
- Section headers appear different sizes in HTML/PDF vs DOCX
- Role titles and descriptions have inconsistent sizing across formats
- Bullet point text sizing varies between formats
- Overall visual hierarchy is inconsistent

**Root Cause**: 
Suspected that HTML/PDF and DOCX are using different font sizing mechanisms rather than both referencing `design_tokens.json` as the single source of truth.

**Expected Behavior**: 
All formats should reference the same font size tokens from `design_tokens.json` to ensure identical appearance across HTML, PDF, and DOCX outputs.

---

### 3. Missing Background Fill in Role Boxes (Cross-Format)
**Status**: Unresolved  
**Priority**: High

**Description**: 
Role boxes in both HTML/PDF and DOCX formats are displaying with borders but no background color/fill. This affects visual hierarchy and professional appearance across all output formats.

**Current State**: 
- Role boxes have borders in all formats ✅
- Role boxes missing background fill in HTML/PDF ❌
- Role boxes missing background fill in DOCX ❌

**Design Token Available**:
```json
"roleBox": {
  "backgroundColor": "transparent",
  "docx": {
    "backgroundColor": "#F8F9FA"
  }
}
```

**Impact**: 
- Reduced visual impact and hierarchy across all formats
- Less distinction between role information and other content
- Inconsistent with modern resume design patterns
- Professional appearance suffers

**Expected Behavior**: 
Role boxes should have a subtle background fill color (light blue/gray) in all formats to provide visual separation and emphasis.

---

### 4. Font Style Inconsistencies Across Formats  
**Status**: Unresolved
**Priority**: High

**Description**: 
Font styles (family, weight, formatting) are inconsistent across HTML/PDF and DOCX formats. Different elements appear to use different font families or styling approaches rather than a unified font system.

**Observed Issues**:
- Font families may differ between HTML/PDF and DOCX
- Bold/italic styling inconsistencies 
- Font weight variations across formats
- Overall typography appears "all over the place"

**Impact**: 
- Unprofessional and inconsistent brand presentation
- Users receive different-looking documents depending on format
- Reduces trust and perceived quality
- Makes formats appear to be from different applications

**Expected Behavior**: 
All formats should use identical font families, weights, and styling as defined in `design_tokens.json` to ensure consistent typography across all exports.

---

### 5. Download Button Format Options Issue
**Status**: Unresolved  
**Priority**: Medium

**Description**: 
The current interface allows both DOCX and PDF download options simultaneously, which may need to be reconsidered based on user experience requirements.

**Current State**: 
- Both "Download PDF" and "Download DOCX" buttons are available
- Users can download in either format

**Impact**: 
- Potential user confusion about which format to choose
- May not align with intended user workflow
- Interface complexity may be unnecessary

**Expected Behavior**: 
Clarification needed on whether both formats should remain available or if the interface should be simplified to focus on a single primary format.

---

### 6. Download Button Styling Issues
**Status**: Unresolved  
**Priority**: Medium

**Description**: 
The download button styling is not user-friendly and lacks consistent visual feedback states.

**Current Issues**:
- Button color choice is "not user-friendly to the eyes"
- Default button state does not match expected modern UI patterns
- Inconsistent styling between PDF and DOCX download buttons

**Expected Behavior**: 
- **Default State**: White text + blue background (like current hover state)
- **Click/Active State**: Darker blue background for feedback
- **Consistent Behavior**: All download buttons should follow the same styling pattern (similar to how PDF download button currently behaves)

**Impact**: 
- Poor user experience and visual appeal
- Inconsistent interface behavior
- May reduce user confidence in the application

---

### 7. Empty Projects Section Added When No Projects Exist
**Status**: Unresolved  
**Priority**: Medium

**Description**: 
The DOCX builder is creating a "PROJECTS" section header even when the resume contains no project data or only empty project content.

**Evidence from Logs**:
```
INFO:utils.docx_builder:Projects content is a string, adding as single project
INFO:word_styles.section_builder:Added table section header: PROJECTS with style BoxedHeading2Table
```

**Impact**: 
- Creates empty or near-empty sections in the resume
- Reduces document professionalism
- Wastes valuable resume space

**Expected Behavior**: 
Projects section should only be added if there is actual project content to display.

---

### 8. Role Box Padding Too Tight (DOCX)
**Status**: Unresolved  
**Priority**: Medium

**Description**: 
The role boxes (containing job titles and dates) have insufficient padding in DOCX format, making the text appear cramped against the box borders.

**Current Implementation**:
```python
cell_margins = {
    'top': 5,      # Too small
    'left': 15,    # Too small  
    'bottom': 15,
    'right': 15
}
```

**Impact**: 
- Poor visual appearance and readability in DOCX
- Text appears cramped and unprofessional
- Inconsistent with typical document formatting standards

**Suggested Fix**: 
Increase padding values to provide more breathing room around the text.

---

### 9. Missing Indentation for Role Content
**Status**: Unresolved  
**Priority**: Low

**Description**: 
The role description text and bullet points under each role box are flush with the left margin, lacking the subtle indentation that would improve visual hierarchy and readability.

**Impact**: 
- Reduced visual hierarchy between role titles and role content
- Less professional document formatting
- Harder to distinguish between different content levels

**Expected Behavior**: 
- Role descriptions should have a small left indent (e.g., 0.25" or 0.5")
- Bullet points should have consistent hanging indent formatting
- This would create clear visual separation between role headers and role content

---

## Implementation Priority

**Critical (High Priority)**:
1. Missing Contact Information Section
2. Font Size Inconsistencies Across Formats  
3. Missing Background Fill in Role Boxes (Cross-Format)
4. Font Style Inconsistencies Across Formats

**Important (Medium Priority)**:
5. Download Button Format Options Issue
6. Download Button Styling Issues
7. Empty Projects Section Logic
8. Role Box Padding Adjustment (DOCX)

**Future Enhancement (Low Priority)**:
9. Role Content Indentation

---

## Technical Notes

**Design Token Integration**: 
- Primary token file: `design_tokens.json`
- Ensure all formats reference the same tokens for fonts, colors, spacing
- Investigate current token usage in HTML/PDF vs DOCX implementations

**Cross-Format Consistency Locations**: 
- HTML generation: Check font size and background color application
- PDF generation: Verify design token usage in styling
- DOCX generation: `word_styles/section_builder.py` → `add_role_box()`
- Token processing: Verify CSS and DOCX builders use same source

**UI/UX Locations**:
- Download button functionality: Frontend JavaScript and template files
- Button styling: CSS files in `static/css/` directory
- Interface templates: HTML template files

**Testing Approach**:
- Generate same resume in all three formats (HTML, PDF, DOCX)
- Visual comparison for font sizes, styles, and colors
- Verify `design_tokens.json` is single source of truth
- Test button interactions and visual feedback states
- Check each issue independently before marking as resolved 