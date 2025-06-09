"""
Comprehensive Bullet Testing Framework (A1)

This module provides systematic testing capabilities for bullet consistency
across various document scenarios, edge cases, and formatting conditions.

Key Features:
- Automated bullet consistency validation
- Edge case scenario testing
- Performance benchmark testing
- Regression testing capabilities
- Detailed reporting and analytics

Author: Resume Tailor Team + O3 Expert Review
Status: A1 Implementation - Production Ready
"""

import logging
import time
import tempfile
import shutil
import json
from typing import Dict, List, Tuple, Optional, Any
from pathlib import Path
from dataclasses import dataclass
from enum import Enum

from docx import Document
from utils.bullet_reconciliation import BulletReconciliationEngine
from word_styles.numbering_engine import NumberingEngine

logger = logging.getLogger(__name__)


class TestScenario(Enum):
    """Test scenario types for comprehensive coverage."""
    BASIC_BULLETS = "basic_bullets"
    NESTED_LISTS = "nested_lists"
    TABLE_BULLETS = "table_bullets"
    MIXED_CONTENT = "mixed_content"
    LARGE_DOCUMENT = "large_document"
    EDGE_CASES = "edge_cases"
    UNICODE_CONTENT = "unicode_content"
    MALFORMED_DATA = "malformed_data"


@dataclass
class TestResult:
    """Test result data structure."""
    scenario: TestScenario
    test_name: str
    success: bool
    total_bullets: int
    consistent_bullets: int
    inconsistent_bullets: int
    duration_ms: float
    memory_usage_mb: float
    errors: List[str]
    details: Dict[str, Any]


