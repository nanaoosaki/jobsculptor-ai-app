#!/usr/bin/env python3

import re
import sys
from pathlib import Path
from typing import List, Tuple

def strip_box_model_properties(scss_content: str) -> Tuple[str, List[str]]:
    """
    Strip hardcoded box-model properties from SCSS content.
    Returns (cleaned_content, list_of_changes)
    """
    
    changes = []
    
    # Box model properties to remove
    box_model_props = [
        'margin', 'margin-top', 'margin-bottom', 'margin-left', 'margin-right',
        'margin-block', 'margin-inline',
        'padding', 'padding-top', 'padding-bottom', 'padding-left', 'padding-right', 
        'padding-block', 'padding-inline',
        'gap', 'row-gap', 'column-gap'
    ]
    
    lines = scss_content.split('\n')
    cleaned_lines = []
    
    for i, line in enumerate(lines):
        original_line = line
        line_number = i + 1
        
        # Skip if line contains translator-ignore comment
        if '/* translator-ignore */' in line:
            cleaned_lines.append(line)
            continue
            
        # Check for box model properties
        stripped = False
        for prop in box_model_props:
            # Match property declarations (but not in comments)
            pattern = r'^\s*' + re.escape(prop) + r'\s*:\s*[^;]*;'
            if re.search(pattern, line) and not line.strip().startswith('//'):
                changes.append(f"Line {line_number}: Removed '{line.strip()}'")
                # Comment out the line instead of removing completely
                cleaned_lines.append(f"  // REMOVED BY TRANSLATOR: {line.strip()}")
                stripped = True
                break
        
        if not stripped:
            cleaned_lines.append(line)
    
    return '\n'.join(cleaned_lines), changes

def backup_file(file_path: Path) -> Path:
    """Create a backup of the original file"""
    backup_path = file_path.with_suffix(f'{file_path.suffix}.backup')
    backup_path.write_text(file_path.read_text())
    return backup_path

def main():
    if len(sys.argv) < 2:
        print("Usage: python tools/migrate_scss.py <scss_file>")
        print("Example: python tools/migrate_scss.py static/scss/_resume.scss")
        sys.exit(1)
    
    scss_file = Path(sys.argv[1])
    
    if not scss_file.exists():
        print(f"❌ File not found: {scss_file}")
        sys.exit(1)
    
    print(f"🔧 Migrating SCSS file: {scss_file}")
    
    # Read original content
    original_content = scss_file.read_text()
    
    # Create backup
    backup_path = backup_file(scss_file)
    print(f"📦 Backup created: {backup_path}")
    
    # Strip box model properties
    cleaned_content, changes = strip_box_model_properties(original_content)
    
    # Write cleaned content
    scss_file.write_text(cleaned_content)
    
    # Report changes
    if changes:
        print(f"✅ Successfully migrated {scss_file}")
        print(f"📊 Changes made ({len(changes)} total):")
        for change in changes[:10]:  # Show first 10 changes
            print(f"  {change}")
        if len(changes) > 10:
            print(f"  ... and {len(changes) - 10} more changes")
        
        print(f"\n🎯 Next Steps:")
        print(f"1. Review changes in {scss_file}")
        print(f"2. Run: python tools/build_hybrid_css.py")
        print(f"3. Test that spacing now comes from translator layer")
        print(f"4. If issues, restore from: {backup_path}")
    else:
        print("ℹ️ No box-model properties found to migrate")
    
    return len(changes)

if __name__ == "__main__":
    main() 