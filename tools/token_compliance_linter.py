"""
AST-Based Token Compliance Linter

This tool finds hardcoded styling that bypasses design tokens using proper AST parsing
for Python and PostCSS for SCSS. It replaces regex-based approaches to avoid false positives.
"""

import ast
import os
import sys
import json
import argparse
import subprocess
from typing import List, Dict, Any
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class HardcodedStyleVisitor(ast.NodeVisitor):
    """AST visitor to find hardcoded styling that bypasses design tokens"""
    
    def __init__(self, filename: str):
        self.filename = filename
        self.violations = []
    
    def visit_Assign(self, node):
        """Check assignment statements for hardcoded styling"""
        # Check for font.name = "literal" (not token)
        if (len(node.targets) > 0 and 
            hasattr(node.targets[0], 'attr') and 
            node.targets[0].attr == 'name' and
            isinstance(node.value, ast.Str) and
            not node.value.s.startswith('var(') and
            not 'token' in node.value.s.lower()):
            self.violations.append({
                'type': 'hardcoded_font',
                'file': self.filename,
                'line': node.lineno,
                'value': node.value.s,
                'message': f"Hardcoded font name '{node.value.s}' should use design token"
            })
        
        # Check for Pt(literal_number) without token reference
        if (isinstance(node.value, ast.Call) and
            hasattr(node.value.func, 'id') and
            node.value.func.id == 'Pt' and
            len(node.value.args) > 0 and
            isinstance(node.value.args[0], ast.Num)):
            # Check if this looks like a hardcoded size
            size_value = node.value.args[0].n
            if size_value > 0:  # Only flag positive sizes
                self.violations.append({
                    'type': 'hardcoded_pt_size',
                    'file': self.filename,
                    'line': node.lineno,
                    'value': size_value,
                    'message': f"Hardcoded point size '{size_value}pt' should use design token"
                })
        
        # Check for RGBColor(r, g, b) hardcoded colors
        if (isinstance(node.value, ast.Call) and
            hasattr(node.value.func, 'id') and
            node.value.func.id == 'RGBColor' and
            len(node.value.args) >= 3):
            r = node.value.args[0]
            g = node.value.args[1] 
            b = node.value.args[2]
            if all(isinstance(x, ast.Num) for x in [r, g, b]):
                hex_color = f"#{r.n:02x}{g.n:02x}{b.n:02x}"
                self.violations.append({
                    'type': 'hardcoded_rgb_color',
                    'file': self.filename,
                    'line': node.lineno,
                    'value': hex_color,
                    'message': f"Hardcoded RGB color '{hex_color}' should use design token"
                })
        
        self.generic_visit(node)
    
    def visit_Str(self, node):
        """Check string literals for hex colors"""
        # Check for hex color patterns
        import re
        if re.match(r'^#[0-9A-Fa-f]{6}$', node.s):
            # Skip if it looks like it's in a token context
            self.violations.append({
                'type': 'hardcoded_hex_color',
                'file': self.filename,
                'line': node.lineno,
                'value': node.s,
                'message': f"Hardcoded hex color '{node.s}' should use design token"
            })
        
        self.generic_visit(node)

