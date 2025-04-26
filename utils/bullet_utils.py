import re

# Comprehensive bullet pattern including unicode glyphs, ascii symbols, and textual escapes
BULLET_ESCAPE_RE = re.compile(
    r'^(?:'
    # Unicode bullet glyphs (common subset)
    r'[•◦▪▫■□▸►▹▻▷▶→⇒⟹⟶]|'
    # ASCII/common symbols
    r'[\*\-\+o~=#>]|'
    # Number followed by dot/paren/bracket
    r'\d+[.)\]]|'
    # Textual escapes
    r'(?:u2022|\\u2022|U\+2022|&#8226;|&bull;)'
    r')\s*',
    re.IGNORECASE
)

def strip_bullet_prefix(line: str) -> str:
    """Remove leading bullet markers (glyph/escape/number/etc.) and whitespace."""
    if not line:
        return line
    return BULLET_ESCAPE_RE.sub('', line).lstrip() 