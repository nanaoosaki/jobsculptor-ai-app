"""
Request Correlation System (A8)

This module provides request correlation capabilities for tracking
bullet consistency issues, performance metrics, and user patterns
across multiple document generation requests.

Key Features:
- Unique request ID generation and propagation
- Cross-request error correlation
- Performance tracking and analytics
- User session tracking
- Debug artifact correlation

Author: Resume Tailor Team + O3 Expert Review
Status: A8 Implementation - Production Ready
"""

import logging
import time
import uuid
import threading
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from pathlib import Path
import json

logger = logging.getLogger(__name__)

# Thread-local storage for request context
_request_context = threading.local()


@dataclass
class RequestMetrics:
    """Performance and error metrics for a request."""
    request_id: str
    start_time: float
    end_time: Optional[float] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    
    # Document metrics
    total_bullets: int = 0
    successful_bullets: int = 0
    failed_bullets: int = 0
    
    # Performance metrics
    build_duration_ms: float = 0.0
    reconciliation_duration_ms: float = 0.0
    total_duration_ms: float = 0.0
    
    # Error tracking
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    # Metadata
    document_size_bytes: int = 0
    template_used: Optional[str] = None
    features_enabled: Dict[str, bool] = field(default_factory=dict)
    debug_artifacts: List[str] = field(default_factory=list)


