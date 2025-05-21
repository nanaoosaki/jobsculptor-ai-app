"""
XML Utilities for Word Styling

This module provides utility functions for generating Word XML styling nodes
and handling measurement conversions between points and twips.
"""

import logging
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

logger = logging.getLogger(__name__)

def twips_from_pt(pt_value):
    """
    Convert points to twips. Word uses twips (twentieth of a point) for many measurements.
    
    Args:
        pt_value (float): Value in points
        
    Returns:
        int: Value in twips (1 pt = 20 twips)
    """
    return int(pt_value * 20)

def pt_from_twips(twips_value):
    """
    Convert twips to points.
    
    Args:
        twips_value (int): Value in twips
        
    Returns:
        float: Value in points
    """
    return float(twips_value) / 20

def make_spacing_node(before=0, after=0, line=None, line_rule="auto", 
                      before_auto=False, after_auto=False):
    """
    Generate a Word XML spacing node with the specified attributes.
    
    Args:
        before (int): Space before in twips
        after (int): Space after in twips
        line (int, optional): Line spacing in twips (e.g., 276 for 13.8pt)
        line_rule (str): Line spacing rule ("auto", "exact", or "atLeast")
        before_auto (bool): Whether to use auto spacing before
        after_auto (bool): Whether to use auto spacing after
        
    Returns:
        Element: XML element for paragraph spacing
    """
    # Build attributes string with proper namespaces
    attrs = []
    
    if before is not None:
        attrs.append(f'w:before="{before}"')
    
    if after is not None:
        attrs.append(f'w:after="{after}"')
    
    if line is not None:
        attrs.append(f'w:line="{line}"')
        attrs.append(f'w:lineRule="{line_rule}"')
    
    # Always explicitly set autospacing flags to prevent Word's default behavior
    # For boxed headers we want these OFF to ensure precise control
    if before_auto:
        attrs.append('w:beforeAutospacing="1"')
    else:
        attrs.append('w:beforeAutospacing="0"')
        
    if after_auto:
        attrs.append('w:afterAutospacing="1"')
    else:
        attrs.append('w:afterAutospacing="0"')
    
    # Create the XML string and parse it into an element
    spacing_xml = f'<w:spacing {nsdecls("w")} {" ".join(attrs)}/>'
    
    try:
        return parse_xml(spacing_xml)
    except Exception as e:
        logger.error(f"Error creating spacing node: {e}")
        logger.error(f"Attempted XML: {spacing_xml}")
        raise

def make_border_node(width_pt=1, color="000000", style="single", padding_pt=1):
    """
    Generate a Word XML paragraph border node with the specified attributes.
    
    Args:
        width_pt (float): Border width in points
        color (str): Border color in hex format (without #)
        style (str): Border style (single, double, etc.)
        padding_pt (float): Border padding in points
        
    Returns:
        Element: XML element for paragraph borders
    """
    # Convert points to 1/8th point units for border width
    width_8th_pt = int(width_pt * 8)
    # Convert points to twips for padding
    padding_twips = int(padding_pt * 20)
    
    # Create border XML with all four sides
    border_xml = f'''
    <w:pBdr {nsdecls("w")}>
        <w:top w:val="{style}" w:sz="{width_8th_pt}" w:space="{padding_twips}" w:color="{color}"/>
        <w:left w:val="{style}" w:sz="{width_8th_pt}" w:space="{padding_twips}" w:color="{color}"/>
        <w:bottom w:val="{style}" w:sz="{width_8th_pt}" w:space="{padding_twips}" w:color="{color}"/>
        <w:right w:val="{style}" w:sz="{width_8th_pt}" w:space="{padding_twips}" w:color="{color}"/>
    </w:pBdr>
    '''
    
    try:
        return parse_xml(border_xml)
    except Exception as e:
        logger.error(f"Error creating border node: {e}")
        logger.error(f"Attempted XML: {border_xml}")
        raise

def make_outline_level_node(level):
    """
    Generate a Word XML outline level node for heading hierarchy.
    
    Args:
        level (int): Outline level (0=Heading 1, 1=Heading 2, etc.)
        
    Returns:
        Element: XML element for outline level
    """
    outline_xml = f'<w:outlineLvl {nsdecls("w")} w:val="{level}"/>'
    
    try:
        return parse_xml(outline_xml)
    except Exception as e:
        logger.error(f"Error creating outline level node: {e}")
        raise

def make_compatibility_node():
    """
    Generate Word compatibility settings node to ensure consistent rendering.
    
    Returns:
        Element: XML element for compatibility settings
    """
    compat_xml = f'''
    <w:compat {nsdecls("w")}>
        <w:compatSetting {nsdecls("w")} w:name="compatibilityMode" w:uri="http://schemas.microsoft.com/office/word" w:val="15"/>
        <w:compatSetting {nsdecls("w")} w:name="overrideTableStyleFontSizeAndJustification" w:uri="http://schemas.microsoft.com/office/word" w:val="1"/>
        <w:compatSetting {nsdecls("w")} w:name="enableOpenTypeFeatures" w:uri="http://schemas.microsoft.com/office/word" w:val="1"/>
        <w:compatSetting {nsdecls("w")} w:name="doNotFlipMirrorIndents" w:uri="http://schemas.microsoft.com/office/word" w:val="1"/>
        <w:compatSetting {nsdecls("w")} w:name="differentiateMultirowTableHeaders" w:uri="http://schemas.microsoft.com/office/word" w:val="1"/>
        <w:compatSetting {nsdecls("w")} w:name="useWord2013TrackBottomHyphenation" w:uri="http://schemas.microsoft.com/office/word" w:val="0"/>
        <w:compatSetting {nsdecls("w")} w:name="ptoNoSpaceBefore" w:uri="http://schemas.microsoft.com/office/word" w:val="1"/>
    </w:compat>
    '''
    
    try:
        return parse_xml(compat_xml)
    except Exception as e:
        logger.error(f"Error creating compatibility node: {e}")
        raise 