"""
Unicode Bullet Character Sanitization System (B3)

This module provides comprehensive sanitization of bullet characters
from text content, preventing conflicts with native Word numbering.

Key Features:
- Comprehensive bullet character detection
- Locale-specific bullet patterns
- Smart sanitization with context awareness
- Preservation of intentional special characters
- Integration with bullet reconciliation

Author: Resume Tailor Team + O3 Expert Review
Status: B3 Implementation - Production Ready
"""

import logging
import re
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class BulletType(Enum):
    """Types of bullet characters found in text."""
    WESTERN_BULLET = "western_bullet"          # • · ◦ ▪ ▫ ‣ ⁃
    EASTERN_BULLET = "eastern_bullet"          # ・ ◆ ◇ ■ □ ● ○
    HYPHEN_DASH = "hyphen_dash"               # - – — ‒ ‑ ‐
    ASTERISK_STAR = "asterisk_star"           # * ★ ☆ ✦ ✧ ✱
    ARROW_POINTER = "arrow_pointer"           # → ⇒ ⇨ ► ▶ ▷
    NUMERIC_BULLET = "numeric_bullet"         # ① ② ③ ❶ ❷ ❸
    CUSTOM_SYMBOL = "custom_symbol"           # § ¶ ♦ ♠ ♣ ♥
    UNKNOWN = "unknown"


@dataclass
class BulletDetection:
    """Result of bullet character detection."""
    found: bool
    bullet_type: BulletType
    character: str
    position: int
    confidence: float
    should_remove: bool
    replacement_suggestion: str


