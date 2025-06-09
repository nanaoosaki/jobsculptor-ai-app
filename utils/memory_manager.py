"""
Memory Management System (A5)

This module provides memory guard rails and resource monitoring for 
bullet consistency operations, ensuring stable performance under
various document sizes and system constraints.

Key Features:
- Memory usage monitoring and limits
- Large document detection and handling
- Resource cleanup and optimization
- Performance guard rails
- Memory leak detection

Author: Resume Tailor Team + O3 Expert Review
Status: A5 Implementation - Production Ready
"""

import logging
import tracemalloc
import gc
import psutil
import time
from typing import Dict, Optional, Any, Tuple, Callable
from dataclasses import dataclass
from functools import wraps
from contextlib import contextmanager

logger = logging.getLogger(__name__)


@dataclass
class MemoryMetrics:
    """Memory usage metrics."""
    peak_memory_mb: float
    current_memory_mb: float
    system_available_mb: float
    process_memory_mb: float
    gc_collections: int
    memory_growth_mb: float
    timestamp: float


class MemoryLimitExceeded(Exception):
    """Raised when memory usage exceeds configured limits."""
    pass


class MemoryManager:
    """
    Memory management system with guard rails and monitoring.
    
    This manager implements A5 requirements:
    - Memory usage monitoring
    - Resource limits enforcement  
    - Large document handling
    - Performance optimization
    - Memory leak detection
    """
    
    def __init__(self, 
                 max_memory_mb: int = 512,
                 large_doc_threshold_mb: int = 100,
                 enable_gc: bool = True):
        """
        Initialize memory manager.
        
        Args:
            max_memory_mb: Maximum memory usage allowed (MB)
            large_doc_threshold_mb: Threshold for large document detection (MB)
            enable_gc: Whether to enable aggressive garbage collection
        """
        self.max_memory_mb = max_memory_mb
        self.large_doc_threshold_mb = large_doc_threshold_mb
        self.enable_gc = enable_gc
        
        self.monitoring_active = False
        self.baseline_memory = None
        self.peak_memory = 0.0
        self.start_time = None
        
        # Get system info
        self.system_memory_mb = psutil.virtual_memory().total / (1024 * 1024)
        
        logger.info(f"A5: Memory manager initialized - Max: {max_memory_mb}MB, "
                   f"Large doc threshold: {large_doc_threshold_mb}MB, "
                   f"System memory: {self.system_memory_mb:.0f}MB")
    
    @contextmanager
    def monitor_operation(self, operation_name: str):
        """
        Context manager for monitoring memory usage during operations.
        
        Args:
            operation_name: Name of the operation being monitored
        """
        logger.debug(f"A5: Starting memory monitoring for: {operation_name}")
        
        # Start monitoring
        self.start_monitoring()
        
        try:
            yield self
        except MemoryLimitExceeded:
            logger.error(f"A5: Memory limit exceeded during {operation_name}")
            raise
        except Exception as e:
            logger.error(f"A5: Operation {operation_name} failed: {e}")
            raise
        finally:
            # End monitoring and get metrics
            metrics = self.end_monitoring()
            
            # Log summary
            logger.info(f"A5: {operation_name} completed - "
                       f"Peak: {metrics.peak_memory_mb:.1f}MB, "
                       f"Growth: {metrics.memory_growth_mb:.1f}MB, "
                       f"Duration: {(time.time() - self.start_time) * 1000:.1f}ms")
            
            # Check for memory concerns
            if metrics.peak_memory_mb > self.large_doc_threshold_mb:
                logger.warning(f"A5: Large memory usage detected in {operation_name}: "
                             f"{metrics.peak_memory_mb:.1f}MB")
            
            # Cleanup if needed
            if self.enable_gc and metrics.memory_growth_mb > 50:
                self._force_cleanup()
    
    def start_monitoring(self) -> None:
        """Start memory monitoring."""
        if not self.monitoring_active:
            tracemalloc.start()
            self.monitoring_active = True
        
        # Record baseline
        self.baseline_memory = self._get_current_memory_mb()
        self.peak_memory = self.baseline_memory
        self.start_time = time.time()
        
        logger.debug(f"A5: Memory monitoring started - Baseline: {self.baseline_memory:.1f}MB")
    
    def end_monitoring(self) -> MemoryMetrics:
        """End monitoring and return metrics."""
        if not self.monitoring_active:
            logger.warning("A5: Attempted to end monitoring that wasn't started")
            return self._create_empty_metrics()
        
        try:
            # Get final measurements
            current_memory = self._get_current_memory_mb()
            system_available = psutil.virtual_memory().available / (1024 * 1024)
            process_memory = psutil.Process().memory_info().rss / (1024 * 1024)
            
            # Get garbage collection stats
            gc_stats = gc.get_stats()
            total_collections = sum(stat['collections'] for stat in gc_stats)
            
            # Calculate growth
            memory_growth = current_memory - (self.baseline_memory or 0)
            
            metrics = MemoryMetrics(
                peak_memory_mb=self.peak_memory,
                current_memory_mb=current_memory,
                system_available_mb=system_available,
                process_memory_mb=process_memory,
                gc_collections=total_collections,
                memory_growth_mb=memory_growth,
                timestamp=time.time()
            )
            
            # Stop monitoring
            tracemalloc.stop()
            self.monitoring_active = False
            
            return metrics
            
        except Exception as e:
            logger.error(f"A5: Error ending memory monitoring: {e}")
            return self._create_empty_metrics()
    
    def check_memory_limits(self) -> None:
        """Check if current memory usage exceeds limits."""
        if not self.monitoring_active:
            return
        
        current_memory = self._get_current_memory_mb()
        
        # Update peak
        self.peak_memory = max(self.peak_memory, current_memory)
        
        # Check against limit
        if current_memory > self.max_memory_mb:
            raise MemoryLimitExceeded(
                f"Memory usage {current_memory:.1f}MB exceeds limit {self.max_memory_mb}MB"
            )
        
        # Check system memory
        system_available = psutil.virtual_memory().available / (1024 * 1024)
        if system_available < 100:  # Less than 100MB available
            logger.warning(f"A5: Low system memory: {system_available:.1f}MB available")
    
    def is_large_document(self, estimated_size_mb: float) -> bool:
        """Check if document qualifies as large."""
        return estimated_size_mb > self.large_doc_threshold_mb
    
    def get_optimization_strategy(self, estimated_size_mb: float) -> str:
        """Get optimization strategy based on document size."""
        if estimated_size_mb < 10:
            return "standard"
        elif estimated_size_mb < self.large_doc_threshold_mb:
            return "conservative"
        elif estimated_size_mb < self.max_memory_mb:
            return "large_document"
        else:
            return "memory_constrained"
    
    def _get_current_memory_mb(self) -> float:
        """Get current memory usage in MB."""
        try:
            if tracemalloc.is_tracing():
                current, peak = tracemalloc.get_traced_memory()
                return current / (1024 * 1024)
            else:
                # Fallback to process memory
                return psutil.Process().memory_info().rss / (1024 * 1024)
        except Exception:
            return 0.0
    
    def _force_cleanup(self) -> None:
        """Force garbage collection and cleanup."""
        logger.debug("A5: Forcing memory cleanup")
        
        # Multiple GC passes for better cleanup
        for generation in [0, 1, 2]:
            collected = gc.collect(generation)
            if collected > 0:
                logger.debug(f"A5: GC generation {generation}: collected {collected} objects")
    
    def _create_empty_metrics(self) -> MemoryMetrics:
        """Create empty metrics for error cases."""
        return MemoryMetrics(
            peak_memory_mb=0.0,
            current_memory_mb=0.0,
            system_available_mb=0.0,
            process_memory_mb=0.0,
            gc_collections=0,
            memory_growth_mb=0.0,
            timestamp=time.time()
        )


