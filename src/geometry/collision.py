"""
Fast Collision Detection for Nesting

Provides efficient collision checking for polygon placement:
- Bounding box pre-filtering (fast rejection)
- Exact polygon intersection (when needed)
- Spatial indexing for large part counts
- Optimized for nesting scenarios

Performance: O(n) with spatial index, O(n²) worst case
"""

from typing import List, Tuple, Optional, Set
from dataclasses import dataclass
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from geometry.polygon import Polygon, BoundingBox


@dataclass
class PlacedPart:
    """A part that has been placed on the sheet"""
    polygon: Polygon
    x: float
    y: float
    rotation: float
    
    def get_transformed_polygon(self) -> Polygon:
        """Get the polygon in its placed position"""
        # Rotate
        if self.rotation != 0:
            transformed = self.polygon.rotate(self.rotation)
        else:
            transformed = self.polygon
        
        # Translate
        transformed = transformed.translate(self.x, self.y)
        return transformed
    
    def get_bounds(self) -> BoundingBox:
        """Get bounding box of placed part"""
        transformed = self.get_transformed_polygon()
        return transformed.bounds


class SpatialIndex:
    """
    Simple spatial index using grid cells
    
    Divides sheet into grid cells and tracks which parts
    occupy which cells for fast collision pre-filtering
    """
    
    def __init__(self, width: float, height: float, cell_size: float = 100.0):
        """
        Initialize spatial index
        
        Args:
            width: Sheet width
            height: Sheet height
            cell_size: Size of grid cells (mm)
        """
        self.width = width
        self.height = height
        self.cell_size = cell_size
        
        self.cols = int(width / cell_size) + 1
        self.rows = int(height / cell_size) + 1
        
        # Grid: cell -> list of part indices
        self.grid = {}
    
    def _get_cells(self, bounds: BoundingBox) -> Set[Tuple[int, int]]:
        """Get all grid cells that overlap with bounds"""
        min_col = int(bounds.min_x / self.cell_size)
        max_col = int(bounds.max_x / self.cell_size)
        min_row = int(bounds.min_y / self.cell_size)
        max_row = int(bounds.max_y / self.cell_size)
        
        cells = set()
        for col in range(max(0, min_col), min(self.cols, max_col + 1)):
            for row in range(max(0, min_row), min(self.rows, max_row + 1)):
                cells.add((col, row))
        
        return cells
    
    def insert(self, part_idx: int, bounds: BoundingBox):
        """Insert a part into the spatial index"""
        cells = self._get_cells(bounds)
        for cell in cells:
            if cell not in self.grid:
                self.grid[cell] = []
            self.grid[cell].append(part_idx)
    
    def query(self, bounds: BoundingBox) -> Set[int]:
        """Query which parts might overlap with bounds"""
        cells = self._get_cells(bounds)
        candidates = set()
        
        for cell in cells:
            if cell in self.grid:
                candidates.update(self.grid[cell])
        
        return candidates


