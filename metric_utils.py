import re
import logging

logger = logging.getLogger(__name__)

_METRIC_RX = re.compile(r'\d')        # any digit
_PLACEHOLDER_RX = re.compile(r'\?\?')
_UNITED_PLACE_RX = re.compile(r'\?\?(?=\w)') # 'across??', 'by??' etc.

def normalize_bullet(text: str) -> str:
    """
    Guarantee the final bullet has *exactly* one metric token.
    1. If digits exist  ->  drop *all* '??' tokens.
    2. Else if no '??'  ->  inject  '?? %' (or ?? unit) intelligently.
    3. If >1 '??'       ->  keep first, drop the rest.
    Also fixes cases where '??' is glued to a word.
    """
    text = _UNITED_PLACE_RX.sub('?? ', text).strip()   # "across??" -> "across ?? "
    has_digit = bool(_METRIC_RX.search(text))
    placeholders = _PLACEHOLDER_RX.findall(text)

    if has_digit:
        # remove every kind of placeholder
        original_text = text # For logging
        text = _PLACEHOLDER_RX.sub('', text)
        text = re.sub(r'\s{2,}', ' ', text).strip(' ,.;')
        if text != original_text:
            logger.info(f"Normalized bullet (digit present, removed '??'): '{original_text}' -> '{text}'")

    else:
        original_text = text # For logging
        injected = False # Flag to track if injection happened
        if not placeholders:                       # inject one
            injected = True # Mark that we intend to inject
            pivot_found = False
            for pivot in (' by ', ' to ', ' of '):
                if pivot in text:
                    text = text.replace(pivot, f'{pivot}?? % ', 1)
                    pivot_found = True
                    break
            if not pivot_found:                                  # no pivot found
                # Append before potential trailing punctuation
                m = re.match(r'^(.*?)([.!?])?$', text.strip())
                core, punct = m.group(1), m.group(2) or ''
                text = f'{core.strip()} by ?? %{punct}'
            logger.info(f"Normalized bullet (no digit/??, injected '??'): '{original_text}' -> '{text}'")

        elif len(placeholders) > 1:                # keep only first
            injected = True # Mark that modification happened
            first_done = False
            def _keeper(m):
                nonlocal first_done
                if not first_done:
                    first_done = True
                    return '??'
                return ''
            text = _PLACEHOLDER_RX.sub(_keeper, text)
            logger.info(f"Normalized bullet (multiple '??', kept first): '{original_text}' -> '{text}'")

    # length cap + white-space normalisation
    final_text = re.sub(r'\s{2,}', ' ', text).strip()
    return final_text[:130] 