#!/usr/bin/env python3
"""
Token Orphan Linter - Prevent Design Token Drift

Part of Phase 1, Day 1 implementation of the hybrid CSS refactor.
This linter prevents drift where design tokens are added but never consumed.

Key Features:
- Detects tokens not used in translator or SCSS
- Prevents token bloat and maintenance debt
- Auto-discovers usage across SCSS files
- Supports CI/CD integration
"""

import json
import glob
import os
import re
from pathlib import Path
from typing import Set, List, Dict, Any


def check_token_orphans(tokens_file: str = "design_tokens.json") -> bool:
    """
    Prevent tokens that no rule consumes
    
    Checks both translator usage and SCSS usage to ensure every design token
    is actually being consumed somewhere in the codebase.
    
    Args:
        tokens_file: Path to design_tokens.json
        
    Returns:
        True if no orphan tokens found, False otherwise
    """
    print(f"🔍 Checking for orphan tokens in {tokens_file}")
    
    if not os.path.exists(tokens_file):
        print(f"❌ Tokens file not found: {tokens_file}")
        return False
    
    with open(tokens_file, 'r', encoding='utf-8') as f:
        tokens = json.load(f)
    
    # Check translator AST usage
    used_in_translator = get_translator_usage(tokens)
    
    # Check SCSS usage
    used_in_scss = get_scss_usage(tokens)
    
    # Check raw usage in Python files (style_manager.py, etc.)
    used_in_python = get_python_usage(tokens)
    
    # Find orphans
    all_tokens = set()
    _extract_all_token_keys(tokens, all_tokens)
    
    used_tokens = used_in_translator | used_in_scss | used_in_python
    orphan_tokens = all_tokens - used_tokens
    
    # Report results
    print(f"\n📊 Token Usage Report:")
    print(f"   - Total tokens: {len(all_tokens)}")
    print(f"   - Used in translator: {len(used_in_translator)}")
    print(f"   - Used in SCSS: {len(used_in_scss)}")
    print(f"   - Used in Python: {len(used_in_python)}")
    print(f"   - Total used: {len(used_tokens)}")
    print(f"   - Orphan tokens: {len(orphan_tokens)}")
    
    if orphan_tokens:
        print("\n⚠️ Orphan tokens found (not used in translator, SCSS, or Python):")
        for token in sorted(orphan_tokens):
            print(f"  {token}")
        
        print("\n💡 Consider:")
        print("   - Remove unused tokens from design_tokens.json")
        print("   - Or add usage in SCSS with $token_name variables")
        print("   - Or add usage in translator spacing rules")
        
        return False
    
    print("\n✅ No orphan tokens found - all tokens are being consumed")
    return True


def get_translator_usage(tokens: Dict[str, Any]) -> Set[str]:
    """
    Check which tokens are used by the translator system
    
    The translator system uses spacing-related tokens to generate CSS rules.
    This function simulates the translator logic to see which tokens it would consume.
    
    Args:
        tokens: Design tokens dictionary
        
    Returns:
        Set of token names used by translator
    """
    used_tokens = set()
    
    # Extract spacing-related tokens (same logic as translator)
    for token_name in tokens.keys():
        if any(prop in token_name for prop in ['margin', 'padding', 'gap', 'line-height']):
            used_tokens.add(token_name)
    
    # Also check if existing translator builds are using tokens
    translator_files = [
        'static/css/raw_rules.py',
        'rendering/compat/translator.py'
    ]
    
    for file_path in translator_files:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            for token_name in tokens.keys():
                # Check for direct token usage in translator code
                if token_name in content:
                    used_tokens.add(token_name)
    
    return used_tokens


def get_scss_usage(tokens: Dict[str, Any]) -> Set[str]:
    """
    Check which tokens are used in SCSS files
    
    SCSS files use tokens via $variable_name syntax where token-name becomes $token_name
    
    Args:
        tokens: Design tokens dictionary
        
    Returns:
        Set of token names used in SCSS
    """
    used_tokens = set()
    
    # Find all SCSS files
    scss_files = glob.glob('static/scss/**/*.scss', recursive=True)
    
    # Combine all SCSS content
    scss_content = ""
    for file in scss_files:
        try:
            with open(file, 'r', encoding='utf-8') as f:
                scss_content += f.read()
        except UnicodeDecodeError:
            print(f"⚠️ Could not read {file} (encoding issue)")
            continue
    
    # Check for token usage in SCSS
    for token_name in tokens.keys():
        # Convert token-name to $token_name (SCSS variable syntax)
        scss_var = f"${token_name.replace('-', '_')}"
        
        if scss_var in scss_content:
            used_tokens.add(token_name)
        
        # Also check for direct token name usage (in comments, etc.)
        if token_name in scss_content:
            used_tokens.add(token_name)
    
    return used_tokens