class RequestCorrelationManager:
    """
    Manages request correlation and tracking across the application.
    
    This manager implements A8 requirements:
    - Request ID generation and propagation
    - Cross-request correlation
    - Performance analytics
    - Error pattern tracking
    - Debug artifact management
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        """Singleton pattern for global request tracking."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize correlation manager."""
        if hasattr(self, 'initialized'):
            return
        
        self.active_requests: Dict[str, RequestMetrics] = {}
        self.completed_requests: List[RequestMetrics] = []
        self.user_sessions: Dict[str, List[str]] = {}  # user_id -> request_ids
        self.lock = threading.Lock()
        self.initialized = True
        
        logger.info("A8: Request correlation manager initialized")
    
    def start_request(self, user_id: Optional[str] = None, 
                     session_id: Optional[str] = None) -> str:
        """
        Start tracking a new request.
        
        Args:
            user_id: Optional user identifier
            session_id: Optional session identifier
            
        Returns:
            Generated request ID
        """
        request_id = self._generate_request_id()
        
        metrics = RequestMetrics(
            request_id=request_id,
            start_time=time.time(),
            user_id=user_id,
            session_id=session_id
        )
        
        with self.lock:
            self.active_requests[request_id] = metrics
            
            # Track user sessions
            if user_id:
                if user_id not in self.user_sessions:
                    self.user_sessions[user_id] = []
                self.user_sessions[user_id].append(request_id)
        
        # Set thread-local context
        self._set_current_request(request_id)
        
        logger.info(f"A8: Started request tracking - {request_id}")
        return request_id
    
    def end_request(self, request_id: str) -> Optional[RequestMetrics]:
        """
        End tracking for a request.
        
        Args:
            request_id: Request identifier
            
        Returns:
            Final metrics for the request
        """
        with self.lock:
            if request_id not in self.active_requests:
                logger.warning(f"A8: Attempted to end unknown request {request_id}")
                return None
            
            metrics = self.active_requests[request_id]
            metrics.end_time = time.time()
            metrics.total_duration_ms = (metrics.end_time - metrics.start_time) * 1000
            
            # Move to completed requests
            self.completed_requests.append(metrics)
            del self.active_requests[request_id]
        
        # Clear thread-local context
        self._clear_current_request()
        
        logger.info(f"A8: Ended request tracking - {request_id} ({metrics.total_duration_ms:.1f}ms)")
        return metrics
    
    def get_current_request_id(self) -> Optional[str]:
        """Get the current request ID from thread-local context."""
        return getattr(_request_context, 'request_id', None)
    
    def get_request_metrics(self, request_id: str) -> Optional[RequestMetrics]:
        """Get metrics for a specific request."""
        with self.lock:
            if request_id in self.active_requests:
                return self.active_requests[request_id]
            
            for metrics in self.completed_requests:
                if metrics.request_id == request_id:
                    return metrics
        
        return None
    
    def add_bullet_success(self, request_id: Optional[str] = None):
        """Record a successful bullet creation."""
        request_id = request_id or self.get_current_request_id()
        if not request_id:
            return
        
        with self.lock:
            if request_id in self.active_requests:
                metrics = self.active_requests[request_id]
                metrics.total_bullets += 1
                metrics.successful_bullets += 1
    
    def add_bullet_failure(self, error_message: str, request_id: Optional[str] = None):
        """Record a bullet creation failure."""
        request_id = request_id or self.get_current_request_id()
        if not request_id:
            return
        
        with self.lock:
            if request_id in self.active_requests:
                metrics = self.active_requests[request_id]
                metrics.total_bullets += 1
                metrics.failed_bullets += 1
                metrics.errors.append(error_message)
    
    def add_warning(self, warning_message: str, request_id: Optional[str] = None):
        """Record a warning for the request."""
        request_id = request_id or self.get_current_request_id()
        if not request_id:
            return
        
        with self.lock:
            if request_id in self.active_requests:
                metrics = self.active_requests[request_id]
                metrics.warnings.append(warning_message)
    
    def set_performance_metric(self, metric_name: str, value: float, 
                              request_id: Optional[str] = None):
        """Set a performance metric for the request."""
        request_id = request_id or self.get_current_request_id()
        if not request_id:
            return
        
        with self.lock:
            if request_id in self.active_requests:
                metrics = self.active_requests[request_id]
                
                if metric_name == 'build_duration_ms':
                    metrics.build_duration_ms = value
                elif metric_name == 'reconciliation_duration_ms':
                    metrics.reconciliation_duration_ms = value
                elif metric_name == 'document_size_bytes':
                    metrics.document_size_bytes = int(value)
    
    def set_metadata(self, key: str, value: Any, request_id: Optional[str] = None):
        """Set metadata for the request."""
        request_id = request_id or self.get_current_request_id()
        if not request_id:
            return
        
        with self.lock:
            if request_id in self.active_requests:
                metrics = self.active_requests[request_id]
                
                if key == 'template_used':
                    metrics.template_used = str(value)
                elif key.startswith('feature_'):
                    feature_name = key[8:]  # Remove 'feature_' prefix
                    metrics.features_enabled[feature_name] = bool(value)
    
    def add_debug_artifact(self, artifact_path: str, request_id: Optional[str] = None):
        """Add a debug artifact reference to the request."""
        request_id = request_id or self.get_current_request_id()
        if not request_id:
            return
        
        with self.lock:
            if request_id in self.active_requests:
                metrics = self.active_requests[request_id]
                metrics.debug_artifacts.append(artifact_path)
    
    def get_analytics_summary(self, lookback_hours: int = 24) -> Dict[str, Any]:
        """
        Get analytics summary for recent requests.
        
        Args:
            lookback_hours: How many hours back to analyze
            
        Returns:
            Analytics summary
        """
        cutoff_time = time.time() - (lookback_hours * 3600)
        
        with self.lock:
            recent_requests = [
                metrics for metrics in self.completed_requests
                if metrics.start_time >= cutoff_time
            ]
        
        if not recent_requests:
            return {"message": f"No requests in last {lookback_hours} hours"}
        
        # Calculate aggregated metrics
        total_requests = len(recent_requests)
        total_bullets = sum(r.total_bullets for r in recent_requests)
        successful_bullets = sum(r.successful_bullets for r in recent_requests)
        total_errors = sum(len(r.errors) for r in recent_requests)
        
        avg_duration = sum(r.total_duration_ms for r in recent_requests) / total_requests
        avg_build_time = sum(r.build_duration_ms for r in recent_requests) / total_requests
        avg_reconciliation_time = sum(r.reconciliation_duration_ms for r in recent_requests) / total_requests
        
        # Error patterns
        error_patterns = {}
        for req in recent_requests:
            for error in req.errors:
                error_key = error[:50]  # Truncate for grouping
                error_patterns[error_key] = error_patterns.get(error_key, 0) + 1
        
        # Feature usage
        feature_usage = {}
        for req in recent_requests:
            for feature, enabled in req.features_enabled.items():
                if feature not in feature_usage:
                    feature_usage[feature] = {"enabled": 0, "disabled": 0}
                if enabled:
                    feature_usage[feature]["enabled"] += 1
                else:
                    feature_usage[feature]["disabled"] += 1
        
        return {
            "period": f"Last {lookback_hours} hours",
            "summary": {
                "total_requests": total_requests,
                "total_bullets": total_bullets,
                "successful_bullets": successful_bullets,
                "bullet_success_rate": (successful_bullets / total_bullets * 100) if total_bullets > 0 else 0,
                "total_errors": total_errors,
                "error_rate": (total_errors / total_requests) if total_requests > 0 else 0
            },
            "performance": {
                "avg_total_duration_ms": avg_duration,
                "avg_build_duration_ms": avg_build_time,
                "avg_reconciliation_duration_ms": avg_reconciliation_time
            },
            "error_patterns": dict(sorted(error_patterns.items(), key=lambda x: x[1], reverse=True)[:10]),
            "feature_usage": feature_usage,
            "active_requests": len(self.active_requests)
        }
    
    def get_user_request_history(self, user_id: str, limit: int = 10) -> List[RequestMetrics]:
        """Get request history for a specific user."""
        with self.lock:
            if user_id not in self.user_sessions:
                return []
            
            user_request_ids = self.user_sessions[user_id][-limit:]  # Get last N requests
            user_requests = []
            
            for req_id in user_request_ids:
                metrics = self.get_request_metrics(req_id)
                if metrics:
                    user_requests.append(metrics)
            
            return user_requests
    
    def cleanup_old_requests(self, max_age_hours: int = 168):  # 1 week default
        """Clean up old completed requests to prevent memory growth."""
        cutoff_time = time.time() - (max_age_hours * 3600)
        
        with self.lock:
            old_count = len(self.completed_requests)
            self.completed_requests = [
                req for req in self.completed_requests
                if req.start_time >= cutoff_time
            ]
            cleaned_count = old_count - len(self.completed_requests)
            
            if cleaned_count > 0:
                logger.info(f"A8: Cleaned up {cleaned_count} old request records")
    
    def _generate_request_id(self) -> str:
        """Generate a unique request ID."""
        # Use timestamp + UUID for uniqueness and readability
        timestamp = int(time.time())
        short_uuid = str(uuid.uuid4())[:8]
        return f"req_{timestamp}_{short_uuid}"
    
    def _set_current_request(self, request_id: str):
        """Set the current request ID in thread-local storage."""
        _request_context.request_id = request_id
    
    def _clear_current_request(self):
        """Clear the current request ID from thread-local storage."""
        if hasattr(_request_context, 'request_id'):
            delattr(_request_context, 'request_id')


