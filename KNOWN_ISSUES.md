# KNOWN ISSUES

Current issues with the resume application as of latest optimizations.

## RESOLVED ✅

### 1. **Missing Contact Information Section** ✅ **RESOLVED**
**Status**: Fixed in contact parsing logic  
**Description**: The DOCX output was missing the contact information section that should appear directly below the name header. This included phone, email, location, and other contact details.
**Solution**: Updated contact parsing logic in `utils/docx_builder.py` lines ~515-540
**Result**: Contact information now appears correctly in DOCX output, including name, phone, email, and other contact details properly parsed from the Unicode symbol format. The section is formatted consistently with HTML/PDF outputs.

### 2. **Font Size Inconsistencies Across Formats** ✅ **RESOLVED**
**Status**: Fixed via Universal Rendering System  
**Description**: Font sizes for various resume elements were not consistent between HTML/PDF and DOCX formats.
**Solution**: Implemented Universal Rendering System with centralized design token control
**Result**: All formats now reference the same font size tokens from design_tokens.json ensuring identical typography hierarchy.

### 3. **Missing Background Fill in Role Boxes** ✅ **RESOLVED**
**Status**: Fixed via design tokens update  
**Description**: Role boxes in both HTML/PDF and DOCX formats were displaying with borders but no background color/fill.
**Solution**: Updated design tokens with `backgroundColor: "#F8F9FA"` and implemented DOCX cell shading
**Result**: Role boxes now have subtle light gray background across all formats providing proper visual hierarchy.

### 4. **Font Style Inconsistencies Across Formats** ✅ **RESOLVED**
**Status**: Fixed via Universal Rendering System  
**Description**: Font styling (weight, family, size) differed between HTML/PDF and DOCX formats.
**Solution**: Universal Rendering System with design tokens controls all typography settings through centralized configuration
**Result**: Consistent font families, weights, and sizing across all formats with proper typography hierarchy.

### 5. **Missing Section Header Borders** ✅ **RESOLVED**
**Status**: Fixed via design tokens implementation  
**Description**: Section headers (PROFESSIONAL SUMMARY, EXPERIENCE, EDUCATION, etc.) were missing blue borders in HTML/PDF formats.
**Solution**: Added complete `sectionBox` configuration in design_tokens.json and regenerated CSS variables
**Result**: Section headers display with blue borders consistently across HTML/PDF and DOCX formats.

### 6. **Excessive Spacing in Experience Section** ✅ **RESOLVED** 
**Status**: Fixed in resume spacing optimization  
**Description**: Two main spacing issues affecting visual density:
- **Issue A**: Excessive spacing between company/location line and role/date line
- **Issue B**: Excessive spacing between role/date line and role description, plus between bullet points
**Impact**: HTML/PDF and DOCX formats, causing inefficient space usage and poor visual flow
**Solution**: Implemented zero spacing design tokens:
- `position-bar-margin-top`: 0rem (was 0.4rem)
- `position-line-margin-bottom`: 0rem (was 0.15rem) 
- `job-content-margin-top`: 0rem (was 0.5rem)
- `bullet-spacing-after`: 0rem (was 0.15rem)
- `docx-paragraph-spacing-pt`: 0 (was 6)
- `docx-bullet-spacing-pt`: 0 (was 6)
**Result**: Ultra-compact layout with maximum space efficiency and improved visual clarity

## ACTIVE ISSUES

### 7. **Download Button Format Options Issue**
**Status**: Unresolved  
**Priority**: Medium
**Description**: The current interface allows both DOCX and PDF download options simultaneously, which may need to be reconsidered based on user experience requirements.
**Current State**: Both "Download PDF" and "Download DOCX" buttons are available
**Impact**: Potential user confusion about which format to choose, interface complexity may be unnecessary

### 8. **Download Button Styling Issues**
**Status**: Unresolved  
**Priority**: Medium
**Description**: The download button styling is not user-friendly and lacks consistent visual feedback states.
**Current Issues**: Button color choice is "not user-friendly to the eyes", lacks proper hover/focus states

### 9. **Projects Section Missing/Incomplete**
**Status**: Unresolved  
**Priority**: Medium
**Description**: The Projects section handling may be incomplete or missing entirely in certain resume formats.
**Impact**: Important resume section may not be displaying properly across all output formats

## SUMMARY

**Progress**: 6 out of 9 issues resolved (67% complete)

**Recently Resolved**: 
- ✅ Issue #6: Excessive spacing optimization - achieved ultra-compact, space-efficient layout
- ✅ All cross-format consistency issues resolved via Universal Rendering System

**Next Focus**: Medium-priority UX improvements (download buttons, projects section, styling) 