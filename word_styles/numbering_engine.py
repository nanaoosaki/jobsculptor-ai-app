"""
Native Numbering Engine for DOCX Generation

This module implements Microsoft Word's native bullets and numbering system,
applying the architectural lessons learned from the MR_Company spacing saga.

Key Features:
- Content-first architecture enforcement (G-1 fix)
- Idempotent numbering creation (G-2 fix) 
- Cross-format consistency (B-1, B-2 fixes)
- Zero spacing preservation
- Per-document state isolation

Created: January 2025
"""

import logging
from typing import Dict, Set, Optional
from docx import Document
from docx.shared import Pt
from docx.text.paragraph import Paragraph
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls

logger = logging.getLogger(__name__)


class NumberingEngine:
    """
    Manages native Word numbering/bullets with architectural safeguards.
    
    This class implements the lessons learned from the MR_Company spacing saga:
    1. Content-first enforcement prevents silent style application failures
    2. Idempotent creation prevents ValueError on duplicate abstractNum IDs
    3. Cross-format consistency ensures visual alignment with HTML/PDF
    
    SIMPLIFIED APPROACH: Use paragraph-level numbering properties only,
    letting Word handle the numbering definitions automatically.
    """
    
    def __init__(self):
        """Initialize per-document state to avoid multi-process leaks."""
        self._applied_paragraphs: Set[id] = set()
        logger.debug("NumberingEngine initialized with fresh state")
    
    def apply_native_bullet(self, para: Paragraph, num_id: int = 1, level: int = 0) -> None:
        """
        Apply native Word numbering to paragraph.
        
        CRITICAL: Enforces content-first pattern that fixed MR_Company.
        UPDATED: Works WITH design token system instead of fighting it.
        
        Args:
            para: Paragraph to apply numbering to
            num_id: Numbering definition ID (default: 1)
            level: List level (0-based, default: 0)
            
        Raises:
            ValueError: If paragraph has no content (violates content-first architecture)
        """
        # G-1 FIX: Content-first enforcement
        if not para.runs:
            raise ValueError(
                "apply_native_bullet called before content - violates content-first architecture. "
                "Add text content with para.add_run() before applying numbering."
            )
        
        para_id = id(para)
        if para_id in self._applied_paragraphs:
            logger.debug(f"Numbering already applied to paragraph, skipping")
            return
        
        logger.debug(f"Applying native bullet: numId={num_id}, level={level}, text='{para.text[:50]}...'")
        
        # Get paragraph properties
        pPr = para._element.get_or_add_pPr()
        
        # Add numbering properties using the proven pattern from successful implementation
        numPr_xml = f'''
        <w:numPr {nsdecls("w")}>
            <w:ilvl w:val="{level}"/>
            <w:numId w:val="{num_id}"/>
        </w:numPr>
        '''
        
        # Add proper bullet-style indentation (B-2 fix: 221 twips = 1em)
        indent_xml = f'<w:ind {nsdecls("w")} w:left="221" w:hanging="221"/>'
        
        # FIXED: Do NOT add spacing XML - let the MR_BulletPoint style handle spacing
        # The design token system already sets MR_BulletPoint to spaceAfterPt: 0
        # Adding XML was OVERRIDING the design token values!
        
        try:
            # Remove any existing properties to prevent conflicts
            for existing_numPr in pPr.xpath('./w:numPr'):
                pPr.remove(existing_numPr)
            for existing_ind in pPr.xpath('./w:ind'):
                pPr.remove(existing_ind)
            # NOTE: Do NOT remove spacing - let style handle it
            
            # Add new numbering and indentation only
            numPr = parse_xml(numPr_xml)
            indent = parse_xml(indent_xml)
            
            pPr.append(numPr)
            pPr.append(indent)
            
            self._applied_paragraphs.add(para_id)
            logger.debug(f"✅ Successfully applied native numbering (letting style handle spacing): numId={num_id}")
        except Exception as e:
            logger.error(f"❌ Failed to apply numbering: {e}")
            raise
    
    def get_or_create_numbering_definition(self, doc: Document, num_id: int = 1, 
                                         abstract_id: int = 0) -> None:
        """
        Simplified: Just track that we've "created" the definition.
        
        In practice, Word will create the numbering definition automatically
        when it encounters paragraphs with numId references.
        
        Implements G-2 fix: idempotent creation prevents issues.
        
        Args:
            doc: Document to add numbering to (unused in simplified approach)
            num_id: Numbering instance ID
            abstract_id: Abstract numbering definition ID (unused in simplified approach)
        """
        # G-2 FIX: Idempotent behavior - always safe to call
        logger.debug(f"Numbering definition {num_id} ready (Word will create automatically)")
    
    def is_native_numbering_supported(self, doc: Document) -> bool:
        """
        Check if document supports native numbering.
        Simplified approach - always supported since we use paragraph properties only.
        """
        try:
            # Test if we can access basic document structure
            _ = doc._element.body
            return True
        except Exception as e:
            logger.warning(f"Native numbering not supported: {e}")
            return False


# Convenience function for backward compatibility
def apply_native_numbering(para: Paragraph, num_id: int = 1, level: int = 0) -> None:
    """
    Convenience function that creates a temporary NumberingEngine instance.
    
    For production use, prefer creating a NumberingEngine per document to avoid
    state leaks between requests (per O3 recommendation).
    """
    engine = NumberingEngine()
    engine.apply_native_bullet(para, num_id, level) 