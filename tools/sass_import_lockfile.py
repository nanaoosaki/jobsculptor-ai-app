#!/usr/bin/env python3
"""
Sass Import Lockfile - Prevent Missing Partials Disaster

Part of Phase 1, Day 1 implementation of the hybrid CSS refactor.
This tool prevents missing partials from causing empty CSS output.

Lessons Learned from May 26 Disaster:
- Missing SCSS partials can make Sass output empty files
- Empty CSS files break the entire visual styling
- Need to detect broken imports before they reach production

Key Features:
- Generates sass-imports.lock with file hashes
- Validates all @import and @use statements resolve to existing files
- CI integration to catch missing partials early
- Prevents silent SCSS compilation failures
"""

import hashlib
import glob
import os
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple


def generate_sass_lockfile(scss_root: str = "static/scss") -> bool:
    """
    Generate sass-imports.lock to prevent missing partials
    
    Creates a lockfile with all SCSS imports and their file hashes.
    This allows CI to detect when imports are broken before Sass compilation.
    
    Args:
        scss_root: Root directory containing SCSS files
        
    Returns:
        True if lockfile generated successfully
    """
    print(f"🔒 Generating Sass import lockfile from {scss_root}")
    
    if not os.path.exists(scss_root):
        print(f"❌ SCSS root directory not found: {scss_root}")
        return False
    
    # Find all SCSS files and their imports
    scss_files = glob.glob(f'{scss_root}/**/*.scss', recursive=True)
    imports = {}
    
    print(f"📂 Found {len(scss_files)} SCSS files:")
    
    for file_path in scss_files:
        print(f"   - {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            print(f"⚠️ Could not read {file_path} (encoding issue)")
            continue
            
        # Extract @import statements (legacy syntax)
        import_lines = re.findall(r'@import\s+["\']([^"\']+)["\'];?', content)
        
        # Extract @use statements (modern syntax)  
        use_lines = re.findall(r'@use\s+["\']([^"\']+)["\'](?:\s+as\s+[^;]*)?;?', content)
        
        # Combine all dependencies
        all_dependencies = import_lines + use_lines
        
        if all_dependencies:
            print(f"      Found {len(all_dependencies)} dependencies:")
        
        for import_path in all_dependencies:
            # Skip built-in Sass modules
            if import_path.startswith('sass:'):
                print(f"         ⚪ {import_path} (built-in module)")
                continue
                
            # Resolve relative imports
            full_import_path = resolve_import_path(file_path, import_path)
            
            if os.path.exists(full_import_path):
                # Calculate file hash
                with open(full_import_path, 'rb') as f:
                    file_hash = hashlib.md5(f.read()).hexdigest()
                imports[full_import_path] = file_hash
                print(f"         ✅ {import_path} → {full_import_path}")
            else:
                print(f"         ❌ Missing: {import_path} → {full_import_path}")
                return False
    
    # Write lockfile
    lockfile_content = []
    lockfile_content.append("# Sass Import Lockfile")
    lockfile_content.append("# Generated automatically - do not edit manually")
    lockfile_content.append("# Tracks @import and @use dependencies")
    lockfile_content.append("# Format: filepath:md5hash")
    lockfile_content.append("")
    
    for file_path in sorted(imports.keys()):
        lockfile_content.append(f"{file_path}:{imports[file_path]}")
    
    lockfile_path = "sass-imports.lock"
    with open(lockfile_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lockfile_content))
    
    print(f"\n✅ Generated {lockfile_path} with {len(imports)} dependencies")
    print(f"   - Lockfile size: {len('\n'.join(lockfile_content))} chars")
    
    return True


def validate_sass_lockfile(lockfile_path: str = "sass-imports.lock") -> bool:
    """
    CI step: detect removed/renamed partials before Sass compilation
    
    Validates that all imports in the lockfile still exist and haven't changed.
    This catches missing partials before they cause empty CSS output.
    
    Args:
        lockfile_path: Path to sass-imports.lock file
        
    Returns:
        True if all imports are valid, False if any missing/changed
    """
    print(f"🔍 Validating Sass imports from {lockfile_path}")
    
    if not os.path.exists(lockfile_path):
        print(f"❌ Sass imports lockfile missing: {lockfile_path}")
        print("   Run 'python tools/sass_import_lockfile.py --generate' to create it")
        return False
    
    try:
        with open(lockfile_path, 'r', encoding='utf-8') as f:
            lockfile_entries = [line.strip() for line in f.readlines() 
                              if line.strip() and not line.startswith('#')]
    except UnicodeDecodeError:
        print(f"❌ Could not read lockfile: {lockfile_path}")
        return False
    
    missing_files = []
    changed_files = []
    total_imports = 0
    
    for entry in lockfile_entries:
        if ':' not in entry:
            continue
            
        file_path, expected_hash = entry.split(':', 1)
        total_imports += 1
        
        if not os.path.exists(file_path):
            missing_files.append(file_path)
        else:
            # Check if file hash changed
            with open(file_path, 'rb') as f:
                current_hash = hashlib.md5(f.read()).hexdigest()
            
            if current_hash != expected_hash:
                changed_files.append((file_path, expected_hash, current_hash))
    
    # Report results
    print(f"\n📊 Sass Import Validation Results:")
    print(f"   - Total dependencies checked: {total_imports}")
    print(f"   - Missing files: {len(missing_files)}")
    print(f"   - Changed files: {len(changed_files)}")
    
    if missing_files:
        print("\n❌ Missing SCSS partials detected:")
        for file_path in missing_files:
            print(f"   {file_path}")
        print("\n💡 This would cause Sass compilation to fail silently!")
        
    if changed_files:
        print("\n⚠️ Changed SCSS partials detected:")
        for file_path, old_hash, new_hash in changed_files:
            print(f"   {file_path} ({old_hash[:8]} → {new_hash[:8]})")
        print("\n💡 Run 'python tools/sass_import_lockfile.py --generate' to update lockfile")
    
    if missing_files or changed_files:
        return False
    
    print("\n✅ All SCSS partials present and unchanged")
    return True