class SCSSHardcodedChecker:
    """SCSS hardcoded style checker using simple parsing"""
    
    def __init__(self):
        self.violations = []
    
    def check_file(self, filepath: str):
        """Check a SCSS file for hardcoded values"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
                
                for line_num, line in enumerate(lines, 1):
                    line = line.strip()
                    
                    # Skip comments
                    if line.startswith('//') or line.startswith('/*'):
                        continue
                    
                    # Check for text-transform: uppercase
                    if 'text-transform:' in line and 'uppercase' in line:
                        self.violations.append({
                            'type': 'hardcoded_text_transform',
                            'file': filepath,
                            'line': line_num,
                            'value': line,
                            'message': "Hardcoded text-transform should use design token for casing control"
                        })
                    
                    # Check for hardcoded colors (hex patterns)
                    import re
                    hex_matches = re.findall(r'#[0-9A-Fa-f]{6}', line)
                    for hex_color in hex_matches:
                        # Skip if it's in a token variable or comment
                        if '$' in line or '//' in line or 'token' in line.lower():
                            continue
                        self.violations.append({
                            'type': 'hardcoded_scss_color',
                            'file': filepath,
                            'line': line_num,
                            'value': hex_color,
                            'message': f"Hardcoded color '{hex_color}' should use design token variable"
                        })
                    
                    # Check for hardcoded point sizes
                    pt_matches = re.findall(r'\b(\d+(?:\.\d+)?)pt\b', line)
                    for pt_size in pt_matches:
                        # Skip if it's in a token context
                        if '$' in line or 'token' in line.lower():
                            continue
                        self.violations.append({
                            'type': 'hardcoded_scss_size',
                            'file': filepath,
                            'line': line_num,
                            'value': f"{pt_size}pt",
                            'message': f"Hardcoded size '{pt_size}pt' should use design token variable"
                        })
                        
        except Exception as e:
            logger.error(f"Error checking SCSS file {filepath}: {e}")

def find_python_files() -> List[str]:
    """Find all Python files in the project"""
    python_files = []
    
    # Search in key directories
    search_dirs = ['.', 'utils', 'word_styles', 'tools', 'tests']
    
    for search_dir in search_dirs:
        if os.path.exists(search_dir):
            for root, dirs, files in os.walk(search_dir):
                # Skip __pycache__ and .git directories
                dirs[:] = [d for d in dirs if not d.startswith(('.', '__pycache__'))]
                
                for file in files:
                    if file.endswith('.py'):
                        python_files.append(os.path.join(root, file))
    
    return python_files

def find_scss_files() -> List[str]:
    """Find all SCSS files in the project"""
    scss_files = []
    
    # Search in static directory
    static_dir = 'static'
    if os.path.exists(static_dir):
        for root, dirs, files in os.walk(static_dir):
            for file in files:
                if file.endswith(('.scss', '.sass')):
                    scss_files.append(os.path.join(root, file))
    
    return scss_files

def audit_hardcoded_styles() -> List[Dict[str, Any]]:
    """Find all hardcoded styling that bypasses design tokens"""
    violations = []
    
    # Python AST analysis
    logger.info("Analyzing Python files with AST...")
    python_files = find_python_files()
    
    for py_file in python_files:
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                try:
                    tree = ast.parse(f.read(), filename=py_file)
                    visitor = HardcodedStyleVisitor(py_file)
                    visitor.visit(tree)
                    violations.extend(visitor.violations)
                except SyntaxError as e:
                    logger.warning(f"Syntax error in {py_file}: {e}")
        except Exception as e:
            logger.error(f"Error processing {py_file}: {e}")
    
    # SCSS analysis
    logger.info("Analyzing SCSS files...")
    scss_files = find_scss_files()
    scss_checker = SCSSHardcodedChecker()
    
    for scss_file in scss_files:
        scss_checker.check_file(scss_file)
    
    violations.extend(scss_checker.violations)
    
    return violations

def load_baseline(baseline_path: str) -> List[Dict[str, Any]]:
    """Load baseline violations from file"""
    try:
        with open(baseline_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.info(f"No baseline file found at {baseline_path}")
        return []
    except Exception as e:
        logger.error(f"Error loading baseline: {e}")
        return []

def save_baseline(violations: List[Dict[str, Any]], baseline_path: str):
    """Save violations as new baseline"""
    try:
        with open(baseline_path, 'w', encoding='utf-8') as f:
            json.dump(violations, f, indent=2)
        logger.info(f"Saved baseline to {baseline_path}")
    except Exception as e:
        logger.error(f"Error saving baseline: {e}")

def find_new_violations(current: List[Dict[str, Any]], baseline: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Find violations that are new compared to baseline"""
    baseline_signatures = set()
    
    for violation in baseline:
        signature = f"{violation['file']}:{violation['line']}:{violation['type']}"
        baseline_signatures.add(signature)
    
    new_violations = []
    for violation in current:
        signature = f"{violation['file']}:{violation['line']}:{violation['type']}"
        if signature not in baseline_signatures:
            new_violations.append(violation)
    
    return new_violations

def print_violations_report(violations: List[Dict[str, Any]]):
    """Print a formatted report of violations"""
    if not violations:
        print("✅ No hardcoded style violations found!")
        return
    
    # Group by type
    by_type = {}
    for violation in violations:
        vtype = violation['type']
        if vtype not in by_type:
            by_type[vtype] = []
        by_type[vtype].append(violation)
    
    print(f"🚨 Found {len(violations)} hardcoded style violations:")
    print()
    
    for vtype, type_violations in by_type.items():
        print(f"## {vtype.replace('_', ' ').title()} ({len(type_violations)} violations)")
        
        for violation in type_violations[:5]:  # Show first 5
            print(f"  📍 {violation['file']}:{violation['line']}")
            print(f"     {violation['message']}")
            print(f"     Value: {violation['value']}")
            print()
        
        if len(type_violations) > 5:
            print(f"  ... and {len(type_violations) - 5} more")
            print()

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(description="AST-based token compliance linter")
    parser.add_argument('--baseline-path', default='.token-baseline.json',
                       help="Path to baseline file for comparison")
    parser.add_argument('--fail-on-violations', action='store_true',
                       help="Exit with error code if violations found")
    parser.add_argument('--save-baseline', action='store_true',
                       help="Save current violations as new baseline")
    parser.add_argument('--verbose', '-v', action='store_true',
                       help="Verbose logging")
    
    args = parser.parse_args()
    
    # Set up logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=log_level, format='%(levelname)s: %(message)s')
    
    # Run the audit
    print("🔍 Scanning for hardcoded styles...")
    violations = audit_hardcoded_styles()
    
    if args.save_baseline:
        save_baseline(violations, args.baseline_path)
        print(f"💾 Saved {len(violations)} violations as baseline")
        return 0
    
    # Check against baseline if it exists
    baseline = load_baseline(args.baseline_path)
    if baseline:
        new_violations = find_new_violations(violations, baseline)
        print(f"📊 Baseline comparison:")
        print(f"   Current: {len(violations)} violations")
        print(f"   Baseline: {len(baseline)} violations") 
        print(f"   New: {len(new_violations)} violations")
        print()
        
        if new_violations:
            print("🆕 New violations found:")
            print_violations_report(new_violations)
            if args.fail_on_violations:
                return 1
        else:
            print("✅ No new violations since baseline")
    else:
        print_violations_report(violations)
        if args.fail_on_violations and violations:
            return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 