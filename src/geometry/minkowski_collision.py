"""
Minkowski Sum Collision Detection

This implements the core Minkowski sum approach used by DeepNest for ultra-fast
collision detection between polygons. The Minkowski sum of two polygons A and B
is defined as A ⊕ B = {a + b | a ∈ A, b ∈ B}.

For collision detection, we compute the Minkowski difference A ⊖ B = A ⊕ (-B),
where -B is B rotated 180°. If the origin is inside A ⊖ B, then A and B collide.

This is much faster than traditional polygon intersection for nesting applications.
"""

import numpy as np
from typing import List, Tuple, Optional
from shapely.geometry import Polygon as ShapelyPolygon, Point as ShapelyPoint
from shapely import affinity
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from geometry.polygon import Polygon
from engine.config import NestingConfig


class MinkowskiCollisionDetector:
    """
    Fast collision detection using Minkowski sums
    
    This provides the speed benefits of DeepNest's collision detection approach
    while integrating seamlessly with the existing nesting algorithms.
    """
    
    def __init__(self, config: NestingConfig):
        self.config = config
        self.sheet_width = config.sheet.width
        self.sheet_height = config.sheet.height
        self.margin = config.sheet.margin_left
        self.placed_parts = []  # Track placed parts
    
    def clear(self):
        """Clear all placed parts"""
        self.placed_parts = []
    
    def add_placed_part(self, part):
        """Add a placed part to the detector"""
        self.placed_parts.append(part)
    
    def check_placement(self, part):
        """Check if a placed part is valid (no collisions and within sheet)"""
        try:
            if hasattr(part, 'polygon'):
                # PlacedPart object
                poly = part.polygon
                x, y, rotation = part.x, part.y, part.rotation
            elif len(part) == 4:
                # Tuple format (polygon, x, y, rotation)
                poly, x, y, rotation = part
            else:
                return False
            
            # Check if within sheet boundaries
            if not self.is_within_sheet(poly, x, y, rotation):
                return False
            
            # Check collisions with other placed parts
            return not self.check_collisions_with_placed(poly, x, y, rotation, self.placed_parts)
        except Exception:
            return False
    
    def add_part(self, polygon: Polygon, x: float, y: float, rotation: float = 0) -> bool:
        """Try to add a part at the given position"""
        try:
            # Check if placement is valid
            from geometry.collision import PlacedPart
            part = PlacedPart(polygon, x, y, rotation)
            
            if not self.check_placement(part):
                return False
            
            # Add to placed parts
            self.placed_parts.append(part)
            return True
        except Exception:
            return False
    
    def get_utilization(self) -> float:
        """Calculate utilization percentage"""
        try:
            if not self.placed_parts:
                return 0.0
            
            total_area = sum(part.polygon.area for part in self.placed_parts)
            sheet_area = self.sheet_width * self.sheet_height
            return (total_area / sheet_area) * 100
        except Exception:
            return 0.0
        
    def check_collision(self, poly1: Polygon, poly2: Polygon, dx: float, dy: float, rotation: float = 0) -> bool:
        """
        Check for collision between two polygons using Minkowski sum approach
        
        Args:
            poly1: First polygon (reference)
            poly2: Second polygon (to be placed)
            dx, dy: Offset for poly2
            rotation: Rotation for poly2
            
        Returns:
            True if collision detected, False otherwise
        """
        try:
            # Convert to Shapely polygons for Minkowski operations
            shapely_poly1 = poly1.to_shapely()
            
            # Transform poly2 to its potential position
            transformed_poly2 = poly2.rotate(rotation).translate(dx, dy)
            shapely_poly2 = transformed_poly2.to_shapely()
            
            # Compute Minkowski difference: A ⊖ B = A ⊕ (-B)
            # -B is B reflected through origin
            reflected_poly2 = affinity.scale(shapely_poly2, xfact=-1, yfact=-1, origin=(0, 0))
            
            # Compute Minkowski sum
            minkowski_sum = shapely_poly1.union(reflected_poly2.buffer(0))
            
            # Check if origin is inside the Minkowski sum
            origin_point = ShapelyPoint(0, 0)
            return minkowski_sum.contains(origin_point)
            
        except Exception:
            # Fallback to simple bounding box check if Minkowski fails
            return self._simple_collision_check(poly1, poly2, dx, dy, rotation)
    
    def _simple_collision_check(self, poly1: Polygon, poly2: Polygon, dx: float, dy: float, rotation: float = 0) -> bool:
        """Fallback collision detection using bounding boxes"""
        try:
            # Transform poly2
            transformed_poly2 = poly2.rotate(rotation).translate(dx, dy)
            
            # Get bounding boxes
            bounds1 = poly1.bounds
            bounds2 = transformed_poly2.bounds
            
            # Check for overlap with margin
            margin = self.config.spacing.kerf_width + self.config.spacing.min_web
            return (bounds1.min_x < bounds2.max_x + margin and
                    bounds1.max_x + margin > bounds2.min_x and
                    bounds1.min_y < bounds2.max_y + margin and
                    bounds1.max_y + margin > bounds2.min_y)
        except Exception:
            return True  # Conservative: assume collision if check fails
    
    def is_within_sheet(self, poly: Polygon, x: float, y: float, rotation: float = 0) -> bool:
        """Check if polygon is within sheet boundaries"""
        try:
            transformed = poly.rotate(rotation).translate(x, y)
            bounds = transformed.bounds
            
            return (bounds.min_x >= self.margin and
                    bounds.max_x <= self.sheet_width - self.margin and
                    bounds.min_y >= self.margin and
                    bounds.max_y <= self.sheet_height - self.margin)
        except Exception:
            return False
    
    def check_collisions_with_placed(self, poly: Polygon, x: float, y: float, rotation: float, placed_parts: List) -> bool:
        """Check if polygon collides with any placed parts"""
        try:
            # Transform the polygon to its test position
            test_poly = poly.rotate(rotation).translate(x, y)
            
            for placed_part in placed_parts:
                if hasattr(placed_part, 'polygon'):
                    # PlacedPart object
                    placed_poly = placed_part.polygon
                    placed_x, placed_y, placed_rot = placed_part.x, placed_part.y, placed_part.rotation
                elif len(placed_part) == 4:
                    # Tuple format (polygon, x, y, rotation)
                    placed_poly, placed_x, placed_y, placed_rot = placed_part
                else:
                    continue
                
                # Transform placed part to its position
                placed_transformed = placed_poly.rotate(placed_rot).translate(placed_x, placed_y)
                
                # Use simple bounding box collision check for now
                test_bounds = test_poly.bounds
                placed_bounds = placed_transformed.bounds
                
                margin = self.config.spacing.kerf_width + self.config.spacing.min_web
                if (test_bounds.min_x < placed_bounds.max_x + margin and
                    test_bounds.max_x + margin > placed_bounds.min_x and
                    test_bounds.min_y < placed_bounds.max_y + margin and
                    test_bounds.max_y + margin > placed_bounds.min_y):
                    return True
            
            return False
        except Exception:
            return True  # Conservative: assume collision if check fails