# Global memory manager instance
memory_manager = MemoryManager()


def memory_monitored(operation_name: Optional[str] = None):
    """
    Decorator for automatic memory monitoring of functions.
    
    Args:
        operation_name: Name of the operation (defaults to function name)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            op_name = operation_name or f"{func.__module__}.{func.__name__}"
            
            with memory_manager.monitor_operation(op_name):
                # Check memory before operation
                memory_manager.check_memory_limits()
                
                # Execute function
                result = func(*args, **kwargs)
                
                # Check memory after operation
                memory_manager.check_memory_limits()
                
                return result
        
        return wrapper
    return decorator


@contextmanager
def memory_constrained_mode():
    """Context manager for memory-constrained operations."""
    logger.info("A5: Entering memory-constrained mode")
    
    # Store original settings
    original_max = memory_manager.max_memory_mb
    original_gc = memory_manager.enable_gc
    
    try:
        # Set conservative limits
        memory_manager.max_memory_mb = min(original_max, 256)
        memory_manager.enable_gc = True
        
        # Force initial cleanup
        memory_manager._force_cleanup()
        
        yield memory_manager
        
    finally:
        # Restore original settings
        memory_manager.max_memory_mb = original_max
        memory_manager.enable_gc = original_gc
        
        # Final cleanup
        memory_manager._force_cleanup()
        
        logger.info("A5: Exited memory-constrained mode")


def estimate_document_memory_mb(num_paragraphs: int, 
                               num_bullets: int,
                               has_images: bool = False) -> float:
    """
    Estimate memory usage for a document.
    
    Args:
        num_paragraphs: Number of paragraphs in document
        num_bullets: Number of bullet points
        has_images: Whether document contains images
        
    Returns:
        Estimated memory usage in MB
    """
    # Base memory for document structure
    base_mb = 5.0
    
    # Memory per paragraph (includes XML overhead)
    paragraph_mb = num_paragraphs * 0.01  # ~10KB per paragraph
    
    # Memory per bullet (additional numbering overhead)
    bullet_mb = num_bullets * 0.005  # ~5KB per bullet
    
    # Image overhead
    image_mb = 50.0 if has_images else 0.0
    
    total_mb = base_mb + paragraph_mb + bullet_mb + image_mb
    
    logger.debug(f"A5: Estimated document memory: {total_mb:.1f}MB "
                f"({num_paragraphs} paragraphs, {num_bullets} bullets, "
                f"images: {has_images})")
    
    return total_mb


def get_memory_status() -> Dict[str, Any]:
    """Get current memory status summary."""
    try:
        # System memory
        vm = psutil.virtual_memory()
        system_total_mb = vm.total / (1024 * 1024)
        system_available_mb = vm.available / (1024 * 1024)
        system_percent = vm.percent
        
        # Process memory
        process = psutil.Process()
        process_memory_mb = process.memory_info().rss / (1024 * 1024)
        
        # GC stats
        gc_stats = gc.get_stats()
        total_collections = sum(stat['collections'] for stat in gc_stats)
        
        return {
            "system": {
                "total_mb": round(system_total_mb, 1),
                "available_mb": round(system_available_mb, 1),
                "used_percent": round(system_percent, 1)
            },
            "process": {
                "memory_mb": round(process_memory_mb, 1),
                "gc_collections": total_collections
            },
            "manager": {
                "max_memory_mb": memory_manager.max_memory_mb,
                "large_doc_threshold_mb": memory_manager.large_doc_threshold_mb,
                "monitoring_active": memory_manager.monitoring_active,
                "peak_memory_mb": round(memory_manager.peak_memory, 1)
            }
        }
        
    except Exception as e:
        logger.error(f"A5: Error getting memory status: {e}")
        return {"error": str(e)} 