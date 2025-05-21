"""
DOCX Builder for Resume Tailor Application

Generates Microsoft Word (.docx) files with consistent styling based on design tokens.
"""

import os
import logging
import json
import traceback
from io import BytesIO
from pathlib import Path
from typing import Dict, List, Optional, Any, Union

from docx import Document
from docx.shared import Pt, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT
from docx.enum.style import WD_STYLE_TYPE
from docx.text.paragraph import Paragraph
from docx.oxml.ns import qn

from style_manager import StyleManager
from style_engine import StyleEngine

# Import our new style registry
try:
    from word_styles.registry import StyleRegistry, get_or_create_style, apply_direct_paragraph_formatting
    from word_styles.section_builder import add_section_header as registry_add_section_header
    from word_styles.section_builder import add_content_paragraph, add_bullet_point, remove_empty_paragraphs
    USE_STYLE_REGISTRY = True
except ImportError:
    USE_STYLE_REGISTRY = False

# Use style engine if available, otherwise fall back to old approach
try:
    from style_engine import StyleEngine
    USE_STYLE_ENGINE = True
except ImportError:
    USE_STYLE_ENGINE = False

logger = logging.getLogger(__name__)

def load_section_json(request_id: str, section_name: str, temp_dir: str) -> Dict[str, Any]:
    """Load a section's JSON data from the temporary session directory."""
    try:
        file_path = os.path.join(temp_dir, f"{request_id}_{section_name}.json")
        logger.info(f"Looking for section file: {file_path}")
        
        if not os.path.exists(file_path):
            logger.warning(f"File not found: {file_path}")
            return {}
            
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            logger.info(f"Successfully loaded '{section_name}' section: {type(data)}")
            if isinstance(data, dict):
                logger.info(f"Dict keys for {section_name}: {list(data.keys())}")
            elif isinstance(data, list):
                logger.info(f"List length for {section_name}: {len(data)}")
            return data
    except FileNotFoundError:
        logger.warning(f"Section file not found: {file_path}")
        return {}
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON from {file_path}: {e}")
        # Try to get raw content for debugging
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                logger.error(f"Raw content from {file_path} (first 100 chars): {content[:100]}...")
        except Exception:
            pass
        return {}
    except Exception as e:
        logger.error(f"Error loading section JSON: {e}")
        return {}

def _apply_paragraph_style(p, style_name: str, docx_styles: Dict[str, Any]):
    """Enhanced style application for paragraphs in DOCX."""
    if not p.runs:
        return  # Skip empty paragraphs
    
    # Get style configuration
    style_config = docx_styles.get(style_name, {})
    if not style_config:
        logger.warning(f"Style not found: {style_name}")
        return
    
    # Apply font properties to all runs in the paragraph for consistency
    for run in p.runs:
        font = run.font
        if "fontSizePt" in style_config:
            font.size = Pt(style_config["fontSizePt"])
        if "fontFamily" in style_config:
            font.name = style_config["fontFamily"]
        if "color" in style_config:
            r, g, b = style_config["color"]
            font.color.rgb = RGBColor(r, g, b)
        if style_config.get("bold", False):
            font.bold = True
        if style_config.get("italic", False):
            font.italic = True
    
    # Apply paragraph formatting
    if "spaceAfterPt" in style_config:
        p.paragraph_format.space_after = Pt(style_config["spaceAfterPt"])
    if "spaceBeforePt" in style_config:
        p.paragraph_format.space_before = Pt(style_config["spaceBeforePt"])
    if "indentCm" in style_config:
        p.paragraph_format.left_indent = Cm(style_config["indentCm"])
    
    # Apply alignment
    if style_name == "heading1":
        p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    elif style_config.get("alignment") == "center":
        p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    else:
        p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT
    
    # For section headers (heading2), apply shading if specified
    if style_name == "heading2" and ("backgroundColor" in style_config or "borderColor" in style_config):
        from docx.oxml.ns import nsdecls
        from docx.oxml import parse_xml
        
        # Apply background shading
        if "backgroundColor" in style_config:
            r, g, b = style_config["backgroundColor"]
            hex_color = f"{r:02x}{g:02x}{b:02x}"
            
            shading_xml = f'<w:shd {nsdecls("w")} w:fill="{hex_color}" w:val="clear"/>'
            p._element.get_or_add_pPr().append(parse_xml(shading_xml))
        
        # Add border if specified
        if "borderColor" in style_config:
            r, g, b = style_config["borderColor"]
            border_hex = f"{r:02x}{g:02x}{b:02x}"
            border_size = style_config.get("borderSize", 1)
            border_xml = f'''
                <w:pBdr {nsdecls("w")}>
                    <w:bottom w:val="single" w:sz="{border_size * 4}" w:space="0" w:color="{border_hex}"/>
                </w:pBdr>
            '''
            p._element.get_or_add_pPr().append(parse_xml(border_xml))
            
        # Apply padding
        if "paddingHorizontal" in style_config or "paddingVertical" in style_config:
            padding_left = style_config.get("paddingHorizontal", 0)
            padding_right = style_config.get("paddingHorizontal", 0)
            padding_top = style_config.get("paddingVertical", 0)
            padding_bottom = style_config.get("paddingVertical", 0)
            
            # Convert to twips (twentieth of a point)
            padding_left_twips = int(padding_left * 20)
            padding_right_twips = int(padding_right * 20)
            padding_top_twips = int(padding_top * 20)
            padding_bottom_twips = int(padding_bottom * 20)
            
            spacing_xml = f'''
                <w:spacing {nsdecls("w")} w:before="{padding_top_twips}" 
                w:after="{padding_bottom_twips}"/>
            '''
            p._element.get_or_add_pPr().append(parse_xml(spacing_xml))
            
            indent_xml = f'''
                <w:ind {nsdecls("w")} w:left="{padding_left_twips}" 
                w:right="{padding_right_twips}"/>
            '''
            p._element.get_or_add_pPr().append(parse_xml(indent_xml))