class CollisionDetector:
    """
    Fast collision detection for nesting
    
    Uses two-phase approach:
    1. Bounding box filtering (fast)
    2. Exact polygon intersection (only when needed)
    
    With spatial indexing for large part counts
    """
    
    def __init__(
        self,
        sheet_width: float,
        sheet_height: float,
        use_spatial_index: bool = True,
        min_spacing: float = 0.0
    ):
        """
        Initialize collision detector
        
        Args:
            sheet_width: Sheet width
            sheet_height: Sheet height
            use_spatial_index: Use spatial indexing (recommended for >50 parts)
            min_spacing: Minimum spacing between parts (kerf + min_web)
        """
        self.sheet_width = sheet_width
        self.sheet_height = sheet_height
        self.min_spacing = min_spacing
        self.use_spatial_index = use_spatial_index
        
        # Placed parts
        self.placed_parts: List[PlacedPart] = []
        
        # Spatial index
        if use_spatial_index:
            self.spatial_index = SpatialIndex(sheet_width, sheet_height, cell_size=100.0)
        else:
            self.spatial_index = None
    
    def add_part(self, polygon: Polygon, x: float, y: float, rotation: float = 0) -> bool:
        """
        Try to add a part at the given position
        
        Returns True if placement is valid (no collision), False otherwise
        """
        # Create placed part
        part = PlacedPart(polygon, x, y, rotation)
        
        # Check collision
        if not self.check_placement(part):
            return False
        
        # Add to placed parts
        part_idx = len(self.placed_parts)
        self.placed_parts.append(part)
        
        # Update spatial index
        if self.spatial_index:
            bounds = part.get_bounds()
            self.spatial_index.insert(part_idx, bounds)
        
        return True
    
    def check_placement(self, part: PlacedPart) -> bool:
        """
        Check if a placement is valid (no collisions)
        
        Args:
            part: Placed part to check
        
        Returns:
            True if valid, False if collision detected
        """
        # Get transformed polygon
        transformed = part.get_transformed_polygon()
        bounds = transformed.bounds
        
        # Check sheet bounds
        if not self._check_sheet_bounds(bounds):
            return False
        
        # Check collisions with other parts
        if not self._check_part_collisions(transformed, bounds):
            return False
        
        return True
    
    def _check_sheet_bounds(self, bounds: BoundingBox) -> bool:
        """Check if part is within sheet bounds"""
        if bounds.min_x < 0 or bounds.min_y < 0:
            return False
        if bounds.max_x > self.sheet_width or bounds.max_y > self.sheet_height:
            return False
        return True
    
    def _check_part_collisions(self, polygon: Polygon, bounds: BoundingBox) -> bool:
        """
        Check collisions with already placed parts
        
        Returns True if no collision, False if collision
        """
        # Get candidate parts using spatial index
        if self.spatial_index:
            candidate_indices = self.spatial_index.query(bounds)
        else:
            # Check all parts
            candidate_indices = range(len(self.placed_parts))
        
        # Check each candidate
        for idx in candidate_indices:
            other = self.placed_parts[idx]
            other_bounds = other.get_bounds()
            
            # Quick bbox check with spacing
            if not self._bbox_overlap(bounds, other_bounds, self.min_spacing):
                continue  # No bbox overlap, skip expensive check
            
            # Exact polygon intersection check
            other_polygon = other.get_transformed_polygon()
            
            # Add spacing buffer if needed
            if self.min_spacing > 0:
                # Buffer both polygons
                buffered = polygon.buffer(self.min_spacing / 2)
                other_buffered = other_polygon.buffer(self.min_spacing / 2)
                
                if buffered.intersects(other_buffered):
                    return False  # Collision!
            else:
                if polygon.intersects(other_polygon):
                    return False  # Collision!
        
        return True  # No collision
    
    def _bbox_overlap(
        self,
        bbox1: BoundingBox,
        bbox2: BoundingBox,
        spacing: float = 0
    ) -> bool:
        """Check if two bounding boxes overlap (with spacing)"""
        # Add spacing to bbox1
        min_x1 = bbox1.min_x - spacing
        max_x1 = bbox1.max_x + spacing
        min_y1 = bbox1.min_y - spacing
        max_y1 = bbox1.max_y + spacing
        
        # Check overlap
        if max_x1 < bbox2.min_x or min_x1 > bbox2.max_x:
            return False
        if max_y1 < bbox2.min_y or min_y1 > bbox2.max_y:
            return False
        
        return True
    
    def clear(self):
        """Clear all placed parts"""
        self.placed_parts = []
        if self.spatial_index:
            self.spatial_index = SpatialIndex(
                self.sheet_width,
                self.sheet_height,
                cell_size=100.0
            )
    
    def get_placed_count(self) -> int:
        """Get number of placed parts"""
        return len(self.placed_parts)
    
    def get_utilization(self) -> float:
        """Compute current utilization percentage"""
        if not self.placed_parts:
            return 0.0
        
        total_area = sum(part.polygon.area for part in self.placed_parts)
        sheet_area = self.sheet_width * self.sheet_height
        return (total_area / sheet_area) * 100


# Convenience functions
def check_collision(
    polygon: Polygon,
    x: float,
    y: float,
    rotation: float,
    placed_parts: List[PlacedPart],
    sheet_width: float,
    sheet_height: float,
    min_spacing: float = 0
) -> bool:
    """
    Quick collision check for a single placement
    
    Returns True if valid (no collision), False if collision
    """
    detector = CollisionDetector(sheet_width, sheet_height, use_spatial_index=False, min_spacing=min_spacing)
    detector.placed_parts = placed_parts
    
    part = PlacedPart(polygon, x, y, rotation)
    return detector.check_placement(part)

