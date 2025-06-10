# ADR-001: Style Taxonomy for Hybrid CSS Architecture

## Status
**ACCEPTED** - Date: 2024-01-XX

## Context
The resume styling system currently has architectural issues with spacing control:
- Design tokens contain correct zero spacing values
- SCSS files override these with hardcoded spacing values  
- This creates inconsistent spacing across HTML/PDF/DOCX formats
- WeasyPrint generates warnings due to logical property usage

We need clear boundaries between what the translator layer controls vs. what SCSS controls to achieve:
1. **Single source of truth** for spacing
2. **Cross-format consistency** 
3. **Prevention of spacing drift** back to SCSS

## Decision

### **Box Model Properties → Design Tokens + Translator**
The following CSS properties MUST be controlled through design tokens and the translator layer:

**Spacing Properties:**
- `margin`, `margin-*`, `margin-block`, `margin-inline`
- `padding`, `padding-*`, `padding-block`, `padding-inline`  
- `gap`, `row-gap`, `column-gap`
- `space-*` (custom spacing tokens)

**Layout Properties:**
- `line-height` (except for headings - see exceptions)
- `text-indent`
- `top`, `right`, `bottom`, `left` (positioning)

### **Visual Properties → SCSS**
The following CSS properties remain under SCSS control:

**Color & Appearance:**
- `color`, `background-color`, `border-color`
- `opacity`, `visibility`, `filter`
- `box-shadow`, `text-shadow`
- `background-image`, `background-gradient`

**Typography (Visual):**
- `font-family`, `font-size`, `font-weight`
- `text-decoration`, `text-transform`
- `letter-spacing`, `word-spacing`

**Layout Structure (Non-spacing):**
- `display`, `position`, `z-index`
- `flex-direction`, `justify-content`, `align-items`
- `grid-template-columns`, `grid-template-rows`
- `overflow`, `white-space`

**Borders & Effects:**
- `border-style`, `border-width` (but not `border-spacing`)
- `border-radius`, `outline`
- `transform`, `transition`, `animation`

### **Exceptions & Special Cases**

**Heading Line-Height Exception:**
- `line-height` on `h1`, `h2`, `h3`, `h4`, `h5`, `h6` may remain in SCSS for visual rhythm
- Must be marked with `/* translator-ignore: visual-rhythm */` comment

**Responsive Overrides:**
- Media query spacing overrides allowed in SCSS if marked with `/* translator-ignore: responsive */`

**Component-Specific Spacing:**
- Interactive components (buttons, forms) may have spacing in SCSS if marked with `/* translator-ignore: component */`

## Enforcement

### **Pre-Commit Linting**
- `tools/style_linter.py` will scan all `.scss` files
- **FAIL** if box model properties found without `/* translator-ignore */` comment
- **PASS** only if spacing flows through design tokens

### **CI Pipeline Enforcement**
```yaml
# .github/workflows/styles.yml
- name: Style Taxonomy Compliance
  run: |
    python tools/style_linter.py
    if [ $? -ne 0 ]; then
      echo "❌ Box model properties found in SCSS - use design tokens"
      exit 1
    fi
```

### **Linter Rules**
```python
# Forbidden in SCSS without translator-ignore comment:
FORBIDDEN_PROPS = [
    'margin', 'margin-top', 'margin-right', 'margin-bottom', 'margin-left',
    'margin-block', 'margin-inline', 'margin-block-start', 'margin-block-end',
    'padding', 'padding-top', 'padding-right', 'padding-bottom', 'padding-left', 
    'padding-block', 'padding-inline', 'padding-block-start', 'padding-block-end',
    'gap', 'row-gap', 'column-gap', 'line-height', 'text-indent'
]

# Whitelisted selectors for line-height (visual rhythm):
LINE_HEIGHT_WHITELIST = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']
```

## Benefits

### **Single Source of Truth**
- All spacing controlled through `design_tokens.json`
- No conflicting values between SCSS and tokens
- Consistent spacing across HTML/PDF/DOCX formats

### **Cross-Format Compatibility**  
- Translator handles engine-specific conversions
- WeasyPrint gets physical properties (no warnings)
- Word gets proper XML spacing values
- Browsers get modern logical properties

### **Maintainability**
- Clear ownership boundaries prevent confusion
- Linting prevents accidental spacing drift
- Future developers know exactly where to make spacing changes

### **Performance**
- Translator only processes spacing-critical rules (~30 rules vs 1000+ full CSS)
- SCSS compilation focuses on visual styles
- Hybrid build optimizes each concern separately

## Consequences

### **Positive**
- **Zero spacing drift**: Impossible to accidentally override tokens in SCSS
- **Format consistency**: Same spacing logic across all output formats  
- **Developer clarity**: Obvious where to make spacing vs visual changes
- **Automated compliance**: CI enforces the taxonomy automatically

### **Negative**
- **Learning curve**: Developers must understand the taxonomy
- **Initial migration**: Existing SCSS spacing must be removed/migrated
- **Two build systems**: Must maintain both SCSS compilation and translator
- **Edge case complexity**: Special cases require `translator-ignore` comments

## Implementation Timeline

### **Phase 1: Setup** (Days 1-2)
- [x] Create this ADR
- [ ] Setup `style_linter.py` with taxonomy rules
- [ ] Update capability tables for project-specific formats

### **Phase 2: Migration** (Days 3-4) 
- [ ] Remove spacing from existing SCSS files
- [ ] Create hybrid CSS builder
- [ ] Enforce taxonomy with CI linting

### **Phase 3: Testing** (Days 5-8)
- [ ] Cross-format spacing validation
- [ ] Visual regression testing
- [ ] Performance telemetry

### **Phase 4: Production** (Days 9-11)
- [ ] Feature flag rollout
- [ ] Documentation updates
- [ ] Legacy cleanup

## Alternatives Considered

### **Option 1: Full SCSS Migration**
- **Rejected**: Would lose design token benefits and require massive refactoring

### **Option 2: Translator-Only Styling**  
- **Rejected**: Too radical, would break existing UI styles and responsive design

### **Option 3: Status Quo**
- **Rejected**: Spacing issues persist, no single source of truth

## References
- [REFACTOR_PLAN.md](./REFACTOR_PLAN.md) - Full implementation roadmap
- [o3 Strategic Recommendations] - Source-of-truth discipline guidance
- [Design Tokens Specification](./design_tokens.json) - Current token structure

---

**Author**: Implementation Team  
**Reviewers**: o3 (Strategic Advisor)  
**Next Review**: Post-Day 11 implementation assessment 