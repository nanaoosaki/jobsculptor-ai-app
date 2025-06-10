#!/usr/bin/env python3
"""
Phase 5.1 Results Analysis: C1/C2 Implementation Test
===================================================

Analyze the test results from the production app to understand if our 
C1/C2 safe allocation fix worked as expected.

Expected Results:
1. Both resumes should show bullets (•) instead of numbered lists (1., 2., 3...)
2. numId values should be much higher (5000+ due to PID-salt)
3. No collision between first and second resume

Actual Results (User Report):
- First resume: "list styling" (numbered lists)
- Second resume: "list styling" (numbered lists)

This analysis will help determine:
- Whether C1/C2 fix was applied
- What numId/abstractNumId values were used
- Whether C3 style anchoring is the issue
- Next steps for Phase 5.2/5.3

Created: January 2025
"""

import os
import sys
from pathlib import Path
from zipfile import ZipFile
import xml.etree.ElementTree as ET
from typing import Dict, List, Tuple

def analyze_docx_numbering(docx_path: str) -> Dict:
    """Analyze numbering structure in a DOCX file."""
    results = {
        'file': docx_path,
        'exists': False,
        'numbering_definitions': [],
        'abstract_definitions': [],
        'paragraph_numbering': [],
        'style_references': [],
        'analysis': {}
    }
    
    if not os.path.exists(docx_path):
        print(f"❌ File not found: {docx_path}")
        return results
    
    results['exists'] = True
    
    try:
        with ZipFile(docx_path, 'r') as docx:
            # Analyze numbering.xml
            try:
                numbering_xml = docx.read('word/numbering.xml').decode('utf-8')
                root = ET.fromstring(numbering_xml)
                
                # Find all num definitions
                for num in root.findall('.//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}num'):
                    num_id = num.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}numId')
                    abstract_ref = num.find('.//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}abstractNumId')
                    abstract_id = abstract_ref.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val') if abstract_ref is not None else 'None'
                    
                    results['numbering_definitions'].append({
                        'numId': int(num_id) if num_id else None,
                        'abstractNumId': int(abstract_id) if abstract_id != 'None' else None
                    })
                
                # Find all abstractNum definitions
                for abstract in root.findall('.//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}abstractNum'):
                    abstract_id = abstract.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}abstractNumId')
                    
                    # Get format info for level 0
                    lvl = abstract.find('.//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}lvl[@{http://schemas.openxmlformats.org/wordprocessingml/2006/main}ilvl="0"]')
                    if lvl is not None:
                        num_fmt = lvl.find('.//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}numFmt')
                        lvl_text = lvl.find('.//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}lvlText')
                        
                        fmt_val = num_fmt.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val') if num_fmt is not None else 'unknown'
                        text_val = lvl_text.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val') if lvl_text is not None else 'unknown'
                        
                        results['abstract_definitions'].append({
                            'abstractNumId': int(abstract_id) if abstract_id else None,
                            'format': fmt_val,
                            'text': text_val
                        })
                
            except KeyError:
                print(f"⚠️  No numbering.xml found in {docx_path}")
            
            # Analyze document.xml for paragraph numbering references
            try:
                doc_xml = docx.read('word/document.xml').decode('utf-8')
                doc_root = ET.fromstring(doc_xml)
                
                for para in doc_root.findall('.//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p'):
                    # Look for numbering properties
                    num_pr = para.find('.//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}numPr')
                    if num_pr is not None:
                        num_id_elem = num_pr.find('.//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}numId')
                        ilvl_elem = num_pr.find('.//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}ilvl')
                        
                        num_id = num_id_elem.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val') if num_id_elem is not None else 'None'
                        ilvl = ilvl_elem.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val') if ilvl_elem is not None else '0'
                        
                        # Get paragraph text for context
                        text_content = ""
                        for t in para.findall('.//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t'):
                            if t.text:
                                text_content += t.text
                        
                        results['paragraph_numbering'].append({
                            'numId': int(num_id) if num_id != 'None' else None,
                            'level': int(ilvl),
                            'text_preview': text_content[:50] + '...' if len(text_content) > 50 else text_content
                        })
                
            except KeyError:
                print(f"⚠️  No document.xml found in {docx_path}")
    
    except Exception as e:
        print(f"❌ Error analyzing {docx_path}: {e}")
        results['error'] = str(e)
    
    return results

