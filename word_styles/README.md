# Word Styles Package

This package provides a centralized registry and utilities for managing DOCX paragraph styles,
with a focus on properly handling spacing, borders, and other styling attributes consistently
across different Word versions and platforms.

## Motivation

Previous approaches to styling DOCX documents led to inconsistent results with:

1. **Box Height Issues** - Section header boxes would be too tall with excessive space around text
2. **Spacing Between Sections** - Large gaps would appear between sections due to hidden empty paragraphs
3. **Cross-Platform Issues** - Styling that worked in one version of Word would break in another

This package implements a completely new approach to DOCX styling that addresses these issues by:

- Centralizing style definitions in a single registry
- Using direct XML manipulation for precise control over spacing and borders
- Adding Word compatibility settings to ensure consistent rendering across platforms
- Implementing a spacing-neutral approach from the start rather than patching afterward

## Architecture

The package consists of three main modules:

- `registry.py` - Central storage for style definitions with proper defaults
- `xml_utils.py` - Utility functions for generating Word XML styling nodes
- `section_builder.py` - Functions for building sections with proper spacing

### Core Components

#### `ParagraphBoxStyle` Dataclass

A dataclass representing a paragraph style with all its properties, including:
- Font properties (name, size, color, etc.)
- Border properties (width, color, style, padding)
- Spacing properties (before, after, line rule, line height)
- Paragraph properties (keep with next, keep lines, etc.)

#### `StyleRegistry` Class

A registry of paragraph styles that can be applied to a document:
- Pre-registers common styles like BoxedHeading2
- Provides the `get_or_create_style` function to fetch or create styles
- Handles applying compatibility settings to Word documents

#### Spacing and Border Utilities

Functions for creating precise XML nodes for spacing and borders:
- `make_spacing_node` - Creates a spacing node with specified attributes
- `make_border_node` - Creates a border node with specified attributes
- `make_compatibility_node` - Creates compatibility settings for consistent rendering

## Usage

### Basic Usage

```python
from docx import Document
from word_styles.registry import StyleRegistry, get_or_create_style
from word_styles.section_builder import add_section_header, add_content_paragraph

# Create a document
doc = Document()

# Apply compatibility settings
registry = StyleRegistry()
registry.apply_compatibility_settings(doc)

# Add section header with border box
add_section_header(doc, "EXPERIENCE")

# Add content with proper spacing
add_content_paragraph(doc, "This is a content paragraph with proper spacing.")
```

### Advanced Usage - Custom Styles

```python
from docx import Document
from word_styles.registry import StyleRegistry, ParagraphBoxStyle

# Create a custom style
registry = StyleRegistry()
registry.register(ParagraphBoxStyle(
    name="MyCustomStyle",
    base_style_name="Normal",
    font_name="Arial",
    font_size_pt=12.0,
    font_bold=True,
    border_width_pt=0.5,
    border_color="FF0000",  # Red
    border_style="single",
    border_padding_pt=2.0,
    space_before_pt=6.0,
    space_after_pt=6.0,
    line_rule="auto",
    line_height_pt=14.0,
    has_border=True
))

# Use the style in a document
from word_styles.section_builder import add_section_header
doc = Document()
add_section_header(doc, "CUSTOM HEADER", "MyCustomStyle")
```

## Key Benefits

1. **Compact Box Height**: Section header boxes are now properly sized with minimal extra space around text
2. **Consistent Spacing**: No more gaps between sections with properly controlled spacing
3. **Cross-Platform Consistency**: Works reliably in Word for Windows, Mac, and online versions
4. **No More Hidden Paragraphs**: The architecture prevents the creation of hidden paragraphs
5. **Better Maintainability**: Centralized style definitions make it easy to update and extend

## Optimal Settings

Through extensive testing, we've found these optimal settings for section header boxes:

- **Line Rule**: "auto" provides the best balance between compactness and reliability
- **Line Height**: 13.8pt (276 twips) works well with 14pt font, keeping boxes compact
- **Border Padding**: 1pt (20 twips) provides clean spacing around text
- **Space Before/After**: 0pt before, 4pt after for consistent section spacing

## Implementation Notes

1. **Strategic Empty Paragraph Approach**: Rather than fight Word's natural spacing, we intentionally add an EmptyParagraph with zero height before section headers, giving us complete control over spacing
2. **Direct XML Manipulation**: We use direct XML manipulation alongside the python-docx API for maximum control
3. **Compatibility Settings**: We apply Word compatibility settings to ensure consistent rendering

## Testing

Two test scripts are provided to validate the implementation:

1. `tests/docx_spacing/test_line_height_matrix.py` - Tests different combinations of line rule and line height
2. `tests/docx_spacing/test_no_blank_paras.py` - Validates there are no unwanted blank paragraphs

## Migration

When migrating from the old approach:

1. Replace calls to `_fix_spacing_between_sections` with `tighten_before_headers`
2. Replace direct styling with calls to the style registry
3. Use the section builder functions for adding section headers and content

Example:
```python
# Old approach
section_para = doc.add_paragraph("SECTION HEADER")
StyleEngine.apply_boxed_section_header_style(doc, section_para)

# New approach
from word_styles.section_builder import add_section_header
add_section_header(doc, "SECTION HEADER")
``` 