def get_python_usage(tokens: Dict[str, Any]) -> Set[str]:
    """
    Check which tokens are used in Python files
    
    Python files might directly reference token names in dictionaries,
    string formatting, or other contexts.
    
    Args:
        tokens: Design tokens dictionary
        
    Returns:
        Set of token names used in Python files
    """
    used_tokens = set()
    
    # Find relevant Python files
    python_files = [
        'style_manager.py',
        'resume_styler.py', 
        'html_generator.py',
        'style_engine.py',
        'utils/docx_builder.py'
    ]
    
    # Also search for Python files in rendering/
    python_files.extend(glob.glob('rendering/**/*.py', recursive=True))
    
    # Check each Python file
    for file_path in python_files:
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                for token_name in tokens.keys():
                    # Check for token usage in various forms
                    patterns = [
                        f'"{token_name}"',      # String literal
                        f"'{token_name}'",      # String literal  
                        f'{token_name}',        # Direct reference
                        f'["{token_name}"]',    # Dictionary key
                        f"['{token_name}']"     # Dictionary key
                    ]
                    
                    for pattern in patterns:
                        if pattern in content:
                            used_tokens.add(token_name)
                            break
                            
            except UnicodeDecodeError:
                print(f"⚠️ Could not read {file_path} (encoding issue)")
                continue
    
    return used_tokens


def _extract_all_token_keys(obj: Any, keys: Set[str], prefix: str = "") -> None:
    """
    Recursively extract all keys from nested dictionaries
    
    Handles nested structures like roleBox.docx.borderColor
    
    Args:
        obj: Object to extract keys from
        keys: Set to add keys to
        prefix: Current key prefix for nested structures
    """
    if isinstance(obj, dict):
        for key, value in obj.items():
            full_key = f"{prefix}.{key}" if prefix else key
            keys.add(full_key)
            
            if isinstance(value, dict):
                _extract_all_token_keys(value, keys, full_key)
    elif isinstance(obj, (list, tuple)):
        for item in obj:
            _extract_all_token_keys(item, keys, prefix)


def generate_orphan_report(tokens_file: str = "design_tokens.json") -> None:
    """
    Generate a detailed report of token usage across the codebase
    """
    print("🧹 Token Orphan Analysis Report")
    print("=" * 50)
    
    if not os.path.exists(tokens_file):
        print(f"❌ Tokens file not found: {tokens_file}")
        return
    
    with open(tokens_file, 'r', encoding='utf-8') as f:
        tokens = json.load(f)
    
    all_tokens = set()
    _extract_all_token_keys(tokens, all_tokens)
    
    used_in_translator = get_translator_usage(tokens)
    used_in_scss = get_scss_usage(tokens)
    used_in_python = get_python_usage(tokens)
    
    print(f"\n📋 Token Categories:")
    print(f"   🔧 Translator tokens: {len(used_in_translator)}")
    for token in sorted(used_in_translator):
        print(f"      {token}")
    
    print(f"\n   🎨 SCSS tokens: {len(used_in_scss)}")
    for token in sorted(used_in_scss):
        print(f"      {token}")
    
    print(f"\n   🐍 Python tokens: {len(used_in_python)}")
    for token in sorted(used_in_python):
        print(f"      {token}")
    
    orphans = all_tokens - (used_in_translator | used_in_scss | used_in_python)
    if orphans:
        print(f"\n   ⚠️ Orphan tokens: {len(orphans)}")
        for token in sorted(orphans):
            print(f"      {token}")
    
    print("=" * 50)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) == 2 and sys.argv[1] == '--report':
        # Generate detailed orphan report
        generate_orphan_report()
    elif len(sys.argv) == 1:
        # Check for orphans (CI mode)
        success = check_token_orphans()
        sys.exit(0 if success else 1)
    else:
        print("Usage:")
        print("  python tools/token_orphan_linter.py           # Check for orphans")
        print("  python tools/token_orphan_linter.py --report  # Detailed report")
        sys.exit(1) 