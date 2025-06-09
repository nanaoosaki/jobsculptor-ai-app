"""
Bullet Error Categorization System (A7)

This module provides systematic error categorization for bullet consistency issues,
enabling targeted debugging and tracking of improvement effectiveness.

Key Features:
- Systematic error classification
- Root cause analysis
- Trending and analytics
- Targeted fix recommendations
- Integration with reconciliation engine

Author: Resume Tailor Team + O3 Expert Review
Status: A7 Implementation - Production Ready
"""

import logging
import time
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)


class ErrorCategory(Enum):
    """Primary error categories for bullet consistency issues."""
    # O3 Core Issues
    MISSING_NUMPR = "missing_numpr"                    # No <w:numPr> element
    INVALID_NUMID = "invalid_numid"                    # numId pointing to non-existent definition
    CORRUPT_XML = "corrupt_xml"                        # Malformed XML structure
    STYLE_MISMATCH = "style_mismatch"                  # Wrong style application
    
    # Architectural Issues  
    TIMING_RACE = "timing_race"                        # Build-phase verification brittleness
    STATE_CORRUPTION = "state_corruption"              # Document object model inconsistency
    NUMBERING_COLLISION = "numbering_collision"        # numId conflicts
    
    # Content Issues
    SANITIZATION_FAILURE = "sanitization_failure"     # Failed to clean bullet prefixes
    ENCODING_ISSUE = "encoding_issue"                  # Unicode/encoding problems
    MALFORMED_INPUT = "malformed_input"                # Invalid input data
    
    # Environmental Issues
    LIBRARY_BUG = "library_bug"                        # python-docx internal issues
    MEMORY_PRESSURE = "memory_pressure"                # System resource constraints
    CONCURRENT_ACCESS = "concurrent_access"            # Multi-threading issues
    
    # Edge Cases
    NESTED_STRUCTURE = "nested_structure"              # Complex document structures
    TEMPLATE_CONFLICT = "template_conflict"            # User template interference
    UNKNOWN = "unknown"                                # Unclassified errors


class ErrorSeverity(Enum):
    """Error severity levels."""
    CRITICAL = "critical"      # Complete bullet failure
    HIGH = "high"             # Partial bullet failure
    MEDIUM = "medium"         # Inconsistent formatting
    LOW = "low"               # Minor cosmetic issues
    INFO = "info"             # Informational/warning


@dataclass
class BulletError:
    """Individual bullet error data structure."""
    category: ErrorCategory
    severity: ErrorSeverity
    message: str
    paragraph_index: int
    paragraph_text: str
    xml_context: Optional[str]
    timestamp: float
    request_id: Optional[str]
    metadata: Dict[str, Any]


@dataclass
class ErrorPattern:
    """Error pattern for trend analysis."""
    category: ErrorCategory
    frequency: int
    contexts: List[str]
    first_seen: float
    last_seen: float
    examples: List[BulletError]


