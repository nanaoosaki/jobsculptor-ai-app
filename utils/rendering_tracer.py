"""
Rendering Path Tracer with Decorator

This module provides a decorator-based tracing system to track which rendering
paths are being executed. It helps identify dual rendering paths and architectural
smells in the typography system.
"""

import logging
import functools
import time
from typing import Callable, Any
from collections import defaultdict
import threading

# Create dedicated tracer logger
tracer = logging.getLogger('rendering.tracer')
tracer.setLevel(logging.INFO)

# Thread-safe call tracking
_call_stats = defaultdict(lambda: {'count': 0, 'total_time': 0.0})
_stats_lock = threading.Lock()

def trace(component_name: str):
    """
    Decorator to trace rendering path execution
    
    Args:
        component_name: Logical component name (e.g., "docx.section_header")
    
    Usage:
        @trace("docx.section_header")
        def add_section_header(doc, section_name):
            # ... existing code
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            call_id = f"{component_name}.{func.__name__}"
            
            # Log entry
            tracer.info(f"RENDER_PATH: {call_id} called")
            
            try:
                result = func(*args, **kwargs)
                
                # Log success
                end_time = time.time()
                duration = end_time - start_time
                tracer.info(f"RENDER_PATH: {call_id} completed in {duration:.3f}s")
                
                # Update stats
                with _stats_lock:
                    _call_stats[call_id]['count'] += 1
                    _call_stats[call_id]['total_time'] += duration
                
                return result
                
            except Exception as e:
                # Log failure
                end_time = time.time()
                duration = end_time - start_time
                tracer.error(f"RENDER_PATH: {call_id} failed after {duration:.3f}s: {e}")
                raise
        
        return wrapper
    return decorator

def get_rendering_stats() -> dict:
    """Get statistics about rendering path usage"""
    with _stats_lock:
        stats = {}
        for call_id, data in _call_stats.items():
            stats[call_id] = {
                'call_count': data['count'],
                'total_time': data['total_time'],
                'avg_time': data['total_time'] / data['count'] if data['count'] > 0 else 0
            }
    return stats

def reset_rendering_stats():
    """Reset rendering statistics"""
    with _stats_lock:
        _call_stats.clear()

def log_rendering_summary():
    """Log a summary of rendering path usage"""
    stats = get_rendering_stats()
    
    if not stats:
        tracer.info("RENDER_SUMMARY: No rendering paths traced")
        return
    
    tracer.info("RENDER_SUMMARY: Rendering path usage summary:")
    
    # Group by component
    by_component = defaultdict(list)
    for call_id, call_stats in stats.items():
        component = call_id.split('.')[0] if '.' in call_id else 'unknown'
        by_component[component].append((call_id, call_stats))
    
    for component, calls in by_component.items():
        tracer.info(f"RENDER_SUMMARY:   {component}:")
        for call_id, call_stats in calls:
            tracer.info(f"RENDER_SUMMARY:     {call_id}: {call_stats['call_count']} calls, "
                       f"{call_stats['avg_time']:.3f}s avg")

def detect_dual_paths():
    """
    Detect potential dual rendering paths
    
    Returns a report of potential architectural smells based on call patterns
    """
    stats = get_rendering_stats()
    issues = []
    
    # Look for multiple section header implementations
    section_header_calls = [call_id for call_id in stats.keys() if 'section_header' in call_id.lower()]
    if len(section_header_calls) > 1:
        issues.append({
            'type': 'dual_section_header_paths',
            'description': f"Multiple section header implementations called: {section_header_calls}",
            'paths': section_header_calls,
            'recommendation': "Consolidate to single section header renderer"
        })
    
    # Look for inconsistent call patterns
    for call_id, call_stats in stats.items():
        if 'legacy' in call_id.lower() and call_stats['call_count'] > 0:
            issues.append({
                'type': 'legacy_path_usage',
                'description': f"Legacy rendering path still in use: {call_id}",
                'call_count': call_stats['call_count'],
                'recommendation': f"Remove or replace legacy path: {call_id}"
            })
    
    return issues

class RenderingTraceContext:
    """Context manager for temporary tracing of a code block"""
    
    def __init__(self, context_name: str):
        self.context_name = context_name
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        tracer.info(f"RENDER_CONTEXT: {self.context_name} started")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        if exc_type is None:
            tracer.info(f"RENDER_CONTEXT: {self.context_name} completed in {duration:.3f}s")
        else:
            tracer.error(f"RENDER_CONTEXT: {self.context_name} failed after {duration:.3f}s: {exc_val}")

def setup_rendering_logger(log_file: str = None, console_level: str = "INFO"):
    """
    Set up the rendering tracer logger with appropriate handlers
    
    Args:
        log_file: Optional file to write logs to
        console_level: Console logging level (DEBUG, INFO, WARNING, ERROR)
    """
    # Clear existing handlers
    tracer.handlers.clear()
    
    # Set up formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, console_level.upper()))
    console_handler.setFormatter(formatter)
    tracer.addHandler(console_handler)
    
    # File handler if requested
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        tracer.addHandler(file_handler)
    
    tracer.setLevel(logging.DEBUG)

# Example usage and testing functions
def example_traced_function():
    """Example of how to use the trace decorator"""
    
    @trace("example.component")
    def process_data(data):
        time.sleep(0.1)  # Simulate work
        return f"processed: {data}"
    
    @trace("example.renderer")
    def render_output(processed_data):
        time.sleep(0.05)  # Simulate work
        return f"rendered: {processed_data}"
    
    # Use the functions
    with RenderingTraceContext("example_workflow"):
        data = process_data("test_data")
        result = render_output(data)
        return result

if __name__ == "__main__":
    # Demo the tracing system
    setup_rendering_logger(console_level="INFO")
    
    # Run example
    result = example_traced_function()
    
    # Show stats
    log_rendering_summary()
    
    # Check for issues
    issues = detect_dual_paths()
    if issues:
        print("\n🚨 Detected rendering path issues:")
        for issue in issues:
            print(f"  - {issue['type']}: {issue['description']}")
    else:
        print("\n✅ No rendering path issues detected") 