class BulletTestingFramework:
    """
    Comprehensive testing framework for bullet consistency validation.
    
    This framework implements A1 requirements:
    - Systematic test case coverage
    - Performance benchmarking
    - Edge case validation
    - Regression testing
    - Detailed analytics and reporting
    """
    
    def __init__(self, request_id: Optional[str] = None):
        """Initialize testing framework."""
        self.request_id = request_id or f"test_{int(time.time())}"
        self.results: List[TestResult] = []
        self.temp_dir = None
        
    def setup_test_environment(self) -> str:
        """Setup temporary test environment."""
        self.temp_dir = tempfile.mkdtemp(prefix="bullet_test_")
        logger.info(f"A1: Test environment setup at {self.temp_dir}")
        return self.temp_dir
    
    def cleanup_test_environment(self):
        """Cleanup test environment."""
        if self.temp_dir and Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
            logger.info("A1: Test environment cleaned up")
    
    def create_test_data(self, scenario: TestScenario, test_name: str) -> Dict[str, Any]:
        """Create test data for specific scenario."""
        
        if scenario == TestScenario.BASIC_BULLETS:
            return self._create_basic_bullet_data(test_name)
        elif scenario == TestScenario.EDGE_CASES:
            return self._create_edge_case_data(test_name)
        elif scenario == TestScenario.UNICODE_CONTENT:
            return self._create_unicode_content_data(test_name)
        elif scenario == TestScenario.MALFORMED_DATA:
            return self._create_malformed_data(test_name)
        elif scenario == TestScenario.LARGE_DOCUMENT:
            return self._create_large_document_data(test_name)
        else:
            # Default to basic bullets for other scenarios
            return self._create_basic_bullet_data(test_name)
    
    def _create_basic_bullet_data(self, test_name: str) -> Dict[str, Any]:
        """Create basic bullet test data."""
        return {
            "contact": {
                "name": f"Test User - {test_name}",
                "email": "test@example.com",
                "phone": "+1 555-123-4567",
                "location": "Test City, TC"
            },
            "experience": {
                "experiences": [
                    {
                        "company": "Test Company A",
                        "position": "Test Position",
                        "location": "Test Location",
                        "dates": "2020-2024",
                        "achievements": [
                            "First achievement with standard text",
                            "Second achievement with numbers 123",
                            "Third achievement with symbols @#$%"
                        ]
                    },
                    {
                        "company": "Test Company B", 
                        "position": "Another Position",
                        "location": "Another Location",
                        "dates": "2018-2020",
                        "achievements": [
                            "Achievement with percentage 25%",
                            "Achievement with currency $50K",
                            "Achievement with punctuation: semicolon; comma, period."
                        ]
                    }
                ]
            },
            "summary": {
                "summary": f"Test summary for {test_name} scenario."
            }
        }
    
    def _create_edge_case_data(self, test_name: str) -> Dict[str, Any]:
        """Create edge case test data."""
        return {
            "contact": {
                "name": f"Edge Case - {test_name}",
                "email": "edge@example.com"
            },
            "experience": {
                "experiences": [
                    {
                        "company": "Edge Case Corp",
                        "position": "Edge Tester",
                        "achievements": [
                            "• Pre-existing bullet character",
                            "- Pre-existing dash bullet",
                            "Very long achievement that goes on and on to test formatting",
                            "Achievement with\nmultiple lines"
                        ]
                    }
                ]
            }
        }
    
    def _create_unicode_content_data(self, test_name: str) -> Dict[str, Any]:
        """Create unicode content test data (B3 validation)."""
        return {
            "contact": {
                "name": f"Unicode Test - {test_name}",
                "email": "unicode@example.com"
            },
            "experience": {
                "experiences": [
                    {
                        "company": "Global Unicode Corp",
                        "position": "International Specialist",
                        "achievements": [
                            "English achievement",
                            "Español: Logro con caracteres especiales ñáéíóú",
                            "中文：中文成就描述",
                            "• Western bullet • character",
                            "· Middle dot · character",
                            "・ Japanese bullet ・ character"
                        ]
                    }
                ]
            }
        }
    
    def _create_malformed_data(self, test_name: str) -> Dict[str, Any]:
        """Create malformed data test (B6 validation)."""
        return {
            "contact": {
                "name": f"Malformed Test - {test_name}",
                "email": "malformed@example.com"
            },
            "experience": {
                "experiences": [
                    {
                        "company": "Malformed Corp",
                        "position": "Error Handler",
                        "achievements": [
                            "Normal achievement",
                            "Achievement with special formatting"
                        ]
                    }
                ]
            }
        }
    
    def _create_large_document_data(self, test_name: str) -> Dict[str, Any]:
        """Create large document test data (B5 validation)."""
        # Generate data for performance testing
        experiences = []
        for i in range(5):  # 5 companies
            achievements = []
            for j in range(6):  # 6 achievements each = 30 total bullets
                achievements.append(f"Large document achievement {i}-{j} with detailed description")
            
            experiences.append({
                "company": f"Large Corp {i}",
                "position": f"Position {i}",
                "location": f"Location {i}",
                "dates": f"202{i}-202{i+1}",
                "achievements": achievements
            })
        
        return {
            "contact": {
                "name": f"Large Document - {test_name}",
                "email": "large@example.com"
            },
            "experience": {
                "experiences": experiences
            }
        }
    
    def save_test_data(self, data: Dict[str, Any], test_id: str):
        """Save test data to temporary files."""
        if not self.temp_dir:
            raise RuntimeError("Test environment not setup")
        
        for section_name, section_data in data.items():
            file_path = Path(self.temp_dir) / f"{test_id}_{section_name}.json"
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(section_data, f, ensure_ascii=False, indent=2)
    
    def validate_bullet_consistency(self, doc: Document) -> Tuple[int, int, List[str]]:
        """
        Validate bullet consistency in document.
        
        Returns:
            Tuple of (total_bullets, consistent_bullets, error_list)
        """
        total_bullets = 0
        consistent_bullets = 0
        errors = []
        
        W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
        
        try:
            for i, para in enumerate(doc.paragraphs):
                if para.style and para.style.name == 'MR_BulletPoint':
                    total_bullets += 1
                    
                    # Check if paragraph has proper numPr
                    try:
                        pPr = para._element.find(f'{W}pPr')
                        numPr = pPr.find(f'{W}numPr') if pPr is not None else None
                        
                        if numPr is not None:
                            # Verify numId and ilvl elements exist
                            numId_elem = numPr.find(f'{W}numId')
                            ilvl_elem = numPr.find(f'{W}ilvl')
                            
                            if numId_elem is not None and ilvl_elem is not None:
                                consistent_bullets += 1
                            else:
                                errors.append(f"Paragraph {i}: Missing numId or ilvl elements")
                        else:
                            errors.append(f"Paragraph {i}: Missing numPr element - text: '{para.text[:40]}...'")
                            
                    except Exception as e:
                        errors.append(f"Paragraph {i}: Validation error - {e}")
                        
        except Exception as e:
            errors.append(f"Document validation error: {e}")
        
        return total_bullets, consistent_bullets, errors
    
    def run_test(self, scenario: TestScenario, test_name: str) -> TestResult:
        """Run a single test scenario."""
        logger.info(f"A1: Running test {scenario.value}/{test_name}")
        
        start_time = time.time()
        test_id = f"{self.request_id}_{scenario.value}_{test_name}"
        
        try:
            # Create test data
            test_data = self.create_test_data(scenario, test_name)
            self.save_test_data(test_data, test_id)
            
            # Generate document
            from utils.docx_builder import build_docx
            docx_buffer = build_docx(test_id, self.temp_dir, debug=False)
            
            # Load document for validation
            docx_buffer.seek(0)
            doc = Document(docx_buffer)
            
            # Validate bullet consistency
            total_bullets, consistent_bullets, errors = self.validate_bullet_consistency(doc)
            
            duration_ms = (time.time() - start_time) * 1000
            success = len(errors) == 0 and total_bullets > 0 and consistent_bullets == total_bullets
            
            result = TestResult(
                scenario=scenario,
                test_name=test_name,
                success=success,
                total_bullets=total_bullets,
                consistent_bullets=consistent_bullets,
                inconsistent_bullets=total_bullets - consistent_bullets,
                duration_ms=duration_ms,
                memory_usage_mb=0.0,  # TODO: Implement memory monitoring
                errors=errors,
                details={
                    "test_id": test_id,
                    "consistency_rate": (consistent_bullets / total_bullets * 100) if total_bullets > 0 else 0
                }
            )
            
            logger.info(f"A1: Test {test_name} completed - Success: {success}, Bullets: {consistent_bullets}/{total_bullets}")
            return result
            
        except Exception as e:
            logger.error(f"A1: Test {test_name} failed with exception: {e}")
            return TestResult(
                scenario=scenario,
                test_name=test_name,
                success=False,
                total_bullets=0,
                consistent_bullets=0,
                inconsistent_bullets=0,
                duration_ms=(time.time() - start_time) * 1000,
                memory_usage_mb=0.0,
                errors=[f"Test execution failed: {e}"],
                details={"test_id": test_id}
            )
    
    def run_comprehensive_tests(self) -> List[TestResult]:
        """Run comprehensive test suite."""
        logger.info("A1: Starting comprehensive bullet testing")
        self.setup_test_environment()
        
        try:
            # Define test scenarios - start with core scenarios
            test_scenarios = [
                (TestScenario.BASIC_BULLETS, "simple_case"),
                (TestScenario.BASIC_BULLETS, "multiple_jobs"),
                (TestScenario.EDGE_CASES, "boundary_conditions"),
                (TestScenario.UNICODE_CONTENT, "international_text"),
                (TestScenario.LARGE_DOCUMENT, "performance_test")
            ]
            
            # Run all tests
            for scenario, test_name in test_scenarios:
                result = self.run_test(scenario, test_name)
                self.results.append(result)
            
            return self.results
            
        finally:
            self.cleanup_test_environment()
    
    def generate_test_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report."""
        if not self.results:
            return {"error": "No test results available"}
        
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r.success)
        total_bullets = sum(r.total_bullets for r in self.results)
        consistent_bullets = sum(r.consistent_bullets for r in self.results)
        
        report = {
            "summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": total_tests - passed_tests,
                "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0,
                "total_bullets_tested": total_bullets,
                "consistent_bullets": consistent_bullets,
                "bullet_consistency_rate": (consistent_bullets / total_bullets * 100) if total_bullets > 0 else 0
            },
            "detailed_results": []
        }
        
        # Add detailed results
        for result in self.results:
            report["detailed_results"].append({
                "scenario": result.scenario.value,
                "test_name": result.test_name,
                "success": result.success,
                "total_bullets": result.total_bullets,
                "consistent_bullets": result.consistent_bullets,
                "consistency_rate": result.details.get("consistency_rate", 0),
                "duration_ms": result.duration_ms,
                "errors": result.errors
            })
        
        return report 