class BulletErrorCategorizer:
    """
    Systematic error categorization for bullet consistency issues.
    
    This categorizer implements A7 requirements:
    - Automatic error classification
    - Root cause analysis
    - Pattern detection and trending
    - Fix recommendation system
    - Integration with reconciliation engine
    """
    
    def __init__(self, request_id: Optional[str] = None):
        """Initialize error categorizer."""
        self.request_id = request_id
        self.errors: List[BulletError] = []
        self.patterns: Dict[ErrorCategory, ErrorPattern] = {}
        
    def categorize_error(self, error_context: Dict[str, Any]) -> BulletError:
        """
        Categorize a bullet consistency error.
        
        Args:
            error_context: Dictionary containing error details
            
        Returns:
            Categorized BulletError object
        """
        paragraph_index = error_context.get('paragraph_index', -1)
        paragraph_text = error_context.get('paragraph_text', '')
        xml_element = error_context.get('xml_element')
        error_message = error_context.get('error_message', '')
        exception = error_context.get('exception')
        
        # Analyze the error to determine category and severity
        category, severity, analysis = self._analyze_error(
            paragraph_text, xml_element, error_message, exception
        )
        
        # Create error object
        error = BulletError(
            category=category,
            severity=severity,
            message=analysis.get('message', error_message),
            paragraph_index=paragraph_index,
            paragraph_text=paragraph_text[:100],  # Truncate for storage
            xml_context=analysis.get('xml_context'),
            timestamp=time.time(),
            request_id=self.request_id,
            metadata=analysis.get('metadata', {})
        )
        
        # Track the error
        self.errors.append(error)
        self._update_patterns(error)
        
        logger.info(f"A7: Categorized error - {category.value}/{severity.value}: {error.message}")
        
        return error
    
    def _analyze_error(self, paragraph_text: str, xml_element: Any, 
                      error_message: str, exception: Optional[Exception]) -> Tuple[ErrorCategory, ErrorSeverity, Dict[str, Any]]:
        """
        Analyze error context to determine category and severity.
        
        Returns:
            Tuple of (category, severity, analysis_details)
        """
        analysis = {
            'message': error_message,
            'metadata': {},
            'xml_context': None
        }
        
        # Check for XML-related issues
        if xml_element is not None:
            xml_analysis = self._analyze_xml_issues(xml_element)
            if xml_analysis['category'] != ErrorCategory.UNKNOWN:
                return xml_analysis['category'], xml_analysis['severity'], xml_analysis
        
        # Check for content-related issues
        content_analysis = self._analyze_content_issues(paragraph_text, error_message)
        if content_analysis['category'] != ErrorCategory.UNKNOWN:
            return content_analysis['category'], content_analysis['severity'], content_analysis
        
        # Check for exception-based issues
        if exception:
            exception_analysis = self._analyze_exception_issues(exception)
            if exception_analysis['category'] != ErrorCategory.UNKNOWN:
                return exception_analysis['category'], exception_analysis['severity'], exception_analysis
        
        # Default categorization
        return ErrorCategory.UNKNOWN, ErrorSeverity.MEDIUM, analysis
    
    def _analyze_xml_issues(self, xml_element: Any) -> Dict[str, Any]:
        """Analyze XML-specific issues."""
        try:
            W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
            
            # Check for missing numPr
            pPr = xml_element.find(f'{W}pPr')
            if pPr is None:
                return {
                    'category': ErrorCategory.MISSING_NUMPR,
                    'severity': ErrorSeverity.HIGH,
                    'message': 'Missing paragraph properties (pPr) element',
                    'xml_context': str(xml_element.tag),
                    'metadata': {'issue': 'no_pPr'}
                }
            
            numPr = pPr.find(f'{W}numPr')
            if numPr is None:
                return {
                    'category': ErrorCategory.MISSING_NUMPR,
                    'severity': ErrorSeverity.CRITICAL,
                    'message': 'Missing numbering properties (numPr) element',
                    'xml_context': f'pPr exists but no numPr child',
                    'metadata': {'issue': 'no_numPr'}
                }
            
            # Check for invalid numId
            numId_elem = numPr.find(f'{W}numId')
            if numId_elem is None:
                return {
                    'category': ErrorCategory.INVALID_NUMID,
                    'severity': ErrorSeverity.HIGH,
                    'message': 'Missing numId element in numPr',
                    'xml_context': 'numPr exists but no numId',
                    'metadata': {'issue': 'no_numId'}
                }
            
            # Check for invalid numId value
            numId_val = numId_elem.get(f'{W}val')
            if not numId_val or not numId_val.isdigit():
                return {
                    'category': ErrorCategory.INVALID_NUMID,
                    'severity': ErrorSeverity.HIGH,
                    'message': f'Invalid numId value: {numId_val}',
                    'xml_context': f'numId val="{numId_val}"',
                    'metadata': {'issue': 'invalid_numId_value', 'numId': numId_val}
                }
            
            # If we get here, XML structure looks valid
            return {
                'category': ErrorCategory.UNKNOWN,
                'severity': ErrorSeverity.LOW,
                'message': 'XML structure appears valid',
                'metadata': {'numId': numId_val}
            }
            
        except Exception as e:
            return {
                'category': ErrorCategory.CORRUPT_XML,
                'severity': ErrorSeverity.CRITICAL,
                'message': f'XML parsing error: {e}',
                'xml_context': 'Unable to parse XML',
                'metadata': {'xml_error': str(e)}
            }
    
    def _analyze_content_issues(self, paragraph_text: str, error_message: str) -> Dict[str, Any]:
        """Analyze content-related issues."""
        
        # Check for encoding issues
        if any(char for char in paragraph_text if ord(char) > 65535):
            return {
                'category': ErrorCategory.ENCODING_ISSUE,
                'severity': ErrorSeverity.MEDIUM,
                'message': 'Text contains high Unicode characters that may cause issues',
                'metadata': {'issue': 'high_unicode', 'text_sample': paragraph_text[:50]}
            }
        
        # Check for pre-existing bullet characters (sanitization failure)
        bullet_chars = ['•', '·', '◦', '▪', '▫', '‣', '⁃', '-', '*']
        if any(paragraph_text.strip().startswith(char) for char in bullet_chars):
            return {
                'category': ErrorCategory.SANITIZATION_FAILURE,
                'severity': ErrorSeverity.MEDIUM,
                'message': f'Text contains pre-existing bullet character: {paragraph_text[:10]}',
                'metadata': {'issue': 'bullet_prefix', 'prefix': paragraph_text[:10]}
            }
        
        # Check for empty or malformed content
        if not paragraph_text or not paragraph_text.strip():
            return {
                'category': ErrorCategory.MALFORMED_INPUT,
                'severity': ErrorSeverity.LOW,
                'message': 'Empty or whitespace-only paragraph text',
                'metadata': {'issue': 'empty_text', 'length': len(paragraph_text)}
            }
        
        # Check for extremely long text that might cause issues
        if len(paragraph_text) > 1000:
            return {
                'category': ErrorCategory.MALFORMED_INPUT,
                'severity': ErrorSeverity.LOW,
                'message': f'Extremely long paragraph text ({len(paragraph_text)} chars)',
                'metadata': {'issue': 'long_text', 'length': len(paragraph_text)}
            }
        
        return {
            'category': ErrorCategory.UNKNOWN,
            'severity': ErrorSeverity.LOW,
            'message': 'Content appears normal',
            'metadata': {}
        }
    
    def _analyze_exception_issues(self, exception: Exception) -> Dict[str, Any]:
        """Analyze exception-based issues."""
        exception_name = type(exception).__name__
        exception_message = str(exception)
        
        # Memory-related exceptions
        if 'memory' in exception_message.lower() or exception_name in ['MemoryError', 'OSError']:
            return {
                'category': ErrorCategory.MEMORY_PRESSURE,
                'severity': ErrorSeverity.HIGH,
                'message': f'Memory-related error: {exception_message}',
                'metadata': {'exception_type': exception_name, 'exception_msg': exception_message}
            }
        
        # XML/parsing exceptions
        if 'xml' in exception_message.lower() or exception_name in ['XMLSyntaxError', 'ParseError']:
            return {
                'category': ErrorCategory.CORRUPT_XML,
                'severity': ErrorSeverity.CRITICAL,
                'message': f'XML error: {exception_message}',
                'metadata': {'exception_type': exception_name, 'exception_msg': exception_message}
            }
        
        # Attribute/access exceptions (potential library bugs)
        if exception_name in ['AttributeError', 'KeyError', 'IndexError']:
            return {
                'category': ErrorCategory.LIBRARY_BUG,
                'severity': ErrorSeverity.HIGH,
                'message': f'Library access error: {exception_message}',
                'metadata': {'exception_type': exception_name, 'exception_msg': exception_message}
            }
        
        # Threading/concurrency exceptions
        if 'thread' in exception_message.lower() or exception_name in ['ThreadError', 'RuntimeError']:
            return {
                'category': ErrorCategory.CONCURRENT_ACCESS,
                'severity': ErrorSeverity.MEDIUM,
                'message': f'Concurrency error: {exception_message}',
                'metadata': {'exception_type': exception_name, 'exception_msg': exception_message}
            }
        
        return {
            'category': ErrorCategory.UNKNOWN,
            'severity': ErrorSeverity.MEDIUM,
            'message': f'Unclassified exception: {exception_name}: {exception_message}',
            'metadata': {'exception_type': exception_name, 'exception_msg': exception_message}
        }
    
    def _update_patterns(self, error: BulletError):
        """Update error patterns for trend analysis."""
        category = error.category
        
        if category not in self.patterns:
            self.patterns[category] = ErrorPattern(
                category=category,
                frequency=0,
                contexts=[],
                first_seen=error.timestamp,
                last_seen=error.timestamp,
                examples=[]
            )
        
        pattern = self.patterns[category]
        pattern.frequency += 1
        pattern.last_seen = error.timestamp
        pattern.contexts.append(f"{error.severity.value}: {error.message}")
        
        # Keep only recent examples (max 5)
        pattern.examples.append(error)
        if len(pattern.examples) > 5:
            pattern.examples.pop(0)
    
    def get_error_summary(self) -> Dict[str, Any]:
        """Get comprehensive error summary."""
        if not self.errors:
            return {"message": "No errors recorded"}
        
        # Count by category and severity
        category_counts = {}
        severity_counts = {}
        
        for error in self.errors:
            category_counts[error.category.value] = category_counts.get(error.category.value, 0) + 1
            severity_counts[error.severity.value] = severity_counts.get(error.severity.value, 0) + 1
        
        # Most frequent categories
        top_categories = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            "total_errors": len(self.errors),
            "category_breakdown": category_counts,
            "severity_breakdown": severity_counts,
            "top_categories": top_categories,
            "patterns_detected": len(self.patterns),
            "request_id": self.request_id
        }
    
    def get_fix_recommendations(self) -> List[Dict[str, Any]]:
        """Get targeted fix recommendations based on error patterns."""
        recommendations = []
        
        for category, pattern in self.patterns.items():
            if pattern.frequency < 2:  # Skip infrequent issues
                continue
                
            rec = self._get_category_recommendation(category, pattern)
            if rec:
                recommendations.append(rec)
        
        # Sort by impact (frequency * severity weight)
        severity_weights = {
            ErrorSeverity.CRITICAL: 4,
            ErrorSeverity.HIGH: 3,
            ErrorSeverity.MEDIUM: 2,
            ErrorSeverity.LOW: 1,
            ErrorSeverity.INFO: 0.5
        }
        
        def calculate_impact(rec):
            freq = rec.get('frequency', 0)
            severity = rec.get('typical_severity', ErrorSeverity.MEDIUM)
            return freq * severity_weights.get(severity, 1)
        
        recommendations.sort(key=calculate_impact, reverse=True)
        
        return recommendations
    
    def _get_category_recommendation(self, category: ErrorCategory, pattern: ErrorPattern) -> Optional[Dict[str, Any]]:
        """Get specific recommendation for error category."""
        
        recommendations_map = {
            ErrorCategory.MISSING_NUMPR: {
                "issue": "Paragraphs missing numbering properties",
                "cause": "Build-phase timing issues or reconciliation failures",
                "fix": "Enhance reconciliation engine to ensure all MR_BulletPoint paragraphs get numPr",
                "priority": "HIGH",
                "code_areas": ["utils/bullet_reconciliation.py", "utils/docx_builder.py"]
            },
            ErrorCategory.INVALID_NUMID: {
                "issue": "Invalid or missing numId references",
                "cause": "Numbering definition not created or collision with existing IDs",
                "fix": "Implement B9 improvements for numId collision prevention",
                "priority": "HIGH", 
                "code_areas": ["word_styles/numbering_engine.py"]
            },
            ErrorCategory.SANITIZATION_FAILURE: {
                "issue": "Pre-existing bullet characters not cleaned",
                "cause": "B3 sanitization not covering all bullet types",
                "fix": "Enhance B3 unicode bullet detection in create_bullet_point",
                "priority": "MEDIUM",
                "code_areas": ["utils/docx_builder.py"]
            },
            ErrorCategory.TIMING_RACE: {
                "issue": "Build-phase verification brittleness",
                "cause": "Old verify-in-loop architecture still active",
                "fix": "Complete transition to build-then-reconcile architecture",
                "priority": "HIGH",
                "code_areas": ["utils/docx_builder.py", "word_styles/numbering_engine.py"]
            },
            ErrorCategory.STYLE_MISMATCH: {
                "issue": "Wrong style application to paragraphs",
                "cause": "Style creation or application failures",
                "fix": "Enhance B1 style collision handling and style verification",
                "priority": "MEDIUM",
                "code_areas": ["utils/docx_builder.py", "style_engine.py"]
            }
        }
        
        if category not in recommendations_map:
            return None
        
        base_rec = recommendations_map[category]
        base_rec.update({
            "category": category.value,
            "frequency": pattern.frequency,
            "first_seen": pattern.first_seen,
            "last_seen": pattern.last_seen,
            "typical_severity": max(pattern.examples, key=lambda e: e.severity.value).severity if pattern.examples else ErrorSeverity.MEDIUM
        })
        
        return base_rec 