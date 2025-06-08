#!/usr/bin/env python3
"""
Achievement Text Sanitizer - O3's Recommendation

This module implements O3's suggested ingest linter to handle problematic achievement text
that contains literal bullet characters or line breaks that interfere with native numbering.

Key issues addressed:
1. Literal "•", "-", "–" prefixes in JSON data (not formatting)
2. Internal line breaks that split achievements into multiple paragraphs
3. Leading/trailing whitespace that can interfere with XML numbering

Based on O3's analysis of the "why-does-this-bullet-work-but-the-next-one-doesn't" mystery.
"""

import re
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

# O3's recommended bullet prefixes to detect and strip
BULLET_PREFIXES = ["•", "-", "–", "‒", "—", "●", "○", "▪", "▫", "◦"]

def sanitize_achievement(raw: str, strict_mode: bool = False) -> List[str]:
    """
    Sanitize achievement text according to O3's recommendations.
    
    Args:
        raw: Raw achievement text from JSON
        strict_mode: If True, raise exception on problematic text; if False, auto-fix
        
    Returns:
        List of cleaned achievement strings (may be multiple if line breaks found)
        
    Raises:
        ValueError: If strict_mode=True and problematic text is detected
    """
    if not raw or not isinstance(raw, str):
        return []
    
    txt = raw.strip()
    if not txt:
        return []
    
    # O3's Fix #1: Detect and handle literal bullet prefixes
    original_had_prefix = False
    for prefix in BULLET_PREFIXES:
        if txt.startswith(prefix):
            original_had_prefix = True
            if strict_mode:
                raise ValueError(f"Achievement contains literal bullet prefix '{prefix}': {txt[:50]}...")
            
            # Strip the prefix and any following whitespace
            txt = txt[len(prefix):].lstrip()
            logger.warning(f"🔧 SANITIZER: Stripped literal bullet prefix '{prefix}' from: {raw[:50]}...")
            break
    
    # O3's Fix #8: Handle internal line breaks
    lines = [line.strip() for line in txt.splitlines() if line.strip()]
    
    if len(lines) > 1:
        if strict_mode:
            raise ValueError(f"Achievement contains line breaks that would split into {len(lines)} paragraphs: {raw[:50]}...")
        
        logger.warning(f"🔧 SANITIZER: Split achievement with line breaks into {len(lines)} separate achievements")
        for i, line in enumerate(lines):
            logger.info(f"   Part {i+1}: {line[:50]}...")
    
    # Additional sanitization
    sanitized_lines = []
    for line in lines:
        # Remove excessive whitespace
        cleaned = re.sub(r'\s+', ' ', line).strip()
        
        # Remove any remaining bullet-like characters at the start
        cleaned = re.sub(r'^[•\-–‒—●○▪▫◦]\s*', '', cleaned).strip()
        
        if cleaned:
            sanitized_lines.append(cleaned)
    
    return sanitized_lines

def validate_achievement_data(achievements: List[str], company: str = "") -> List[str]:
    """
    Validate and sanitize a list of achievements for a company.
    
    Args:
        achievements: List of raw achievement strings
        company: Company name for logging context
        
    Returns:
        List of sanitized achievement strings (may be longer if line breaks were split)
    """
    if not achievements:
        return []
    
    sanitized = []
    total_issues = 0
    
    for i, raw_achievement in enumerate(achievements):
        try:
            cleaned_achievements = sanitize_achievement(raw_achievement, strict_mode=False)
            
            if len(cleaned_achievements) != 1:
                total_issues += 1
                if len(cleaned_achievements) == 0:
                    logger.warning(f"🚨 SANITIZER: Empty achievement #{i+1} for {company}")
                else:
                    logger.info(f"🔧 SANITIZER: Split achievement #{i+1} for {company} into {len(cleaned_achievements)} parts")
            
            sanitized.extend(cleaned_achievements)
            
        except Exception as e:
            logger.error(f"❌ SANITIZER: Failed to sanitize achievement #{i+1} for {company}: {e}")
            # In case of error, try to preserve original text without bullet prefix
            fallback = raw_achievement.strip()
            for prefix in BULLET_PREFIXES:
                if fallback.startswith(prefix):
                    fallback = fallback[len(prefix):].strip()
                    break
            if fallback:
                sanitized.append(fallback)
    
    if total_issues > 0:
        logger.info(f"🔧 SANITIZER: Fixed {total_issues} achievement formatting issues for {company}")
    
    return sanitized

def detect_bullet_prefix_issues(experience_data: dict) -> dict:
    """
    Analyze experience data for bullet prefix issues as O3 suggested.
    
    Returns:
        Dictionary with analysis results
    """
    analysis = {
        'companies_with_issues': [],
        'total_achievements': 0,
        'achievements_with_prefixes': 0,
        'achievements_with_line_breaks': 0,
        'problematic_achievements': []
    }
    
    experiences = experience_data.get('experiences', [])
    if not experiences and 'jobs' in experience_data:
        experiences = experience_data['jobs']
    
    for company_data in experiences:
        company = company_data.get('company', 'Unknown')
        achievements = company_data.get('achievements', [])
        
        company_issues = []
        
        for i, achievement in enumerate(achievements):
            if not isinstance(achievement, str):
                continue
                
            analysis['total_achievements'] += 1
            
            # Check for literal bullet prefixes
            has_prefix = any(achievement.strip().startswith(prefix) for prefix in BULLET_PREFIXES)
            if has_prefix:
                analysis['achievements_with_prefixes'] += 1
                company_issues.append(f"Achievement #{i+1} has bullet prefix: {achievement[:50]}...")
            
            # Check for line breaks
            if '\n' in achievement:
                analysis['achievements_with_line_breaks'] += 1
                company_issues.append(f"Achievement #{i+1} has line breaks: {achievement[:50]}...")
            
            if has_prefix or '\n' in achievement:
                analysis['problematic_achievements'].append({
                    'company': company,
                    'index': i,
                    'text': achievement[:100],
                    'has_prefix': has_prefix,
                    'has_line_breaks': '\n' in achievement
                })
        
        if company_issues:
            analysis['companies_with_issues'].append({
                'company': company,
                'issues': company_issues
            })
    
    return analysis

if __name__ == "__main__":
    # Test the sanitizer with some examples
    test_cases = [
        "• Created statewide student assessment reporting system",
        "– Implemented data warehouse solution consolidating multiple data sources",
        "Built responsive web applications using Angular and Node.js",
        "• Multi-line achievement\nwith internal breaks\nthat should be split",
        "  •  Extra whitespace around bullet  ",
        ""
    ]
    
    print("🧪 Testing Achievement Sanitizer:")
    for i, test in enumerate(test_cases):
        print(f"\nTest {i+1}: {repr(test)}")
        try:
            result = sanitize_achievement(test, strict_mode=False)
            print(f"✅ Result: {result}")
        except ValueError as e:
            print(f"❌ Strict mode error: {e}") 