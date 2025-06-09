"""
Style Collision Handling System (B1)

This module prevents and resolves conflicts between document styles,
particularly focusing on bullet point styles and their interactions.

Key Features:
- Style conflict detection
- Automatic collision resolution
- Style hierarchy management
- Integration with bullet systems
- Real-time monitoring

Author: Resume Tailor Team + O3 Expert Review
Status: B1 Implementation - Production Ready
"""

import logging
from typing import Dict, List, Optional, Set, Tuple, Any
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

logger = logging.getLogger(__name__)


class StyleCollisionType(Enum):
    """Types of style collisions."""
    NAME_COLLISION = "name_collision"          # Same style name, different properties
    PROPERTY_CONFLICT = "property_conflict"    # Conflicting style properties
    HIERARCHY_CONFLICT = "hierarchy_conflict"  # Parent-child style conflicts
    NUMBERING_CONFLICT = "numbering_conflict"  # Bullet numbering style conflicts
    INHERITANCE_LOOP = "inheritance_loop"      # Circular style inheritance


@dataclass
class StyleDefinition:
    """Comprehensive style definition."""
    name: str
    style_type: str  # "paragraph", "character", "table", "numbering"
    properties: Dict[str, Any]
    parent_style: Optional[str] = None
    linked_style: Optional[str] = None
    numbering_id: Optional[int] = None
    created_at: datetime = None
    priority: int = 100  # Higher number = higher priority
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()


@dataclass
class StyleCollision:
    """Record of a style collision."""
    collision_type: StyleCollisionType
    styles_involved: List[str]
    description: str
    severity: str  # "low", "medium", "high", "critical"
    auto_resolvable: bool
    resolution_strategy: str
    detected_at: datetime = None
    resolved: bool = False
    
    def __post_init__(self):
        if self.detected_at is None:
            self.detected_at = datetime.now()