def _create_document_styles(doc, docx_styles):
    """Create custom styles in the document for consistent formatting."""
    # Create all custom styles using the StyleEngine
    try:
        # Create all custom styles at once
        custom_styles = StyleEngine.create_docx_custom_styles(doc)
        logger.info(f"Successfully created custom DOCX styles: {list(custom_styles.keys())}")
        return custom_styles
    except Exception as e:
        logger.warning(f"Error creating custom styles: {e}")
        logger.warning("Falling back to legacy style creation")
        
        # Fallback to original implementation
        styles = {}
        
        # Create section header style
        try:
            section_style = StyleEngine.create_docx_section_header_style(doc)
            styles["SectionHeader"] = section_style
            logger.info("Successfully created custom SectionHeader style with fallback method")
        except Exception as e:
            logger.warning(f"Error creating SectionHeader style with fallback method: {e}")
        
        # Create bullet style
        try:
            bullet_style = StyleEngine.create_docx_bullet_style(doc)
            styles["CustomBullet"] = bullet_style
            logger.info("Successfully created custom CustomBullet style with fallback method")
        except Exception as e:
            logger.warning(f"Error creating CustomBullet style with fallback method: {e}")
            
        return styles

def format_right_aligned_pair(doc, left_text, right_text, left_style, right_style, docx_styles):
    """Creates a paragraph with left-aligned and right-aligned text using tab stops."""
    para = doc.add_paragraph(style='MR_Content')  # Use our new custom style
    
    # Add left-aligned text
    if left_text:
        left_run = para.add_run(left_text)
        # Apply styling for the left text (always bold)
        left_run.bold = True
    
    # Get global margin values from design tokens
    structured_tokens = StyleEngine.get_structured_tokens()
    global_margins = structured_tokens.get("global", {}).get("margins", {})
    global_left_margin_cm = float(global_margins.get("leftCm", "2.0"))
    global_right_margin_cm = float(global_margins.get("rightCm", "2.0"))
    
    # Fallback to section properties if needed for compatibility
    section = doc.sections[0]
    page_width_emu = section.page_width if section.page_width is not None else 0
    
    # Convert page width from EMU to cm
    if page_width_emu > 0:
        page_width_cm = page_width_emu / 360000.0  # 1 cm = 360000 EMUs
    else:
        # Fallback to A4 width if page_width not available
        page_width_cm = 21.0  # Standard A4 width
    
    # Calculate content width in cm using global margins
    content_width_cm = page_width_cm - global_left_margin_cm - global_right_margin_cm
    
    # Set tab position at the right edge of content area
    if content_width_cm <= 0:  # Fallback if dimensions are invalid
        logger.warning(f"Calculated non-positive content_width_cm ({content_width_cm}). Defaulting tab stop to 16cm.")
        tab_position_cm = 16.0  # A reasonable default
    else:
        tab_position_cm = content_width_cm
    
    logger.info(f"Global margins: L={global_left_margin_cm}cm, R={global_right_margin_cm}cm, PW={page_width_cm:.2f}cm, Content={content_width_cm:.2f}cm, TabPos={tab_position_cm:.2f}cm")
    
    # Remove any existing tab stops to prevent conflicts
    para.paragraph_format.tab_stops.clear_all()
    
    # Add the new tab stop at the calculated position
    if tab_position_cm > 0:
        para.paragraph_format.tab_stops.add_tab_stop(Cm(tab_position_cm), WD_TAB_ALIGNMENT.RIGHT)
    else:
        logger.warning(f"Calculated tab position {tab_position_cm:.2f}cm is not positive. Skipping tab stop addition.")
    
    # Add right-aligned text with tab
    if right_text:
        para.add_run('\t')  # Add tab
        right_run = para.add_run(right_text)
    
    # Spacing and indentation are handled by the 'MR_Content' style
    return para