def resolve_import_path(importer_file: str, import_path: str) -> str:
    """
    Resolve SCSS import path to absolute file path
    
    SCSS import resolution rules:
    1. Relative to importing file directory
    2. Add .scss extension if missing
    3. Add _ prefix for partials if missing
    4. Handle sass: module imports (built-in modules)
    
    Args:
        importer_file: Path to file doing the import
        import_path: Import path from @import or @use statement
        
    Returns:
        Absolute path to imported file
    """
    # Skip built-in Sass modules
    if import_path.startswith('sass:'):
        return ""  # Built-in module, no file to track
    
    importer_dir = os.path.dirname(importer_file)
    
    # Handle relative paths
    if not import_path.startswith('/'):
        base_path = os.path.join(importer_dir, import_path)
    else:
        base_path = import_path[1:]  # Remove leading slash
    
    # Try different variations of the import path
    variations = [
        base_path,                           # Exact path
        f"{base_path}.scss",                # Add .scss extension
        f"{base_path}.css",                 # Add .css extension
    ]
    
    # Also try with _ prefix for partials
    dir_part = os.path.dirname(base_path)
    name_part = os.path.basename(base_path)
    
    if not name_part.startswith('_'):
        partial_variations = [
            os.path.join(dir_part, f"_{name_part}"),
            os.path.join(dir_part, f"_{name_part}.scss"),
            os.path.join(dir_part, f"_{name_part}.css")
        ]
        variations.extend(partial_variations)
    
    # Return first existing variation
    for variation in variations:
        abs_path = os.path.abspath(variation)
        if os.path.exists(abs_path):
            return abs_path
    
    # Return the most likely path even if it doesn't exist
    return os.path.abspath(f"{base_path}.scss")


def analyze_import_dependencies(scss_root: str = "static/scss") -> None:
    """
    Analyze and visualize SCSS import dependencies
    
    Useful for understanding the import graph and potential circular dependencies.
    """
    print("🕸️ Analyzing SCSS Import Dependencies")
    print("=" * 50)
    
    scss_files = glob.glob(f'{scss_root}/**/*.scss', recursive=True)
    dependencies = {}
    
    for file_path in scss_files:
        rel_path = os.path.relpath(file_path)
        dependencies[rel_path] = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            continue
            
        # Find both @import and @use statements
        import_lines = re.findall(r'@import\s+["\']([^"\']+)["\'];?', content)
        use_lines = re.findall(r'@use\s+["\']([^"\']+)["\'](?:\s+as\s+[^;]*)?;?', content)
        
        all_deps = import_lines + use_lines
        
        for import_path in all_deps:
            # Skip built-in modules
            if import_path.startswith('sass:'):
                continue
                
            full_import_path = resolve_import_path(file_path, import_path)
            rel_import_path = os.path.relpath(full_import_path)
            dependencies[rel_path].append((import_path, rel_import_path))
    
    # Print dependency tree
    for file_path, imports in dependencies.items():
        print(f"\n📄 {file_path}")
        if imports:
            for original_path, resolved_path in imports:
                exists = "✅" if os.path.exists(resolved_path) else "❌"
                print(f"   {exists} {original_path} → {resolved_path}")
        else:
            print("   (no dependencies)")
    
    print("=" * 50)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) == 2:
        command = sys.argv[1]
        
        if command == '--generate':
            success = generate_sass_lockfile()
            sys.exit(0 if success else 1)
            
        elif command == '--validate':
            success = validate_sass_lockfile()
            sys.exit(0 if success else 1)
            
        elif command == '--analyze':
            analyze_import_dependencies()
            sys.exit(0)
            
        else:
            print(f"Unknown command: {command}")
            sys.exit(1)
    
    elif len(sys.argv) == 1:
        # Default: validate if lockfile exists, otherwise generate
        if os.path.exists("sass-imports.lock"):
            success = validate_sass_lockfile()
        else:
            success = generate_sass_lockfile()
        sys.exit(0 if success else 1)
    
    else:
        print("Usage:")
        print("  python tools/sass_import_lockfile.py              # Auto: validate or generate")
        print("  python tools/sass_import_lockfile.py --generate   # Generate lockfile")
        print("  python tools/sass_import_lockfile.py --validate   # Validate lockfile")
        print("  python tools/sass_import_lockfile.py --analyze    # Analyze dependencies")
        sys.exit(1) 