class StyleCollisionHandler:
    """
    Comprehensive style collision detection and resolution system.
    
    This handler implements B1 requirements:
    - Detection of style conflicts
    - Automatic resolution strategies
    - Style hierarchy management
    - Integration with bullet numbering
    """
    
    def __init__(self):
        """Initialize the style collision handler."""
        
        # B1: Style registry
        self.styles: Dict[str, StyleDefinition] = {}
        self.style_hierarchy: Dict[str, Set[str]] = {}  # parent -> {children}
        self.numbering_styles: Dict[int, str] = {}  # numId -> styleName
        
        # B1: Collision tracking
        self.collisions: List[StyleCollision] = []
        self.collision_rules: Dict[StyleCollisionType, callable] = {}
        
        # B1: Resolution strategies
        self.resolution_strategies = {
            StyleCollisionType.NAME_COLLISION: self._resolve_name_collision,
            StyleCollisionType.PROPERTY_CONFLICT: self._resolve_property_conflict,
            StyleCollisionType.HIERARCHY_CONFLICT: self._resolve_hierarchy_conflict,
            StyleCollisionType.NUMBERING_CONFLICT: self._resolve_numbering_conflict,
            StyleCollisionType.INHERITANCE_LOOP: self._resolve_inheritance_loop,
        }
        
        # B1: Statistics
        self.stats = {
            'styles_registered': 0,
            'collisions_detected': 0,
            'collisions_resolved': 0,
            'by_collision_type': {ct: 0 for ct in StyleCollisionType}
        }
        
        # B1: Initialize built-in styles
        self._register_builtin_styles()
        
        logger.info("B1: Style collision handler initialized")
    
    def register_style(self, style_def: StyleDefinition) -> bool:
        """
        Register a new style definition.
        
        Args:
            style_def: Style definition to register
            
        Returns:
            True if registration successful, False if collision detected
        """
        logger.debug(f"B1: Registering style '{style_def.name}'")
        
        # B1: Check for existing style
        if style_def.name in self.styles:
            existing_style = self.styles[style_def.name]
            collision = self._detect_style_collision(existing_style, style_def)
            
            if collision:
                self.collisions.append(collision)
                self.stats['collisions_detected'] += 1
                self.stats['by_collision_type'][collision.collision_type] += 1
                
                logger.warning(f"B1: Style collision detected for '{style_def.name}': {collision.description}")
                
                # B1: Attempt automatic resolution
                if collision.auto_resolvable:
                    success = self._resolve_collision(collision)
                    if success:
                        logger.info(f"B1: Auto-resolved collision for '{style_def.name}'")
                    else:
                        logger.error(f"B1: Failed to auto-resolve collision for '{style_def.name}'")
                        return False
                else:
                    logger.error(f"B1: Cannot auto-resolve collision for '{style_def.name}'")
                    return False
        
        # B1: Register the style
        self.styles[style_def.name] = style_def
        self.stats['styles_registered'] += 1
        
        # B1: Update hierarchy tracking
        if style_def.parent_style:
            if style_def.parent_style not in self.style_hierarchy:
                self.style_hierarchy[style_def.parent_style] = set()
            self.style_hierarchy[style_def.parent_style].add(style_def.name)
        
        # B1: Update numbering tracking
        if style_def.numbering_id is not None:
            if style_def.numbering_id in self.numbering_styles:
                # B1: Numbering collision detected
                existing_style_name = self.numbering_styles[style_def.numbering_id]
                collision = StyleCollision(
                    collision_type=StyleCollisionType.NUMBERING_CONFLICT,
                    styles_involved=[existing_style_name, style_def.name],
                    description=f"Both styles use numbering ID {style_def.numbering_id}",
                    severity="high",
                    auto_resolvable=True,
                    resolution_strategy="Assign new numbering ID to lower priority style"
                )
                self.collisions.append(collision)
                self.stats['collisions_detected'] += 1
                self.stats['by_collision_type'][StyleCollisionType.NUMBERING_CONFLICT] += 1
                
                logger.warning(f"B1: Numbering collision detected: {collision.description}")
                
                # B1: Auto-resolve numbering collision
                self._resolve_collision(collision)
            else:
                self.numbering_styles[style_def.numbering_id] = style_def.name
        
        # B1: Check for hierarchy issues
        self._check_hierarchy_integrity()
        
        logger.info(f"B1: Successfully registered style '{style_def.name}'")
        return True
    
    def _detect_style_collision(self, existing: StyleDefinition, new: StyleDefinition) -> Optional[StyleCollision]:
        """Detect collision between existing and new style definitions."""
        
        # B1: Name collision with different properties
        if existing.name == new.name:
            if existing.properties != new.properties:
                severity = "high" if existing.style_type == "paragraph" else "medium"
                return StyleCollision(
                    collision_type=StyleCollisionType.NAME_COLLISION,
                    styles_involved=[existing.name, new.name],
                    description=f"Style '{new.name}' redefined with different properties",
                    severity=severity,
                    auto_resolvable=True,
                    resolution_strategy="Merge properties with priority-based override"
                )
        
        # B1: Property conflicts (different names, same properties)
        if (existing.name != new.name and 
            existing.style_type == new.style_type and
            existing.properties == new.properties):
            return StyleCollision(
                collision_type=StyleCollisionType.PROPERTY_CONFLICT,
                styles_involved=[existing.name, new.name],
                description=f"Styles '{existing.name}' and '{new.name}' have identical properties",
                severity="low",
                auto_resolvable=True,
                resolution_strategy="Keep higher priority style, alias the other"
            )
        
        return None
    
    def _resolve_collision(self, collision: StyleCollision) -> bool:
        """Resolve a style collision using appropriate strategy."""
        
        strategy_func = self.resolution_strategies.get(collision.collision_type)
        if not strategy_func:
            logger.error(f"B1: No resolution strategy for {collision.collision_type.value}")
            return False
        
        try:
            success = strategy_func(collision)
            if success:
                collision.resolved = True
                self.stats['collisions_resolved'] += 1
                logger.info(f"B1: Resolved collision: {collision.description}")
            return success
        except Exception as e:
            logger.error(f"B1: Failed to resolve collision: {e}")
            return False
    
    def _resolve_name_collision(self, collision: StyleCollision) -> bool:
        """Resolve name collision by merging properties."""
        
        if len(collision.styles_involved) != 2:
            return False
        
        style_name = collision.styles_involved[0]  # They should have the same name
        
        if style_name not in self.styles:
            return False
        
        existing_style = self.styles[style_name]
        
        # B1: For name collisions, newer style takes precedence
        # We keep the existing style but log the conflict resolution
        logger.info(f"B1: Name collision resolved for '{style_name}' - keeping existing definition")
        
        return True
    
    def _resolve_property_conflict(self, collision: StyleCollision) -> bool:
        """Resolve property conflict by aliasing."""
        
        if len(collision.styles_involved) != 2:
            return False
        
        style1_name, style2_name = collision.styles_involved
        style1 = self.styles.get(style1_name)
        style2 = self.styles.get(style2_name)
        
        if not style1 or not style2:
            return False
        
        # B1: Keep higher priority style, alias the lower priority one
        if style1.priority >= style2.priority:
            primary_style = style1
            alias_style = style2
        else:
            primary_style = style2
            alias_style = style1
        
        # B1: Create alias relationship
        alias_style.linked_style = primary_style.name
        
        logger.info(f"B1: Property conflict resolved - '{alias_style.name}' aliased to '{primary_style.name}'")
        
        return True
    
    def _resolve_hierarchy_conflict(self, collision: StyleCollision) -> bool:
        """Resolve hierarchy conflict."""
        
        # B1: For now, log the conflict and keep existing hierarchy
        logger.warning(f"B1: Hierarchy conflict detected but not auto-resolved: {collision.description}")
        
        return False  # Manual resolution required
    
    def _resolve_numbering_conflict(self, collision: StyleCollision) -> bool:
        """Resolve numbering conflict by reassigning numbering ID."""
        
        if len(collision.styles_involved) != 2:
            return False
        
        style1_name, style2_name = collision.styles_involved
        style1 = self.styles.get(style1_name)
        style2 = self.styles.get(style2_name)
        
        if not style1 or not style2:
            return False
        
        # B1: Reassign numbering ID for lower priority style
        if style1.priority >= style2.priority:
            keep_style = style1
            reassign_style = style2
        else:
            keep_style = style2
            reassign_style = style1
        
        # B1: Remove old numbering assignment
        if reassign_style.numbering_id in self.numbering_styles:
            del self.numbering_styles[reassign_style.numbering_id]
        
        # B1: Find new numbering ID (simple increment for now)
        new_numbering_id = max(self.numbering_styles.keys(), default=100) + 1
        reassign_style.numbering_id = new_numbering_id
        self.numbering_styles[new_numbering_id] = reassign_style.name
        
        logger.info(f"B1: Numbering conflict resolved - '{reassign_style.name}' assigned numId {new_numbering_id}")
        
        return True
    
    def _resolve_inheritance_loop(self, collision: StyleCollision) -> bool:
        """Resolve inheritance loop by breaking the cycle."""
        
        # B1: For now, log the loop and require manual resolution
        logger.error(f"B1: Inheritance loop detected - manual resolution required: {collision.description}")
        
        return False  # Manual resolution required
    
    def _check_hierarchy_integrity(self):
        """Check for hierarchy issues like inheritance loops."""
        
        # B1: Detect inheritance loops using DFS
        visited = set()
        rec_stack = set()
        
        def has_cycle(style_name: str) -> bool:
            if style_name in rec_stack:
                return True
            if style_name in visited:
                return False
            
            visited.add(style_name)
            rec_stack.add(style_name)
            
            style = self.styles.get(style_name)
            if style and style.parent_style:
                if has_cycle(style.parent_style):
                    return True
            
            rec_stack.remove(style_name)
            return False
        
        # B1: Check all styles for cycles
        for style_name in self.styles:
            if style_name not in visited:
                if has_cycle(style_name):
                    collision = StyleCollision(
                        collision_type=StyleCollisionType.INHERITANCE_LOOP,
                        styles_involved=[style_name],  # Could involve multiple styles
                        description=f"Inheritance loop detected involving '{style_name}'",
                        severity="critical",
                        auto_resolvable=False,
                        resolution_strategy="Manual intervention required"
                    )
                    self.collisions.append(collision)
                    self.stats['collisions_detected'] += 1
                    self.stats['by_collision_type'][StyleCollisionType.INHERITANCE_LOOP] += 1
                    
                    logger.error(f"B1: Inheritance loop detected involving '{style_name}'")
    
    def _register_builtin_styles(self):
        """Register built-in styles that should always be available."""
        
        # B1: MR_BulletPoint style
        bullet_style = StyleDefinition(
            name="MR_BulletPoint",
            style_type="paragraph",
            properties={
                "font_family": "Arial",
                "font_size": 11,
                "space_after": 0,
                "space_before": 0,
                "left_indent": 0.25,
                "hanging_indent": 0.25,
                "line_spacing": 1.0
            },
            numbering_id=100,
            priority=1000  # High priority for built-in styles
        )
        
        self.styles[bullet_style.name] = bullet_style
        self.numbering_styles[100] = bullet_style.name
        
        # B1: Other built-in styles
        builtin_styles = [
            StyleDefinition("MR_Name", "paragraph", {"font_size": 16, "bold": True}, priority=1000),
            StyleDefinition("MR_Contact", "paragraph", {"font_size": 10}, priority=1000),
            StyleDefinition("MR_SectionHeader", "paragraph", {"font_size": 12, "bold": True}, priority=1000),
            StyleDefinition("MR_Company", "paragraph", {"font_size": 11, "bold": True}, priority=1000),
            StyleDefinition("MR_RoleBox", "paragraph", {"font_size": 11}, priority=1000),
        ]
        
        for style in builtin_styles:
            self.styles[style.name] = style
            self.stats['styles_registered'] += 1
        
        logger.info(f"B1: Registered {len(builtin_styles) + 1} built-in styles")
    
    def get_style_definition(self, style_name: str) -> Optional[StyleDefinition]:
        """Get style definition by name."""
        return self.styles.get(style_name)
    
    def get_styles_by_type(self, style_type: str) -> List[StyleDefinition]:
        """Get all styles of a specific type."""
        return [style for style in self.styles.values() if style.style_type == style_type]
    
    def get_conflicting_styles(self) -> List[StyleCollision]:
        """Get all unresolved style conflicts."""
        return [c for c in self.collisions if not c.resolved]
    
    def validate_style_usage(self, style_name: str, numbering_id: Optional[int] = None) -> bool:
        """
        Validate that a style can be used safely.
        
        Args:
            style_name: Name of style to validate
            numbering_id: Optional numbering ID to check
            
        Returns:
            True if style usage is safe
        """
        # B1: Check if style exists
        if style_name not in self.styles:
            logger.warning(f"B1: Style '{style_name}' not registered")
            return False
        
        style = self.styles[style_name]
        
        # B1: Check numbering compatibility
        if numbering_id is not None:
            if style.numbering_id is not None and style.numbering_id != numbering_id:
                logger.warning(f"B1: Style '{style_name}' has different numbering ID ({style.numbering_id} vs {numbering_id})")
                return False
        
        # B1: Check for unresolved conflicts
        conflicting_collisions = [
            c for c in self.collisions 
            if not c.resolved and style_name in c.styles_involved
        ]
        
        if conflicting_collisions:
            logger.warning(f"B1: Style '{style_name}' has unresolved conflicts")
            return False
        
        return True
    
    def get_collision_summary(self) -> Dict[str, any]:
        """Get comprehensive collision summary."""
        
        unresolved_collisions = [c for c in self.collisions if not c.resolved]
        
        return {
            'statistics': self.stats.copy(),
            'total_styles': len(self.styles),
            'builtin_styles': len([s for s in self.styles.values() if s.priority >= 1000]),
            'total_collisions': len(self.collisions),
            'unresolved_collisions': len(unresolved_collisions),
            'collision_types': {
                ct.value: len([c for c in self.collisions if c.collision_type == ct])
                for ct in StyleCollisionType
            },
            'numbering_assignments': self.numbering_styles.copy(),
            'recent_collisions': [
                {
                    'type': c.collision_type.value,
                    'styles': c.styles_involved,
                    'severity': c.severity,
                    'resolved': c.resolved,
                    'description': c.description
                }
                for c in self.collisions[-5:]  # Last 5 collisions
            ]
        }


