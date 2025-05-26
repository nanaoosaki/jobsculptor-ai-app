#!/usr/bin/env python3
"""
Style Linter for Hybrid CSS Architecture
Enforces Style Taxonomy ADR-001: Box model properties must use design tokens + translator

Usage:
    python tools/style_linter.py                    # Check all SCSS files
    python tools/style_linter.py --file path.scss   # Check specific file
    python tools/style_linter.py --ci               # CI mode (exit with error code)
"""

import os
import re
import sys
import glob
import argparse
from typing import List, Tuple, Dict, Set
from pathlib import Path

# Box model properties that MUST use design tokens + translator (ADR-001)
FORBIDDEN_SCSS_PROPS = [
    # Margin properties
    'margin', 'margin-top', 'margin-right', 'margin-bottom', 'margin-left',
    'margin-block', 'margin-inline', 'margin-block-start', 'margin-block-end',
    'margin-inline-start', 'margin-inline-end',
    
    # Padding properties  
    'padding', 'padding-top', 'padding-right', 'padding-bottom', 'padding-left',
    'padding-block', 'padding-inline', 'padding-block-start', 'padding-block-end',
    'padding-inline-start', 'padding-inline-end',
    
    # Gap properties
    'gap', 'row-gap', 'column-gap', 'grid-gap', 'grid-row-gap', 'grid-column-gap',
    
    # Layout spacing properties
    'line-height',  # Exception: allowed for h1-h6 with visual-rhythm comment
    'text-indent',
    
    # Position properties (spacing-related)
    'top', 'right', 'bottom', 'left',
    'inset', 'inset-block', 'inset-inline',
]

# Whitelisted selectors where line-height is allowed (visual rhythm)
LINE_HEIGHT_WHITELIST = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']

# Valid translator-ignore reasons
VALID_IGNORE_REASONS = [
    'visual-rhythm',    # For h1-h6 line-height
    'responsive',       # For media query overrides
    'component',        # For interactive components (buttons, forms)
    'legacy',          # Temporary during migration
    'vendor',          # Third-party component overrides
]

class StyleViolation:
    def __init__(self, file_path: str, line_num: int, prop: str, value: str, line_content: str):
        self.file_path = file_path
        self.line_num = line_num
        self.prop = prop
        self.value = value
        self.line_content = line_content.strip()
    
    def __str__(self):
        return f"{self.file_path}:{self.line_num} - '{self.prop}' should use design tokens + translator"