# Global singleton instance
correlation_manager = RequestCorrelationManager()


# Convenience functions for easy access
def start_request(user_id: Optional[str] = None, session_id: Optional[str] = None) -> str:
    """Start tracking a new request."""
    return correlation_manager.start_request(user_id, session_id)


def end_request(request_id: str) -> Optional[RequestMetrics]:
    """End tracking for a request."""
    return correlation_manager.end_request(request_id)


def get_current_request_id() -> Optional[str]:
    """Get the current request ID."""
    return correlation_manager.get_current_request_id()


def add_bullet_success(request_id: Optional[str] = None):
    """Record a successful bullet creation."""
    correlation_manager.add_bullet_success(request_id)


def add_bullet_failure(error_message: str, request_id: Optional[str] = None):
    """Record a bullet creation failure."""
    correlation_manager.add_bullet_failure(error_message, request_id)


def add_warning(warning_message: str, request_id: Optional[str] = None):
    """Record a warning."""
    correlation_manager.add_warning(warning_message, request_id)


def set_performance_metric(metric_name: str, value: float, request_id: Optional[str] = None):
    """Set a performance metric."""
    correlation_manager.set_performance_metric(metric_name, value, request_id)


def set_metadata(key: str, value: Any, request_id: Optional[str] = None):
    """Set metadata for the request."""
    correlation_manager.set_metadata(key, value, request_id)


def add_debug_artifact(artifact_path: str, request_id: Optional[str] = None):
    """Add a debug artifact reference."""
    correlation_manager.add_debug_artifact(artifact_path, request_id) 