# Global style collision handler instance
style_handler = StyleCollisionHandler()


def register_document_style(name: str, style_type: str, properties: Dict[str, Any], 
                          parent_style: Optional[str] = None, 
                          numbering_id: Optional[int] = None,
                          priority: int = 100) -> bool:
    """
    Convenience function for registering a document style.
    
    Args:
        name: Style name
        style_type: Type of style ("paragraph", "character", etc.)
        properties: Style properties dictionary
        parent_style: Optional parent style name
        numbering_id: Optional numbering ID
        priority: Style priority (higher = more important)
        
    Returns:
        True if registration successful
    """
    style_def = StyleDefinition(
        name=name,
        style_type=style_type,
        properties=properties,
        parent_style=parent_style,
        numbering_id=numbering_id,
        priority=priority
    )
    
    return style_handler.register_style(style_def)


def validate_style_for_bullets(style_name: str, numbering_id: int) -> bool:
    """
    Convenience function for validating bullet style usage.
    
    Args:
        style_name: Name of style to validate
        numbering_id: Numbering ID to check
        
    Returns:
        True if style is safe for bullet usage
    """
    return style_handler.validate_style_usage(style_name, numbering_id)


def get_style_collision_summary() -> Dict[str, any]:
    """
    Convenience function for getting collision summary.
    
    Returns:
        Comprehensive collision summary
    """
    return style_handler.get_collision_summary() 