class StyleLinter:
    def __init__(self, strict_mode: bool = False):
        self.strict_mode = strict_mode
        self.violations: List[StyleViolation] = []
        
    def lint_file(self, file_path: str) -> List[StyleViolation]:
        """Lint a single SCSS file for style taxonomy violations."""
        violations = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except Exception as e:
            print(f"⚠️  Warning: Could not read {file_path}: {e}")
            return violations
            
        for line_num, line in enumerate(lines, 1):
            violations.extend(self._check_line(file_path, line_num, line))
            
        return violations
    
    def _check_line(self, file_path: str, line_num: int, line: str) -> List[StyleViolation]:
        """Check a single line for style taxonomy violations."""
        violations = []
        line_clean = line.strip()
        
        # Skip comments, empty lines, and imports
        if (not line_clean or 
            line_clean.startswith('//') or 
            line_clean.startswith('/*') or
            line_clean.startswith('@import') or
            line_clean.startswith('@use')):
            return violations
        
        # Check for translator-ignore comment on the same line
        has_ignore_comment = '/* translator-ignore' in line
        
        # Extract CSS property declarations
        css_property_pattern = r'^\s*([a-zA-Z-]+)\s*:\s*([^;]+);?'
        match = re.match(css_property_pattern, line_clean)
        
        if match:
            prop = match.group(1).strip()
            value = match.group(2).strip()
            
            if prop in FORBIDDEN_SCSS_PROPS:
                violation = None
                
                if prop == 'line-height':
                    # Special handling for line-height on headings
                    if self._is_heading_line_height(file_path, line_num, line):
                        if not has_ignore_comment or 'visual-rhythm' not in line:
                            violation = StyleViolation(
                                file_path, line_num, prop, value, line_clean
                            )
                    else:
                        # Non-heading line-height must be ignored or use translator
                        if not has_ignore_comment:
                            violation = StyleViolation(
                                file_path, line_num, prop, value, line_clean
                            )
                else:
                    # All other forbidden properties
                    if not has_ignore_comment:
                        violation = StyleViolation(
                            file_path, line_num, prop, value, line_clean
                        )
                
                if violation:
                    violations.append(violation)
                    
                # Validate ignore comment reason if present
                if has_ignore_comment:
                    self._validate_ignore_comment(file_path, line_num, line)
        
        return violations
    
    def _is_heading_line_height(self, file_path: str, line_num: int, line: str) -> bool:
        """Check if line-height is being applied to a heading selector."""
        # Look for heading selectors in the current context
        # This is a simplified check - could be enhanced with proper SCSS parsing
        context_lines = self._get_context_lines(file_path, line_num, lookback=10)
        
        for context_line in context_lines:
            for heading in LINE_HEIGHT_WHITELIST:
                if f'{heading}' in context_line and '{' in context_line:
                    return True
        return False
    
    def _get_context_lines(self, file_path: str, line_num: int, lookback: int = 5) -> List[str]:
        """Get previous lines for context analysis."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                start = max(0, line_num - lookback - 1)
                end = line_num - 1
                return [line.strip() for line in lines[start:end]]
        except:
            return []
    
    def _validate_ignore_comment(self, file_path: str, line_num: int, line: str):
        """Validate that translator-ignore comment has a valid reason."""
        ignore_pattern = r'/\*\s*translator-ignore\s*:?\s*([^*]+)\*/'
        match = re.search(ignore_pattern, line)
        
        if match:
            reason = match.group(1).strip()
            if reason not in VALID_IGNORE_REASONS:
                print(f"⚠️  {file_path}:{line_num} - Invalid ignore reason '{reason}'. Valid: {', '.join(VALID_IGNORE_REASONS)}")
    
    def lint_directory(self, scss_dir: str = "static/scss") -> List[StyleViolation]:
        """Lint all SCSS files in a directory."""
        all_violations = []
        
        scss_pattern = os.path.join(scss_dir, "**/*.scss")
        scss_files = glob.glob(scss_pattern, recursive=True)
        
        if not scss_files:
            print(f"⚠️  No SCSS files found in {scss_dir}")
            return all_violations
        
        print(f"🔍 Linting {len(scss_files)} SCSS files...")
        
        for file_path in scss_files:
            file_violations = self.lint_file(file_path)
            all_violations.extend(file_violations)
            
            if file_violations:
                print(f"❌ {file_path}: {len(file_violations)} violations")
            else:
                print(f"✅ {file_path}: clean")
        
        return all_violations
    
    def report_violations(self, violations: List[StyleViolation]) -> bool:
        """Report all violations and return True if any found."""
        if not violations:
            print("✅ No style taxonomy violations found!")
            return False
        
        print(f"\n❌ Found {len(violations)} style taxonomy violations:")
        print("=" * 60)
        
        # Group violations by file
        violations_by_file: Dict[str, List[StyleViolation]] = {}
        for violation in violations:
            if violation.file_path not in violations_by_file:
                violations_by_file[violation.file_path] = []
            violations_by_file[violation.file_path].append(violation)
        
        for file_path, file_violations in violations_by_file.items():
            print(f"\n📁 {file_path}:")
            for violation in file_violations:
                print(f"  Line {violation.line_num}: {violation.prop}")
                print(f"    → {violation.line_content}")
                print(f"    💡 Use design tokens or add: /* translator-ignore: reason */")
        
        print("\n" + "=" * 60)
        print("📖 Style Taxonomy Rules (ADR-001):")
        print("   • Box model properties → Design tokens + translator")
        print("   • Visual properties → SCSS") 
        print("   • Use /* translator-ignore: reason */ for exceptions")
        print(f"   • Valid reasons: {', '.join(VALID_IGNORE_REASONS)}")
        
        return True

def main():
    parser = argparse.ArgumentParser(description='Style Linter for Hybrid CSS Architecture')
    parser.add_argument('--file', help='Lint specific SCSS file')
    parser.add_argument('--dir', default='static/scss', help='Directory to lint (default: static/scss)')
    parser.add_argument('--ci', action='store_true', help='CI mode: exit with error code on violations')
    parser.add_argument('--strict', action='store_true', help='Strict mode: stricter validation')
    
    args = parser.parse_args()
    
    linter = StyleLinter(strict_mode=args.strict)
    
    if args.file:
        if not os.path.exists(args.file):
            print(f"❌ File not found: {args.file}")
            sys.exit(1)
        violations = linter.lint_file(args.file)
    else:
        if not os.path.exists(args.dir):
            print(f"❌ Directory not found: {args.dir}")
            sys.exit(1)
        violations = linter.lint_directory(args.dir)
    
    has_violations = linter.report_violations(violations)
    
    if args.ci and has_violations:
        print("\n💥 Style linting failed - fix violations before committing")
        sys.exit(1)
    
    if has_violations:
        print(f"\n🔧 Fix violations and run again: python tools/style_linter.py")
        sys.exit(1 if args.ci else 0)
    else:
        print("\n🎉 All SCSS files comply with Style Taxonomy ADR-001!")

if __name__ == "__main__":
    main() 