class UnicodeBulletSanitizer:
    """
    Comprehensive Unicode bullet character sanitizer.
    
    This sanitizer implements B3 requirements:
    - Detection of various bullet character types
    - Locale-aware sanitization
    - Context-sensitive removal decisions
    - Integration with bullet reconciliation
    """
    
    def __init__(self):
        """Initialize the sanitizer with comprehensive bullet patterns."""
        
        # B3: Comprehensive bullet character mappings
        self.bullet_patterns = {
            BulletType.WESTERN_BULLET: {
                'chars': ['•', '·', '◦', '▪', '▫', '‣', '⁃', '⁌', '⁍'],
                'regex': r'^[\s]*[•·◦▪▫‣⁃⁌⁍][\s]*',
                'confidence': 0.9,
                'common_locales': ['en', 'fr', 'de', 'es', 'it']
            },
            BulletType.EASTERN_BULLET: {
                'chars': ['・', '◆', '◇', '■', '□', '●', '○', '♦', '◘', '◙'],
                'regex': r'^[\s]*[・◆◇■□●○♦◘◙][\s]*',
                'confidence': 0.85,
                'common_locales': ['ja', 'ko', 'zh', 'zh-cn', 'zh-tw']
            },
            BulletType.HYPHEN_DASH: {
                'chars': ['-', '–', '—', '‒', '‑', '‐', '⸺', '⸻'],
                'regex': r'^[\s]*[-–—‒‑‐⸺⸻][\s]*',
                'confidence': 0.7,  # Lower confidence due to ambiguity
                'common_locales': ['all']
            },
            BulletType.ASTERISK_STAR: {
                'chars': ['*', '★', '☆', '✦', '✧', '✱', '✲', '✳', '✴', '✵'],
                'regex': r'^[\s]*[*★☆✦✧✱✲✳✴✵][\s]*',
                'confidence': 0.75,
                'common_locales': ['all']
            },
            BulletType.ARROW_POINTER: {
                'chars': ['→', '⇒', '⇨', '►', '▶', '▷', '➤', '➜', '⇛', '⇝'],
                'regex': r'^[\s]*[→⇒⇨►▶▷➤➜⇛⇝][\s]*',
                'confidence': 0.8,
                'common_locales': ['all']
            },
            BulletType.NUMERIC_BULLET: {
                'chars': ['①', '②', '③', '④', '⑤', '⑥', '⑦', '⑧', '⑨', '⑩',
                         '❶', '❷', '❸', '❹', '❺', '❻', '❼', '❽', '❾', '❿'],
                'regex': r'^[\s]*[①②③④⑤⑥⑦⑧⑨⑩❶❷❸❹❺❻❼❽❾❿][\s]*',
                'confidence': 0.95,
                'common_locales': ['all']
            },
            BulletType.CUSTOM_SYMBOL: {
                'chars': ['§', '¶', '♠', '♣', '♥', '♪', '♫', '☎', '☏', '✓', '✔', '✕', '✗'],
                'regex': r'^[\s]*[§¶♠♣♥♪♫☎☏✓✔✕✗][\s]*',
                'confidence': 0.6,  # Lower confidence - might be intentional
                'common_locales': ['all']
            }
        }
        
        # B3: Context-aware exclusion patterns
        self.exclusion_patterns = {
            'email_dash': r'[\w\.-]+@[\w\.-]+\.\w+',      # Email addresses
            'phone_dash': r'\b\d{3}-\d{3}-\d{4}\b',       # Phone numbers
            'url_scheme': r'https?://[\w\.-]+',           # URLs
            'date_dash': r'\b\d{1,2}-\d{1,2}-\d{4}\b',    # Dates
            'range_dash': r'\b\d+\s*[-–—]\s*\d+\b',       # Number ranges
            'compound_word': r'\b\w+-\w+\b',              # Hyphenated words
            'emoticon': r'[:;]-?[()PpDd]',                # Simple emoticons
            'currency': r'[$€£¥₹]\s*\d',                  # Currency symbols
        }
        
        # B3: Sanitization statistics
        self.stats = {
            'total_processed': 0,
            'bullets_found': 0,
            'bullets_removed': 0,
            'false_positives_avoided': 0,
            'by_type': {bt: 0 for bt in BulletType}
        }
        
    def sanitize_text(self, text: str, locale: Optional[str] = None) -> Tuple[str, List[BulletDetection]]:
        """
        Sanitize text by removing bullet characters.
        
        Args:
            text: Text to sanitize
            locale: Optional locale for context-aware sanitization
            
        Returns:
            Tuple of (sanitized_text, detections_list)
        """
        if not text or not text.strip():
            return text, []
        
        self.stats['total_processed'] += 1
        detections = []
        sanitized_text = text
        
        logger.debug(f"B3: Sanitizing text: '{text[:50]}...'")
        
        # B3: Detect all bullet characters
        for bullet_type, pattern_info in self.bullet_patterns.items():
            detection = self._detect_bullet_type(text, bullet_type, pattern_info, locale)
            
            if detection.found:
                detections.append(detection)
                self.stats['bullets_found'] += 1
                self.stats['by_type'][bullet_type] += 1
                
                # B3: Apply context-aware removal decision
                if detection.should_remove:
                    sanitized_text = self._remove_bullet_character(
                        sanitized_text, detection
                    )
                    self.stats['bullets_removed'] += 1
                    logger.info(f"B3: Removed {bullet_type.value} bullet '{detection.character}' from text")
                else:
                    self.stats['false_positives_avoided'] += 1
                    logger.debug(f"B3: Preserved {bullet_type.value} character '{detection.character}' (context-sensitive)")
        
        return sanitized_text, detections
    
    def _detect_bullet_type(self, text: str, bullet_type: BulletType, 
                          pattern_info: Dict, locale: Optional[str]) -> BulletDetection:
        """Detect specific bullet type in text."""
        
        # B3: Use regex for efficient detection
        regex_pattern = pattern_info['regex']
        match = re.match(regex_pattern, text, re.UNICODE)
        
        if not match:
            return BulletDetection(
                found=False,
                bullet_type=bullet_type,
                character='',
                position=-1,
                confidence=0.0,
                should_remove=False,
                replacement_suggestion=''
            )
        
        # Extract the bullet character
        bullet_char = match.group().strip()
        position = match.start()
        
        # B3: Calculate confidence based on context
        base_confidence = pattern_info['confidence']
        context_confidence = self._calculate_context_confidence(text, bullet_char, bullet_type)
        final_confidence = min(base_confidence * context_confidence, 1.0)
        
        # B3: Locale-aware confidence adjustment
        if locale:
            locale_boost = self._get_locale_confidence_boost(bullet_type, locale, pattern_info)
            final_confidence = min(final_confidence + locale_boost, 1.0)
        
        # B3: Decide whether to remove
        should_remove = self._should_remove_bullet(text, bullet_char, final_confidence)
        
        # B3: Suggest replacement
        replacement = self._suggest_replacement(bullet_char, bullet_type)
        
        return BulletDetection(
            found=True,
            bullet_type=bullet_type,
            character=bullet_char,
            position=position,
            confidence=final_confidence,
            should_remove=should_remove,
            replacement_suggestion=replacement
        )
    
    def _calculate_context_confidence(self, text: str, bullet_char: str, bullet_type: BulletType) -> float:
        """Calculate confidence based on text context."""
        
        # B3: Check for exclusion patterns
        text_lower = text.lower()
        
        for pattern_name, pattern_regex in self.exclusion_patterns.items():
            if re.search(pattern_regex, text, re.IGNORECASE):
                logger.debug(f"B3: Found exclusion pattern '{pattern_name}' in text")
                return 0.3  # Significantly reduce confidence
        
        # B3: Boost confidence if bullet is at start and followed by content
        if text.strip().startswith(bullet_char):
            # Check if there's actual content after the bullet
            remaining_text = text.strip()[len(bullet_char):].strip()
            if len(remaining_text) > 5:  # Minimum meaningful content
                return 1.2  # Boost confidence
        
        # B3: Reduce confidence if bullet appears mid-sentence
        words_before = text[:text.find(bullet_char)].strip().split()
        if len(words_before) > 3:
            return 0.5  # Likely not a list bullet
        
        return 1.0  # Neutral confidence
    
    def _get_locale_confidence_boost(self, bullet_type: BulletType, locale: str, 
                                   pattern_info: Dict) -> float:
        """Get locale-specific confidence boost."""
        
        common_locales = pattern_info.get('common_locales', [])
        
        if 'all' in common_locales:
            return 0.1  # Small boost for universal patterns
        
        # B3: Exact locale match
        if locale in common_locales:
            return 0.2
        
        # B3: Language family match (e.g., zh matches zh-cn)
        locale_lang = locale.split('-')[0] if '-' in locale else locale
        for common_locale in common_locales:
            common_lang = common_locale.split('-')[0] if '-' in common_locale else common_locale
            if locale_lang == common_lang:
                return 0.15
        
        return 0.0  # No locale-specific boost
    
    def _should_remove_bullet(self, text: str, bullet_char: str, confidence: float) -> bool:
        """Decide whether to remove the bullet character."""
        
        # B3: Conservative removal threshold
        min_confidence = 0.7
        
        if confidence < min_confidence:
            return False
        
        # B3: Additional safety checks
        
        # Don't remove if bullet is part of a larger symbol sequence
        bullet_index = text.find(bullet_char)
        if bullet_index > 0:
            prev_char = text[bullet_index - 1]
            if prev_char in '!@#$%^&*()[]{}|\\:";\'<>?,.`~':
                return False
        
        # Don't remove if followed immediately by letters (might be part of word)
        if bullet_index + len(bullet_char) < len(text):
            next_char = text[bullet_index + len(bullet_char)]
            if next_char.isalpha():
                return False
        
        # B3: Safe to remove
        return True
    
    def _suggest_replacement(self, bullet_char: str, bullet_type: BulletType) -> str:
        """Suggest appropriate replacement for removed bullet."""
        
        # B3: Most bullet types should just be removed (empty replacement)
        if bullet_type in [BulletType.WESTERN_BULLET, BulletType.EASTERN_BULLET,
                          BulletType.ASTERISK_STAR, BulletType.ARROW_POINTER]:
            return ''
        
        # B3: Numeric bullets might be replaced with text
        if bullet_type == BulletType.NUMERIC_BULLET:
            return ''  # Let Word handle numbering
        
        # B3: Hyphens might be contextual
        if bullet_type == BulletType.HYPHEN_DASH:
            return ''  # Remove bullet-style hyphens
        
        return ''  # Default: remove
    
    def _remove_bullet_character(self, text: str, detection: BulletDetection) -> str:
        """Remove bullet character from text."""
        
        # B3: Smart removal that preserves spacing
        bullet_char = detection.character
        replacement = detection.replacement_suggestion
        
        # Find the bullet in the text
        bullet_index = text.find(bullet_char)
        if bullet_index == -1:
            return text
        
        # B3: Remove bullet and normalize spacing
        before = text[:bullet_index]
        after = text[bullet_index + len(bullet_char):]
        
        # Clean up spacing - remove leading/trailing whitespace from the bullet area
        before = before.rstrip()
        after = after.lstrip()
        
        # Add single space if needed to separate words
        if before and after and not before.endswith(' ') and not after.startswith(' '):
            return before + ' ' + replacement + after
        else:
            return before + replacement + after
    
    def get_sanitization_stats(self) -> Dict[str, any]:
        """Get comprehensive sanitization statistics."""
        
        total = self.stats['total_processed']
        found = self.stats['bullets_found']
        removed = self.stats['bullets_removed']
        
        return {
            'total_texts_processed': total,
            'total_bullets_found': found,
            'total_bullets_removed': removed,
            'false_positives_avoided': self.stats['false_positives_avoided'],
            'removal_rate': (removed / found * 100) if found > 0 else 0,
            'detection_rate': (found / total * 100) if total > 0 else 0,
            'by_bullet_type': {
                bt.value: count for bt, count in self.stats['by_type'].items()
            }
        }
    
    def reset_stats(self):
        """Reset sanitization statistics."""
        self.stats = {
            'total_processed': 0,
            'bullets_found': 0,
            'bullets_removed': 0,
            'false_positives_avoided': 0,
            'by_type': {bt: 0 for bt in BulletType}
        }


# Global sanitizer instance
unicode_sanitizer = UnicodeBulletSanitizer()


def sanitize_bullet_text(text: str, locale: Optional[str] = None) -> str:
    """
    Convenience function for sanitizing bullet characters from text.
    
    Args:
        text: Text to sanitize
        locale: Optional locale for context-aware sanitization
        
    Returns:
        Sanitized text with bullet characters removed
    """
    if not text:
        return text
        
    sanitized, detections = unicode_sanitizer.sanitize_text(text, locale)
    
    if detections:
        removed_chars = [d.character for d in detections if d.should_remove]
        if removed_chars:
            logger.debug(f"B3: Sanitized text, removed: {removed_chars}")
    
    return sanitized


def analyze_bullet_characters(text: str) -> List[BulletDetection]:
    """
    Analyze text for bullet characters without modifying it.
    
    Args:
        text: Text to analyze
        
    Returns:
        List of bullet character detections
    """
    if not text:
        return []
        
    _, detections = unicode_sanitizer.sanitize_text(text)
    return detections


def get_supported_bullet_types() -> List[str]:
    """Get list of supported bullet character types."""
    return [bt.value for bt in BulletType if bt != BulletType.UNKNOWN] 