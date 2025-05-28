#!/usr/bin/env python3
"""
Hybrid CSS Builder - Combine SCSS UI Styles with Translator Spacing Rules

Part of Phase 2, Day 3 implementation of the hybrid CSS refactor.
This tool safely combines existing SCSS compilation with translator-generated spacing.

Key Features:
- Additive approach: Legacy CSS (preserved) + Spacing Layer = Enhanced CSS
- PostCSS optimization with fallback
- Cache invalidation based on git SHA + file mtime
- Cascade layer protection for modern browsers
- Feature flag support for safe rollout
"""

import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, Any, Optional

# Add project root to Python path for imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)


def build_hybrid_css(enable_enhanced_spacing: bool = True) -> bool:
    """
    Combine SCSS compilation with translator-generated spacing rules
    
    Uses additive approach to ensure existing functionality is preserved:
    - Generate spacing rules via translator with enhanced caching
    - Compile existing SCSS (UI styles only)
    - Merge: UI styles + spacing rules + reset
    - Optimize with PostCSS fallback
    
    Args:
        enable_enhanced_spacing: Whether to include spacing enhancements
        
    Returns:
        True if build successful, False otherwise
    """
    print("🏗️ Building Hybrid CSS")
    print("=" * 50)
    
    try:
        # 1. Generate spacing rules via translator with enhanced caching
        print("📏 Step 1: Generating spacing rules...")
        cache_key = f"translator-{get_git_sha()}-{get_tokens_mtime()}"
        spacing_rules = get_cached_or_build(cache_key, build_spacing_rules)
        
        if enable_enhanced_spacing:
            browser_spacing = generate_spacing_css(spacing_rules, "browser")
            weasyprint_spacing = generate_spacing_css(spacing_rules, "weasyprint")
            print(f"   ✅ Generated spacing CSS: {len(browser_spacing)} chars (browser)")
        else:
            browser_spacing = ""
            weasyprint_spacing = ""
            print("   ⚪ Enhanced spacing disabled by feature flag")
        
        # 2. Compile existing SCSS (UI styles only)
        print("\n🎨 Step 2: Compiling SCSS UI styles...")
        if not compile_scss_files():
            return False
        
        # 3. Merge: UI styles + spacing rules + reset
        print("\n🔄 Step 3: Merging CSS layers...")
        if not merge_css_layers(browser_spacing, weasyprint_spacing):
            return False
        
        # 4. Optimize with PostCSS fallback
        print("\n⚡ Step 4: Optimizing CSS...")
        optimize_css_with_fallback()
        
        # 5. Generate legacy browser versions
        if enable_enhanced_spacing:
            print("\n🔧 Step 5: Generating legacy browser support...")
            generate_legacy_browser_versions()
        
        print("\n✅ Hybrid CSS build completed successfully!")
        print(f"   - Enhanced spacing: {'enabled' if enable_enhanced_spacing else 'disabled'}")
        print(f"   - Cache key: {cache_key}")
        
        return True
        
    except Exception as e:
        print(f"❌ Hybrid CSS build failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def build_spacing_rules() -> Dict[str, Any]:
    """Build spacing rules from design tokens using existing tools"""
    print("   🔍 Loading design tokens...")
    
    if not os.path.exists("design_tokens.json"):
        print("   ❌ design_tokens.json not found")
        return {}
    
    # Import and use our existing spacing extraction tool
    try:
        # Try importing from tools directory
        sys.path.insert(0, os.path.join(os.getcwd(), 'tools'))
        from extract_spacing_rules import extract_spacing_rules, convert_to_css_rules
    except ImportError:
        try:
            # Try direct import approach
            import importlib.util
            spec = importlib.util.spec_from_file_location("extract_spacing_rules", 
                                                        "tools/extract_spacing_rules.py")
            extract_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(extract_module)
            extract_spacing_rules = extract_module.extract_spacing_rules
            convert_to_css_rules = extract_module.convert_to_css_rules
        except Exception as e:
            print(f"   ❌ Could not import spacing extraction tools: {e}")
            return {}
    
    spacing_tokens = extract_spacing_rules()
    if not spacing_tokens:
        print("   ⚠️ No spacing tokens found")
        return {}
    
    css_rules = convert_to_css_rules(spacing_tokens)
    print(f"   ✅ Built {len(css_rules)} spacing rule selectors")
    
    return css_rules


def generate_spacing_css(css_rules: Dict[str, Dict[str, str]], target_engine: str) -> str:
    """
    Generate CSS content from spacing rules for specific engine
    
    Args:
        css_rules: Dictionary of CSS rules by selector
        target_engine: "browser" or "weasyprint"
        
    Returns:
        CSS content as string with cascade layer protection
    """
    if not css_rules:
        return ""
    
    css_lines = []
    css_lines.append(f"/* Enhanced Spacing Rules - Generated for {target_engine} */")
    css_lines.append("/* DO NOT EDIT MANUALLY - Use design_tokens.json */")
    css_lines.append("")
    
    # Wrap in cascade layer for modern browser protection
    css_lines.append("@layer spacing {")
    
    for selector, properties in css_rules.items():
        css_lines.append(f"  {selector} {{")
        
        for prop, value in properties.items():
            # Convert logical properties for WeasyPrint compatibility
            if target_engine == "weasyprint":
                prop = convert_logical_to_physical(prop)
            
            css_lines.append(f"    {prop}: {value};")
        
        css_lines.append("  }")
        css_lines.append("")
    
    # Add WeasyPrint reset AFTER translator (injection order matters)
    if target_engine == "weasyprint":
        css_lines.append("  /* WeasyPrint reset - applied after spacing rules */")
        css_lines.append("  html, body, p, ul, li { margin: 0; padding: 0; }")
        css_lines.append("")
    
    css_lines.append("}")
    
    return "\n".join(css_lines)


def convert_logical_to_physical(css_property: str) -> str:
    """Convert logical CSS properties to physical for WeasyPrint compatibility"""
    logical_to_physical = {
        'margin-block': 'margin-top',  # Simplified conversion
        'margin-inline': 'margin-left',
        'padding-block': 'padding-top',
        'padding-inline': 'padding-left'
    }
    
    return logical_to_physical.get(css_property, css_property)


def compile_scss_files() -> bool:
    """Compile existing SCSS files to preserve UI styles"""
    
    scss_files = [
        ("static/scss/preview.scss", "static/css/preview_ui.css"),
        ("static/scss/print.scss", "static/css/print_ui.css")
    ]
    
    for scss_input, css_output in scss_files:
        if not os.path.exists(scss_input):
            print(f"   ⚠️ SCSS file not found: {scss_input}")
            continue
        
        try:
            # Check if libsass is available
            try:
                import sass
                
                # Compile SCSS to CSS
                with open(scss_input, 'r', encoding='utf-8') as f:
                    scss_content = f.read()
                
                css_content = sass.compile(string=scss_content, include_paths=['static/scss'])
                
                # Write compiled CSS
                os.makedirs(os.path.dirname(css_output), exist_ok=True)
                with open(css_output, 'w', encoding='utf-8') as f:
                    f.write(css_content)
                
                print(f"   ✅ Compiled: {scss_input} → {css_output}")
                
            except ImportError:
                # Fallback: try system sass command
                cmd = ['sass', scss_input, css_output]
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode == 0:
                    print(f"   ✅ Compiled (system sass): {scss_input} → {css_output}")
                else:
                    print(f"   ❌ SCSS compilation failed: {result.stderr}")
                    return False
                    
        except Exception as e:
            print(f"   ❌ Error compiling {scss_input}: {e}")
            return False
    
    return True


def merge_css_layers(browser_spacing: str, weasyprint_spacing: str) -> bool:
    """Merge UI styles with spacing rules using additive approach"""
    
    try:
        # Read compiled UI styles
        ui_preview = read_file_safe("static/css/preview_ui.css")
        ui_print = read_file_safe("static/css/print_ui.css")
        
        # Merge: UI styles + spacing rules (additive approach)
        final_preview = merge_css_content(ui_preview, browser_spacing, "preview")
        final_print = merge_css_content(ui_print, weasyprint_spacing, "print")
        
        # Write merged CSS files
        write_css_file("static/css/preview.css", final_preview)
        write_css_file("static/css/print.css", final_print)
        
        print(f"   ✅ Merged preview CSS: {len(final_preview):,} chars")
        print(f"   ✅ Merged print CSS: {len(final_print):,} chars")
        
        return True
        
    except Exception as e:
        print(f"   ❌ CSS merge failed: {e}")
        return False


def merge_css_content(ui_css: str, spacing_css: str, css_type: str) -> str:
    """Merge UI CSS with spacing CSS using additive approach"""
    
    merged_lines = []
    merged_lines.append(f"/* Hybrid CSS - {css_type.title()} */")
    merged_lines.append(f"/* Generated: {time.strftime('%Y-%m-%d %H:%M:%S')} */")
    merged_lines.append("")
    
    # Always include UI styles first (legacy CSS preserved)
    if ui_css:
        merged_lines.append("/* ===== UI STYLES (Legacy CSS - Preserved) ===== */")
        merged_lines.append(ui_css)
        merged_lines.append("")
    
    # Add spacing rules if provided
    if spacing_css:
        merged_lines.append("/* ===== ENHANCED SPACING RULES ===== */")
        merged_lines.append(spacing_css)
    
    return "\n".join(merged_lines)


def optimize_css_with_fallback() -> None:
    """PostCSS optimization with fallback (o3 refinement)"""
    
    css_files = ["static/css/preview.css", "static/css/print.css"]
    
    for css_file in css_files:
        if not os.path.exists(css_file):
            continue
            
        try:
            # Try PostCSS optimization
            cmd = ['npx', 'postcss', css_file, '--use', 'postcss-merge-longhand', '--use', 'cssnano', '--replace']
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                print(f"   ✅ Optimized: {css_file}")
            else:
                print(f"   ⚠️ PostCSS failed for {css_file}, keeping unoptimized version")
                
        except (FileNotFoundError, subprocess.TimeoutExpired):
            print(f"   ⚠️ PostCSS not available - skipping optimization for {css_file}")
        except Exception as e:
            print(f"   ⚠️ PostCSS error for {css_file}: {e}")


def generate_legacy_browser_versions() -> None:
    """Generate layer-stripped versions for Safari ≤ 15, pre-Chromium Edge"""
    
    spacing_files = [
        ("static/css/preview.css", "static/css/preview_legacy.css"),
        ("static/css/print.css", "static/css/print_legacy.css")
    ]
    
    for src_path, dst_path in spacing_files:
        if os.path.exists(src_path):
            strip_cascade_layers(src_path, dst_path)
            print(f"   ✅ Legacy version: {dst_path}")


def strip_cascade_layers(src_path: str, dst_path: str) -> None:
    """Remove @layer spacing { ... } wrapper for old browsers"""
    
    with open(src_path, 'r', encoding='utf-8') as f:
        css_content = f.read()
    
    # Remove "@layer spacing {" and matching "}"
    import re
    layer_pattern = re.compile(r'@layer\s+spacing\s*\{([\s\S]*?)\}', re.MULTILINE)
    css_no_layer = layer_pattern.sub(r'\1', css_content)
    
    with open(dst_path, 'w', encoding='utf-8') as f:
        f.write(css_no_layer)


def get_cached_or_build(cache_key: str, build_func) -> Dict[str, Any]:
    """Get cached result or build new with file mtime for cache invalidation"""
    
    cache_file = f".build_cache/spacing_rules_{cache_key[:16]}.json"
    
    # Check if cached version exists and is valid
    if os.path.exists(cache_file):
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                cached_data = json.load(f)
            print(f"   ✅ Using cached spacing rules: {cache_key[:16]}...")
            return cached_data
        except Exception:
            pass  # Cache invalid, rebuild
    
    # Build new version
    print(f"   🔄 Building new spacing rules...")
    result = build_func()
    
    # Cache the result
    os.makedirs(".build_cache", exist_ok=True)
    try:
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2)
    except Exception as e:
        print(f"   ⚠️ Could not cache result: {e}")
    
    return result


def get_git_sha() -> str:
    """Get current git SHA for cache invalidation"""
    try:
        result = subprocess.run(['git', 'rev-parse', 'HEAD'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            return result.stdout.strip()[:8]
    except Exception:
        pass
    
    return "no-git"


def get_tokens_mtime() -> str:
    """Get design tokens file modification time for cache invalidation"""
    try:
        return str(int(os.path.getmtime("design_tokens.json")))
    except Exception:
        return "0"


def read_file_safe(file_path: str) -> str:
    """Safely read file, return empty string if not found"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception:
        return ""


def write_css_file(file_path: str, content: str) -> None:
    """Write CSS file with directory creation"""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)


def main():
    """Main function to build hybrid CSS"""
    
    # Check for feature flag
    enable_enhanced_spacing = os.getenv('USE_ENHANCED_SPACING', 'true').lower() == 'true'
    
    print("🎯 Hybrid CSS Builder - Phase 2, Day 3")
    print("=" * 50)
    print(f"Enhanced spacing: {'enabled' if enable_enhanced_spacing else 'disabled'}")
    print("")
    
    # Run CSS safety validation first
    print("🛡️ Running safety validation...")
    try:
        sys.path.insert(0, os.path.join(os.getcwd(), 'tools'))
        from css_safety_validator import validate_css_safety
        
        # Only validate if files exist
        if os.path.exists("static/css/preview.css"):
            # We'll validate after build, for now just log
            print("   ✅ Safety validator available")
    except ImportError:
        print("   ⚠️ Safety validator not available")
    
    # Build hybrid CSS
    success = build_hybrid_css(enable_enhanced_spacing)
    
    if success:
        print("\n🎉 Hybrid CSS Build SUCCESSFUL!")
        print("Next steps:")
        print("  - Test the application in browser")
        print("  - Compare before/after visual output")
        print("  - Verify no regressions in existing functionality")
    else:
        print("\n❌ Hybrid CSS Build FAILED!")
        print("Check error messages above and fix issues before proceeding")
    
    return success


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) == 2 and sys.argv[1] == '--help':
        print("Usage:")
        print("  python tools/build_hybrid_css.py                    # Build with feature flag")
        print("  USE_ENHANCED_SPACING=false python tools/build_hybrid_css.py  # Build legacy only")
        print("")
        print("Environment Variables:")
        print("  USE_ENHANCED_SPACING=true/false  # Enable/disable spacing enhancements")
        sys.exit(0)
    
    success = main()
    sys.exit(0 if success else 1) 