def create_bullet_point(doc, text, docx_styles):
    """Creates a properly styled bullet point with consistent formatting."""
    # from docx.oxml.ns import nsdecls # Not needed if XML is removed
    # from docx.oxml import parse_xml # Not needed if XML is removed
    # from docx.shared import Cm, Pt # Not needed if direct formatting is removed
    
    # Use our new custom style
    bullet_para = doc.add_paragraph(style='MR_BulletPoint')
    
    # Add the text content with the bullet character
    bullet_para.add_run(f"• {text}")
    
    # Indentation, hanging indent, and spacing are now handled by the 'MR_BulletPoint' style.
    # Removed direct paragraph formatting for left_indent, first_line_indent.
    # Removed direct XML formatting for indentation (w:ind) and spacing (w:spacing).
    
    logger.info(f"Applied MR_BulletPoint style to: {str(text)[:30]}...")
    return bullet_para

def add_section_header(doc: Document, section_name: str) -> Paragraph:
    """
    Add a section header with proper styling.
    
    This function uses the new style registry approach if available,
    otherwise it falls back to the previous approach.
    
    Args:
        doc: The document to add the section header to
        section_name: The section header text
        
    Returns:
        The added paragraph
    """
    if USE_STYLE_REGISTRY:
        # Use the new registry-based approach
        section_para = registry_add_section_header(doc, section_name)
        logger.info(f"Applied BoxedHeading2 style to section header: {section_name}")
        return section_para
    else:
        # Fall back to the old approach
        section_para = doc.add_paragraph(section_name)
        
        # Apply styling using StyleEngine if available
        if USE_STYLE_ENGINE:
            boxed_heading_style = StyleEngine.create_boxed_heading_style(doc)
            section_para.style = boxed_heading_style
            StyleEngine.apply_boxed_section_header_style(doc, section_para)
        else:
            # Basic fallback styling
            section_para.style = "Heading 2"
            for run in section_para.runs:
                run.bold = True
        
        logger.info(f"Applied style to section header: {section_name}")
        return section_para

def add_role_description(doc, text, docx_styles):
    """Adds a consistently formatted role description paragraph."""
    if not text:
        return None
    
    # Use our new custom style
    role_para = doc.add_paragraph(text, style='MR_RoleDescription')
    
    # Indentation and spacing are now handled by the 'MR_RoleDescription' style.
    # Font properties (italic, size) are also handled by the style.
    # Removed direct paragraph formatting for left_indent, space_after.
    # Removed direct XML formatting for indentation (w:ind) and spacing (w:spacing).
    
    logger.info(f"Applied MR_RoleDescription style to: {str(text)[:30]}...")
    return role_para

def tighten_before_headers(doc):
    """
    Finds paragraphs before section headers and sets spacing to zero.
    
    This enhanced implementation addresses the issues identified:
    1. Properly detects empty paragraphs that might cause unwanted spacing
    2. Applies spacing changes directly to XML for maximum compatibility
    3. Handles various paragraph types correctly
    
    Args:
        doc: The document to process
        
    Returns:
        Number of paragraphs fixed
    """
    from docx.oxml import parse_xml
    from docx.oxml.ns import nsdecls
    
    logger.info("Starting tighten_before_headers process...")
    fixed_instances_count = 0
    
    # If using style registry, first remove any unwanted empty paragraphs
    if USE_STYLE_REGISTRY:
        # This doesn't delete intentional EmptyParagraph style paragraphs
        remove_count = remove_empty_paragraphs(doc)
        logger.info(f"Removed {remove_count} unwanted empty paragraphs")
    
    # Find all section headers
    header_indices = []
    for i, para in enumerate(doc.paragraphs):
        # Check by style name first (most reliable)
        if para.style and para.style.name in ['BoxedHeading2', 'Heading 2']:
            header_indices.append(i)
            continue
            
        # Check by borders (also reliable)
        p_pr = para._element.get_or_add_pPr()
        if p_pr.find(qn('w:pBdr')) is not None:
            header_indices.append(i)
            continue
            
        # Check by common section header names as fallback
        section_keywords = ["PROFESSIONAL SUMMARY", "SUMMARY", "EXPERIENCE", 
                            "EDUCATION", "SKILLS", "PROJECTS"]
        if any(keyword in para.text.upper() for keyword in section_keywords):
            header_indices.append(i)
            
    logger.info(f"Found {len(header_indices)} section headers")
    
    # Process paragraphs before each header (skip first header)
    for header_idx in header_indices[1:]:  # Skip first header (no content before it)
        if header_idx > 0:  # Safety check
            prev_para = doc.paragraphs[header_idx - 1]
            
            # Apply spacing change
            p_pr = prev_para._element.get_or_add_pPr()
            
            # Create spacing node with zero space after
            spacing_xml = f'<w:spacing {nsdecls("w")} w:after="0"/>'
            
            # Remove existing spacing element to avoid conflicts
            for existing in p_pr.xpath('./w:spacing'):
                p_pr.remove(existing)
                
            # Add new spacing element
            p_pr.append(parse_xml(spacing_xml))
            
            # Also set via API for maximum compatibility
            prev_para.paragraph_format.space_after = Pt(0)
            
            logger.info(f"Fixed spacing: Set space_after=0 on paragraph before section header at index {header_idx}")
            fixed_instances_count += 1
    
    return fixed_instances_count