def compare_with_expectations(results1: Dict, results2: Dict):
    """Compare actual results with our C1/C2 implementation expectations."""
    print("\n" + "="*80)
    print("📊 C1/C2 IMPLEMENTATION RESULTS ANALYSIS")
    print("="*80)
    
    print("\n🎯 EXPECTATIONS vs REALITY:")
    print("Expected after C1/C2 fix:")
    print("  ✅ Both resumes should show bullets (•)")
    print("  ✅ numId values should be 5000+ (PID-salt)")
    print("  ✅ No collisions between documents")
    print("  ✅ abstractNumId should be safely allocated")
    
    print(f"\nActual results (User report):")
    print("  ❌ First resume: 'list styling' (numbered lists)")
    print("  ❌ Second resume: 'list styling' (numbered lists)")
    
    print("\n" + "="*80)
    print("📋 DETAILED DOCUMENT ANALYSIS")
    print("="*80)
    
    for i, results in enumerate([results1, results2], 1):
        if not results['exists']:
            print(f"\n❌ Document {i}: File not found")
            continue
            
        print(f"\n📄 DOCUMENT {i}: {Path(results['file']).name}")
        print("-" * 60)
        
        # Numbering definitions analysis
        print(f"📊 Numbering Definitions ({len(results['numbering_definitions'])}):")
        for num_def in results['numbering_definitions']:
            print(f"  • numId: {num_def['numId']} → abstractNumId: {num_def['abstractNumId']}")
        
        # Abstract definitions analysis
        print(f"\n📊 Abstract Definitions ({len(results['abstract_definitions'])}):")
        for abs_def in results['abstract_definitions']:
            icon = "🔹" if abs_def['format'] == 'bullet' else "🔢" if abs_def['format'] == 'decimal' else "❓"
            print(f"  {icon} abstractNumId: {abs_def['abstractNumId']} | format: {abs_def['format']} | text: '{abs_def['text']}'")
        
        # Paragraph numbering usage
        print(f"\n📊 Paragraph Numbering Usage ({len(results['paragraph_numbering'])}):")
        for para in results['paragraph_numbering'][:5]:  # Show first 5
            print(f"  • numId: {para['numId']} | level: {para['level']} | text: '{para['text_preview']}'")
        if len(results['paragraph_numbering']) > 5:
            print(f"  ... and {len(results['paragraph_numbering']) - 5} more paragraphs")

def analyze_c1_c2_effectiveness(results1: Dict, results2: Dict):
    """Analyze whether C1/C2 fix was effective."""
    print("\n" + "="*80)
    print("🔍 C1/C2 EFFECTIVENESS ANALYSIS")
    print("="*80)
    
    # Check if safe allocation was used
    doc1_nums = [d['numId'] for d in results1['numbering_definitions']] if results1['exists'] else []
    doc2_nums = [d['numId'] for d in results2['numbering_definitions']] if results2['exists'] else []
    
    print(f"\n🔢 numId Ranges:")
    print(f"Document 1: {doc1_nums}")
    print(f"Document 2: {doc2_nums}")
    
    # Check for PID-salt (5000+ range)
    high_nums_doc1 = [n for n in doc1_nums if n and n >= 5000]
    high_nums_doc2 = [n for n in doc2_nums if n and n >= 5000]
    
    print(f"\n🧂 PID-Salt Detection (5000+ range):")
    if high_nums_doc1 or high_nums_doc2:
        print(f"  ✅ PID-salt applied: Doc1={high_nums_doc1}, Doc2={high_nums_doc2}")
        print("  ✅ C1/C2 safe allocation WAS used")
    else:
        print(f"  ❌ No PID-salt detected")
        print("  ❌ C1/C2 safe allocation may NOT have been used")
    
    # Check for collisions
    if results1['exists'] and results2['exists']:
        common_nums = set(doc1_nums) & set(doc2_nums)
        if common_nums:
            print(f"  ⚠️  numId collisions detected: {common_nums}")
        else:
            print(f"  ✅ No numId collisions between documents")
    
    # Analyze why bullets became numbered lists
    print(f"\n🔍 ROOT CAUSE ANALYSIS:")
    
    for i, results in enumerate([results1, results2], 1):
        if not results['exists']:
            continue
            
        bullet_abstracts = [d for d in results['abstract_definitions'] if d['format'] == 'bullet']
        decimal_abstracts = [d for d in results['abstract_definitions'] if d['format'] == 'decimal']
        
        print(f"\nDocument {i}:")
        print(f"  • Bullet definitions: {len(bullet_abstracts)} ({[d['abstractNumId'] for d in bullet_abstracts]})")
        print(f"  • Decimal definitions: {len(decimal_abstracts)} ({[d['abstractNumId'] for d in decimal_abstracts]})")
        
        # Check which format is being used by paragraphs
        if results['paragraph_numbering']:
            used_nums = set(p['numId'] for p in results['paragraph_numbering'] if p['numId'])
            print(f"  • Paragraphs using numIds: {used_nums}")
            
            # Map to abstract definitions
            for num_def in results['numbering_definitions']:
                if num_def['numId'] in used_nums:
                    abstract_format = next((d['format'] for d in results['abstract_definitions'] 
                                          if d['abstractNumId'] == num_def['abstractNumId']), 'unknown')
                    print(f"    - numId {num_def['numId']} → abstractNumId {num_def['abstractNumId']} → format: {abstract_format}")

def provide_next_steps_recommendation(results1: Dict, results2: Dict):
    """Provide recommendations for next steps based on analysis."""
    print("\n" + "="*80)
    print("🎯 NEXT STEPS RECOMMENDATION")
    print("="*80)
    
    # Determine if C1/C2 was applied
    doc1_nums = [d['numId'] for d in results1['numbering_definitions']] if results1['exists'] else []
    doc2_nums = [d['numId'] for d in results2['numbering_definitions']] if results2['exists'] else []
    
    has_high_nums = any(n >= 5000 for n in doc1_nums + doc2_nums if n)
    
    if not has_high_nums:
        print("\n❌ C1/C2 FIX NOT APPLIED")
        print("Possible causes:")
        print("  1. Integration issue - safe allocation not being called")
        print("  2. Code not deployed to test environment")
        print("  3. Fallback path being used instead of safe allocation")
        print("\nRecommended action:")
        print("  🔧 Debug why safe allocation isn't being used")
        print("  🔧 Check if our changes are active in the app")
        
    else:
        print("\n✅ C1/C2 FIX WAS APPLIED")
        print("Safe allocation working, but bullets still showing as numbered lists")
        print("\nPossible causes:")
        print("  1. C3 Style Anchoring issue (O3's prediction)")
        print("  2. Different root cause than numId collision")
        print("  3. Corporate template style conflicts")
        print("\nRecommended action:")
        print("  🚀 Proceed with Phase 5.2 (C3 Style Anchoring Fix)")
        print("  📋 Investigate paragraph style conflicts")
    
    print(f"\n📋 Immediate debugging steps:")
    print(f"  1. Check app logs for 'C1/C2: Allocated safe IDs' messages")
    print(f"  2. Verify our code changes are active in test environment")
    print(f"  3. Test with clean browser session (clear any cached state)")

if __name__ == "__main__":
    print("🚀 Phase 5.1 Results Analysis: C1/C2 Implementation Test")
    print("Analyzing test results from production app...")
    
    # Analyze both documents
    file1 = "tailored_resume_a1f14c2f-52e9-46e8-b961-68d54b05b752.docx"
    file2 = "tailored_resume_a43507f5-c788-460c-9d65-f6ed0e76711c.docx"
    
    print(f"\nAnalyzing: {file1}")
    results1 = analyze_docx_numbering(file1)
    
    print(f"Analyzing: {file2}")
    results2 = analyze_docx_numbering(file2)
    
    # Compare with expectations
    compare_with_expectations(results1, results2)
    
    # Analyze C1/C2 effectiveness
    analyze_c1_c2_effectiveness(results1, results2)
    
    # Provide recommendations
    provide_next_steps_recommendation(results1, results2)
    
    print(f"\n✅ Analysis complete. Review findings above.") 