#!/usr/bin/env python3
"""
Style Linter - Prevent Spacing Drift Back to SCSS

Part of Phase 1, Day 2 implementation of the hybrid CSS refactor.
This linter prevents spacing properties from being added to SCSS files.

Key Features:
- Enforces style taxonomy: spacing → design tokens, UI → SCSS
- Whitelist for line-height on headings (o3 refinement)
- Escape hatch with /* translator-ignore */ comments
- CI integration to fail builds on violations
"""

import glob
import os
import re
from typing import List, Tuple, Set


def check_scss_spacing_violations(scss_root: str = "static/scss") -> bool:
    """
    Prevent spacing drift back to SCSS with whitelist (o3 refinement)
    
    Checks SCSS files for spacing properties that should be in design tokens.
    Allows line-height for headings and properties with /* translator-ignore */ comments.
    
    Args:
        scss_root: Root directory containing SCSS files
        
    Returns:
        True if no violations found, False otherwise
    """
    print(f"🔍 Checking SCSS spacing violations in {scss_root}")
    
    if not os.path.exists(scss_root):
        print(f"❌ SCSS root directory not found: {scss_root}")
        return False
    
    scss_files = glob.glob(f'{scss_root}/**/*.scss', recursive=True)
    violations = []
    
    # Spacing properties that should be in design tokens
    spacing_props = ['margin', 'padding', 'gap', 'line-height']
    
    # o3 refinement: Whitelist line-height for headings
    allowed_line_height_selectors = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']
    
    print(f"📂 Checking {len(scss_files)} SCSS files:")
    
    for file_path in scss_files:
        print(f"   - {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except UnicodeDecodeError:
            print(f"⚠️ Could not read {file_path} (encoding issue)")
            continue
            
        file_violations = check_file_spacing_violations(
            file_path, lines, spacing_props, allowed_line_height_selectors
        )
        violations.extend(file_violations)
    
    # Report results
    print(f"\n📊 Style Linter Results:")
    print(f"   - Files checked: {len(scss_files)}")
    print(f"   - Violations found: {len(violations)}")
    
    if violations:
        print("\n❌ SCSS spacing violations found:")
        for violation in violations:
            print(f"  {violation}")
        
        print("\n💡 Fix violations by:")
        print("   - Moving spacing properties to design_tokens.json")
        print("   - Using translator layer for spacing control")
        print("   - Adding /* translator-ignore */ comment for exceptions")
        
        return False
    
    print("\n✅ No SCSS spacing violations found")
    return True


def check_file_spacing_violations(
    file_path: str, 
    lines: List[str], 
    spacing_props: List[str],
    allowed_line_height_selectors: List[str]
) -> List[str]:
    """
    Check a single SCSS file for spacing violations
    
    Args:
        file_path: Path to SCSS file
        lines: File content as list of lines
        spacing_props: List of spacing properties to check
        allowed_line_height_selectors: Selectors allowed to have line-height
        
    Returns:
        List of violation messages
    """
    violations = []
    current_selector = ""
    
    for i, line in enumerate(lines):
        line_num = i + 1
        stripped_line = line.strip()
        
        # Skip comments and empty lines
        if not stripped_line or stripped_line.startswith('//'):
            continue
        
        # Track current selector context
        if '{' in stripped_line and not stripped_line.startswith('@'):
            # Extract selector before {
            selector_match = re.match(r'^([^{]+)\s*\{', stripped_line)
            if selector_match:
                current_selector = selector_match.group(1).strip()
        
        # Check for spacing properties
        for prop in spacing_props:
            if f'{prop}:' in stripped_line or f'{prop}-' in stripped_line:
                # Check for translator-ignore escape hatch
                if '/* translator-ignore */' in line:
                    continue
                
                # o3 refinement: Allow line-height for headings
                if prop == 'line-height':
                    if any(sel in current_selector for sel in allowed_line_height_selectors):
                        continue
                
                violation = f"{file_path}:{line_num} - {prop} should use translator (selector: {current_selector})"
                violations.append(violation)
    
    return violations


def generate_style_taxonomy_report() -> None:
    """
    Generate a report showing the style taxonomy enforcement
    """
    print("📋 Style Taxonomy Report")
    print("=" * 50)
    
    print("\n🎯 Style Taxonomy Rules:")
    print("   📦 Box Model Properties → Design Tokens + Translator")
    print("      - margin-* (top, bottom, left, right, block, inline)")
    print("      - padding-* (top, bottom, left, right, block, inline)")
    print("      - gap")
    print("      - line-height (except h1-h6)")
    print("")
    print("   🎨 Visual Properties → SCSS")
    print("      - color, background-color")
    print("      - font-family, font-size, font-weight")
    print("      - border, border-radius")
    print("      - display, position, flex")
    print("      - line-height (h1-h6 allowed)")
    print("")
    print("   🚪 Escape Hatch:")
    print("      - Add /* translator-ignore */ comment for exceptions")
    print("")
    print("   ✅ Benefits:")
    print("      - Single source of truth for spacing")
    print("      - Prevents spacing drift")
    print("      - Clear separation of concerns")
    
    print("=" * 50)


def check_design_token_coverage() -> None:
    """
    Check if all spacing properties in SCSS have corresponding design tokens
    """
    print("\n🔄 Checking design token coverage...")
    
    # This would analyze SCSS files and cross-reference with design_tokens.json
    # to ensure all spacing values have corresponding tokens
    
    # For now, just a placeholder
    print("   ℹ️ Design token coverage check not yet implemented")
    print("   ℹ️ Will be added in Phase 2 for comprehensive validation")


def main():
    """Main function to run style linting"""
    print("🎯 Style Linter - Prevent Spacing Drift")
    print("=" * 50)
    
    # Check for spacing violations
    success = check_scss_spacing_violations()
    
    # Generate taxonomy report
    generate_style_taxonomy_report()
    
    # Check design token coverage (placeholder)
    check_design_token_coverage()
    
    return success


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) == 2:
        command = sys.argv[1]
        
        if command == '--report':
            generate_style_taxonomy_report()
            sys.exit(0)
        elif command == '--help':
            print("Usage:")
            print("  python tools/style_linter.py           # Check for violations")
            print("  python tools/style_linter.py --report  # Show style taxonomy")
            sys.exit(0)
        else:
            print(f"Unknown command: {command}")
            sys.exit(1)
    
    elif len(sys.argv) == 1:
        # Default: check for violations (CI mode)
        success = main()
        sys.exit(0 if success else 1)
    
    else:
        print("Usage:")
        print("  python tools/style_linter.py           # Check for violations")
        print("  python tools/style_linter.py --report  # Show style taxonomy")
        sys.exit(1) 