# Replace old _fix_spacing_between_sections with new implementation
_fix_spacing_between_sections = tighten_before_headers

def build_docx(request_id: str, temp_dir: str, debug: bool = False) -> BytesIO:
    """
    Build a DOCX file from the resume data for the given request ID.
    
    Args:
        request_id: The unique request ID for the resume
        temp_dir: Directory containing the temp session data files
        debug: Whether to enable debugging output
        
    Returns:
        BytesIO object containing the DOCX file data
    """
    try:
        logger.info(f"Building DOCX for request ID: {request_id}")
        logger.info(f"Temp directory path: {temp_dir}")
        logger.info(f"Debug mode: {debug}")
        
        # Check for files related to this request_id
        try:
            file_list = os.listdir(temp_dir)
            matching_files = [f for f in file_list if request_id in f]
            logger.info(f"Files containing request ID: {matching_files}")
        except Exception as e:
            logger.error(f"Error listing directory: {e}")
        
        # Load DOCX styles from StyleManager
        docx_styles = StyleManager.load_docx_styles()
        if not docx_styles:
            logger.error("No DOCX styles found. Using defaults.")
            docx_styles = {
                "page": {"marginTopCm": 1.0, "marginBottomCm": 1.0, "marginLeftCm": 2.0, "marginRightCm": 2.0},
                "heading1": {"fontFamily": "Calibri", "fontSizePt": 16},
                "heading2": {"fontFamily": "Calibri", "fontSizePt": 14, "color": [0, 0, 102], "spaceAfterPt": 6},
                "heading3": {"fontFamily": "Calibri", "fontSizePt": 11, "bold": True, "spaceAfterPt": 4},
                "body": {"fontFamily": "Calibri", "fontSizePt": 11}
            }
        
        # Create a new Document
        doc = Document()
        
        # Create custom document styles
        custom_styles = _create_document_styles(doc, docx_styles)
        
        # Configure page margins using global margin tokens
        section = doc.sections[0]
        page_config = docx_styles.get("page", {})
        
        # Get margin values from global tokens
        structured_tokens = StyleEngine.get_structured_tokens()
        global_margins = structured_tokens.get("global", {}).get("margins", {})
        global_left_margin_cm = float(global_margins.get("leftCm", "2.0"))
        global_right_margin_cm = float(global_margins.get("rightCm", "2.0"))
        
        # Set margins from tokens and style config
        section.top_margin = Cm(page_config.get("marginTopCm", 1.0))
        section.bottom_margin = Cm(page_config.get("marginBottomCm", 1.0))
        section.left_margin = Cm(global_left_margin_cm)  # Use global token
        section.right_margin = Cm(global_right_margin_cm)  # Use global token
        
        logger.info(f"Applied document margins from global tokens: Left={global_left_margin_cm}cm, Right={global_right_margin_cm}cm")
        
        # ------ CONTACT SECTION ------
        logger.info("Processing Contact section...")
        
        # Open and inspect the contact file directly to debug structure issues
        contact_file_path = os.path.join(temp_dir, f"{request_id}_contact.json")
        if os.path.exists(contact_file_path):
            try:
                with open(contact_file_path, 'r', encoding='utf-8') as f:
                    raw_content = f.read()
                    logger.info(f"Raw contact file content (first 200 chars): {raw_content[:200]}")
            except Exception as e:
                logger.error(f"Error reading raw contact file: {e}")
        
        contact = load_section_json(request_id, "contact", temp_dir)
        logger.info(f"Contact data loaded: {bool(contact)}")
        logger.info(f"Contact data type: {type(contact)}")
        
        if isinstance(contact, dict):
            logger.info(f"Contact keys: {list(contact.keys())}")
        
        if contact:
            # Verify contact is a dictionary
            if not isinstance(contact, dict):
                logger.warning(f"Contact section is not a dictionary: {type(contact)}")
                contact = {}
            
            # Check if contact has a 'content' key (alternate structure)
            if 'content' in contact:
                logger.info("Found 'content' key in contact section")
                # Extract actual contact data from content
                try:
                    # Try to access the contact data
                    contact_data = contact['content']
                    if isinstance(contact_data, dict):
                        logger.info(f"Contact content is a dictionary with keys: {list(contact_data.keys())}")
                        contact = contact_data
                    elif isinstance(contact_data, list) and len(contact_data) > 0 and isinstance(contact_data[0], dict):
                        logger.info(f"Contact content is a list of dictionaries, using first item")
                        contact = contact_data[0]
                    elif isinstance(contact_data, str):
                        # Handle string content - parse it into structured data
                        logger.info("Contact content is a string, attempting to parse")
                        
                        # Parse the contact information from the string
                        lines = contact_data.strip().split('\n')
                        
                        # Extract name from the first line
                        name = lines[0].strip() if lines else ""
                        logger.info(f"Extracted name from string: {name}")
                        
                        # Extract contact details from subsequent lines
                        contact_details = {}
                        if len(lines) > 1:
                            details_line = lines[1].strip()
                            # Split by common separators
                            details_parts = [p.strip() for p in details_line.replace('|', '|').split('|')]
                            
                            logger.info(f"Extracted contact details: {details_parts}")
                            
                            for part in details_parts:
                                part = part.strip()
                                # Try to identify the type of contact detail
                                if '@' in part:
                                    contact_details['email'] = part
                                elif 'P:' in part or 'Phone:' in part or any(c.isdigit() for c in part):
                                    contact_details['phone'] = part
                                elif 'LinkedIn' in part or 'linkedin.com' in part:
                                    contact_details['linkedin'] = part
                                elif 'Github' in part or 'github.com' in part:
                                    contact_details['github'] = part
                                elif any(loc in part.lower() for loc in ['street', 'ave', 'road', 'blvd', 'city', 'state']):
                                    contact_details['location'] = part
                        
                        # Create a new contact object
                        contact = {'name': name, **contact_details}
                        logger.info(f"Created structured contact data: {contact}")
                    else:
                        logger.info(f"Contact content is type: {type(contact_data)}")
                except Exception as e:
                    logger.warning(f"Error accessing contact content: {e}")
            
            # Print full contact data for debugging
            logger.info(f"Final contact data structure to use: {contact}")
            
            # Name - handle potential different structures
            name = ""
            if "name" in contact:
                name = contact["name"]
            elif "full_name" in contact:
                name = contact["full_name"]
            
            if name:
                name_para = doc.add_paragraph(name)
                _apply_paragraph_style(name_para, "heading1", docx_styles)
                
                # Contact details
                contact_parts = []
                if "location" in contact and contact["location"]:
                    contact_parts.append(contact["location"])
                if "phone" in contact and contact["phone"]:
                    contact_parts.append(contact["phone"])
                if "email" in contact and contact["email"]:
                    contact_parts.append(contact["email"])
                if "linkedin" in contact and contact["linkedin"]:
                    contact_parts.append(contact["linkedin"])
                
                # Additional possible contact fields
                if "website" in contact and contact["website"]:
                    contact_parts.append(contact["website"])
                if "github" in contact and contact["github"]:
                    contact_parts.append(contact["github"])
                
                contact_text = " | ".join(contact_parts)
                contact_para = doc.add_paragraph(contact_text)
                _apply_paragraph_style(contact_para, "body", docx_styles)
                contact_para.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
                
                # Add a horizontal line
                doc.add_paragraph("").paragraph_format.space_after = Pt(6)
            else:
                logger.warning("No name found in contact data, skipping contact section")
        else:
            logger.warning("No contact data found")
            
            # Try a fallback approach - look for the file directly
            fallback_files = [f for f in os.listdir(temp_dir) if f.endswith("_contact.json") and request_id in f]
            if fallback_files:
                logger.info(f"Found fallback contact files: {fallback_files}")
                try:
                    with open(os.path.join(temp_dir, fallback_files[0]), 'r', encoding='utf-8') as f:
                        fallback_contact = json.load(f)
                        logger.info(f"Loaded fallback contact data: {fallback_contact}")
                        
                        # Extract name and add to document
                        if isinstance(fallback_contact, dict):
                            name = fallback_contact.get("name", "")
                            if name:
                                name_para = doc.add_paragraph(name)
                                _apply_paragraph_style(name_para, "heading1", docx_styles)
                                logger.info(f"Added name from fallback: {name}")
                except Exception as e:
                    logger.error(f"Error processing fallback contact data: {e}")
        
        # ------ SUMMARY SECTION ------
        logger.info("Processing Summary section...")
        summary = load_section_json(request_id, "summary", temp_dir)
        logger.info(f"Summary data loaded: {bool(summary)}")
        
        # Handle both direct summary and summary with 'content' key
        summary_text = ""
        if summary:
            if isinstance(summary, dict):
                if "summary" in summary:
                    summary_text = summary.get("summary", "")
                elif "content" in summary:
                    # Alternative structure with content key
                    content = summary.get("content", "")
                    if isinstance(content, dict) and "summary" in content:
                        summary_text = content.get("summary", "")
                    else:
                        summary_text = str(content)
            else:
                summary_text = str(summary)
                
            if summary_text:
                # Add section header with helper function
                summary_header = add_section_header(doc, "PROFESSIONAL SUMMARY")
                
                # Add summary content
                summary_para = doc.add_paragraph(summary_text, style='MR_SummaryText')
                
                # Space after section
                doc.add_paragraph("").paragraph_format.space_after = Pt(6)
        
        # ------ EXPERIENCE SECTION ------
        logger.info("Processing Experience section...")
        experience = load_section_json(request_id, "experience", temp_dir)
        logger.info(f"Experience data loaded: {bool(experience)}")
        logger.info(f"Experience contains 'experiences' key: {isinstance(experience, dict) and 'experiences' in experience}")
        
        # Handle both dictionary with 'experiences' key and direct list of experiences
        experiences_list = []
        if experience:
            if isinstance(experience, dict) and "experiences" in experience:
                experiences_list = experience.get("experiences", [])
            elif isinstance(experience, list):
                # Direct list of experiences
                experiences_list = experience
            else:
                logger.warning(f"Unexpected experience format: {type(experience)}")
                
            if experiences_list:
                # Add section header with helper function
                exp_header = add_section_header(doc, "EXPERIENCE")
                
                # Verify experiences is a list
                if not isinstance(experiences_list, list):
                    logger.warning(f"Experiences is not a list: {type(experiences_list)}")
                    experiences_list = []
                    
                # Add each job
                for job in experiences_list:
                    # Verify job is a dictionary
                    if not isinstance(job, dict):
                        logger.warning(f"Job is not a dictionary: {type(job)}")
                        continue
                        
                    # Company and location - use the helper function for consistent formatting
                    company = job.get('company', '')
                    location = job.get('location', '')
                    
                    if company or location:
                        company_para = format_right_aligned_pair(
                            doc,
                            company,
                            location,
                            "heading3",
                            "heading3",
                            docx_styles
                        )
                    
                    # Position and dates - use the helper function for consistent formatting
                    position = job.get('position', '')
                    if not position and job.get('title'):  # Fallback to 'title' if 'position' is not available
                        position = job.get('title', '')
                    dates = job.get('dates', '')
                    
                    if position or dates:
                        position_para = format_right_aligned_pair(
                            doc,
                            position,
                            dates,
                            "body",
                            "body",
                            docx_styles
                        )
                    
                    logger.info(f"Formatted experience entry: '{company} - {position}'")
                    
                    # Role description - use the helper function for consistent formatting
                    if job.get('role_description'):
                        role_para = add_role_description(doc, job.get('role_description'), docx_styles)
                    
                    # Achievements/bullets - use the helper function for consistent formatting
                    for achievement in job.get('achievements', []):
                        bullet_para = create_bullet_point(doc, achievement, docx_styles)
                
        # ------ EDUCATION SECTION ------
        logger.info("Processing Education section...")
        education = load_section_json(request_id, "education", temp_dir)
        logger.info(f"Education data loaded: {bool(education)}")
        logger.info(f"Education contains 'institutions' key: {isinstance(education, dict) and 'institutions' in education}")
        
        # Handle both dictionary with 'institutions' key and direct list of institutions
        institutions_list = []
        if education:
            if isinstance(education, dict) and "institutions" in education:
                institutions_list = education.get("institutions", [])
            elif isinstance(education, list):
                # Direct list of institutions
                institutions_list = education
            else:
                logger.warning(f"Unexpected education format: {type(education)}")
                
            if institutions_list:
                # Add section header with helper function
                edu_header = add_section_header(doc, "EDUCATION")
                
                # Verify institutions is a list
                if not isinstance(institutions_list, list):
                    logger.warning(f"Institutions is not a list: {type(institutions_list)}")
                    institutions_list = []
                    
                # Add each institution
                for school in institutions_list:
                    # Verify school is a dictionary
                    if not isinstance(school, dict):
                        logger.warning(f"School is not a dictionary: {type(school)}")
                        continue
                        
                    # Institution and location - use the helper function for consistent formatting
                    institution = school.get('institution', '')
                    location = school.get('location', '')
                    
                    if institution or location:
                        school_para = format_right_aligned_pair(
                            doc,
                            institution,
                            location,
                            "heading3",
                            "heading3",
                            docx_styles
                        )
                    
                    # Degree and dates - use the helper function for consistent formatting
                    degree = school.get('degree', '')
                    dates = school.get('dates', '')
                    
                    if degree or dates:
                        degree_para = format_right_aligned_pair(
                            doc,
                            degree,
                            dates,
                            "body",
                            "body",
                            docx_styles
                        )
                    
                    logger.info(f"Formatted education entry: '{institution} - {degree}'")
                    
                    # Highlights/bullets - use the helper function for consistent formatting
                    for highlight in school.get('highlights', []):
                        bullet_para = create_bullet_point(doc, highlight, docx_styles)
        
        # ------ SKILLS SECTION ------
        logger.info("Processing Skills section...")
        skills = load_section_json(request_id, "skills", temp_dir)
        logger.info(f"Skills data loaded: {bool(skills)}")
        logger.info(f"Skills data type: {type(skills)}")
        logger.info(f"Skills content sample: {str(skills)[:100]}")
        
        if skills:
            # Add section header with helper function 
            skills_header = add_section_header(doc, "SKILLS")
            
            # Add skills content - handle different possible formats
            if isinstance(skills, dict) and "skills" in skills:
                skills_content = skills.get("skills", "")
                logger.info(f"Skills content type: {type(skills_content)}")
                
                # Check if skills content is a list
                if isinstance(skills_content, list):
                    logger.info("Processing skills as inline list with commas")
                    # Handle skills as a comma-separated list on a single line
                    skills_text = ", ".join([str(skill) for skill in skills_content])
                    skills_para = doc.add_paragraph(skills_text, style='MR_SkillList')
                    logger.info(f"Applied MR_SkillList style to skills list")
                elif isinstance(skills_content, dict):
                    logger.info("Processing skills as dict")
                    # Handle skills as dictionary with categories
                    for category, skill_list in skills_content.items():
                        # Add category as subheading
                        category_para = doc.add_paragraph(category.upper(), style='MR_SkillCategory')
                        logger.info(f"Applied MR_SkillCategory style to category: {category}")
                        
                        # Add skills in this category as a comma-separated list
                        if isinstance(skill_list, list):
                            skills_text = ", ".join([str(skill) for skill in skill_list])
                            skills_para = doc.add_paragraph(skills_text, style='MR_SkillList')
                            logger.info(f"Applied MR_SkillList style to skills in category: {category}")
                        else:
                            # Not a list, just add as text
                            skill_para = doc.add_paragraph(str(skill_list), style='MR_SkillList')
                            logger.info(f"Applied MR_SkillList style to non-list skills in category: {category}")
                else:
                    logger.info("Processing skills as string")
                    # Handle skills as string or any other type
                    skills_para = doc.add_paragraph(str(skills_content), style='MR_SkillList')
                    logger.info(f"Applied MR_SkillList style to skills string")
            elif isinstance(skills, dict):
                logger.info("Processing skills dict directly")
                # Direct display of skills object if it doesn't have "skills" key
                for category, skill_list in skills.items():
                    # Add category as subheading
                    category_para = doc.add_paragraph(category.upper(), style='MR_SkillCategory')
                    logger.info(f"Applied MR_SkillCategory style to category: {category}")
                    
                    # Add skills in this category as a comma-separated list
                    if isinstance(skill_list, list):
                        skills_text = ", ".join([str(skill) for skill in skill_list])
                        skills_para = doc.add_paragraph(skills_text, style='MR_SkillList')
                        logger.info(f"Applied MR_SkillList style to skills in category: {category}")
                    else:
                        # Not a list, just add as text
                        skill_para = doc.add_paragraph(str(skill_list), style='MR_SkillList')
                        logger.info(f"Applied MR_SkillList style to non-list skills in category: {category}")
            elif isinstance(skills, list):
                logger.info("Processing skills as top-level list")
                # Handle the case where skills is a list directly
                skills_text = ", ".join([str(skill) for skill in skills])
                skills_para = doc.add_paragraph(skills_text, style='MR_SkillList')
                logger.info(f"Applied MR_SkillList style to top-level skills list")
            else:
                logger.info(f"Processing skills as fallback type: {type(skills)}")
                # Fallback for any other format
                skills_para = doc.add_paragraph(str(skills), style='MR_SkillList')
                logger.info(f"Applied MR_SkillList style to fallback skills content")
        
        # ------ PROJECTS SECTION ------
        logger.info("Processing Projects section...")
        projects = load_section_json(request_id, "projects", temp_dir)
        logger.info(f"Projects data loaded: {bool(projects)}")
        logger.info(f"Projects contains 'projects' key: {isinstance(projects, dict) and 'projects' in projects}")
        
        # Handle both dictionary with 'projects' key, direct list of projects, and content key
        projects_list = []
        if projects:
            if isinstance(projects, dict) and "projects" in projects:
                projects_list = projects.get("projects", [])
            elif isinstance(projects, dict) and "content" in projects:
                # Handle content key similar to other sections
                logger.info("Found 'content' key in projects section")
                content = projects.get("content", [])
                if isinstance(content, list):
                    projects_list = content
                elif isinstance(content, dict) and "projects" in content:
                    projects_list = content.get("projects", [])
                elif isinstance(content, str):
                    # In some cases, content might be a string
                    logger.info("Projects content is a string, adding as single project")
                    # Add projects section header using helper function
                    projects_header = add_section_header(doc, "PROJECTS")
                    
                    # Add the string content directly as paragraph
                    projects_para = doc.add_paragraph(content)
                    _apply_paragraph_style(projects_para, "body", docx_styles)
                    
                    # Skip the rest of the projects processing
                    projects_list = []
                else:
                    logger.warning(f"Unexpected projects content format: {type(content)}")
            elif isinstance(projects, list):
                # Direct list of projects
                projects_list = projects
            else:
                logger.warning(f"Unexpected projects format: {type(projects)}")
                
            if projects_list:
                # Add section header with helper function
                projects_header = add_section_header(doc, "PROJECTS")
                
                # Verify projects is a list
                if not isinstance(projects_list, list):
                    logger.warning(f"Projects is not a list: {type(projects_list)}")
                    projects_list = []
                    
                # Add each project
                for project in projects_list:
                    # Verify project is a dictionary
                    if not isinstance(project, dict):
                        logger.warning(f"Project is not a dictionary: {type(project)}")
                        continue
                        
                    # Project title and dates - use the helper function for consistent formatting
                    title = project.get('title', '')
                    if not title and project.get('name'):  # Fallback to 'name' if 'title' is not available
                        title = project.get('name', '')
                    dates = project.get('dates', '')
                    if not dates and project.get('date'):  # Fallback to 'date' if 'dates' is not available
                        dates = project.get('date', '')
                    
                    if title or dates:
                        title_para = format_right_aligned_pair(
                            doc,
                            title,
                            dates,
                            "heading3",
                            "body",
                            docx_styles
                        )
                    
                    logger.info(f"Formatted project entry: '{title}'")
                    
                    # Project details - use the helper function for consistent formatting
                    for detail in project.get('details', []):
                        bullet_para = create_bullet_point(doc, detail, docx_styles)
        
        # Fix spacing between sections - use our enhanced implementation
        if USE_STYLE_REGISTRY:
            tighten_before_headers(doc)
        else:
            _fix_spacing_between_sections(doc)
        
        # Save DOCX to BytesIO
        logger.info("Saving DOCX to BytesIO...")
        
        output = BytesIO()
        doc.save(output)
        output.seek(0)
        
        # Generate debug report if requested
        if debug:
            try:
                from utils.docx_debug import generate_debug_report
                import json
                
                # Generate debug report
                debug_report = generate_debug_report(doc)
                
                # Save debug report to file
                debug_path = Path(__file__).parent.parent / f'debug_{request_id}.json'
                with open(debug_path, 'w') as f:
                    json.dump(debug_report, f, indent=2)
                
                logger.info(f"Debug report saved to {debug_path}")
                
                # Also save a copy of the DOCX for inspection
                debug_docx_path = Path(__file__).parent.parent / f'debug_{request_id}.docx'
                with open(debug_docx_path, 'wb') as f:
                    f.write(output.getvalue())
                
                logger.info(f"Debug DOCX saved to {debug_docx_path}")
                
                # Reset the output buffer position
                output.seek(0)
            except Exception as e:
                logger.error(f"Error generating debug report: {e}")
        
        logger.info(f"Successfully built DOCX for request ID: {request_id}")
        return output
    
    except Exception as e:
        # Enhanced error reporting
        logger.error(f"Error building DOCX for request ID {request_id}: {e}")
        logger.error(f"Error type: {type(e).__name__}")
        logger.error(f"Error details: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise 