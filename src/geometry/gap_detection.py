"""
Gap Detection for Nesting Optimization

Identifies empty spaces on the sheet where additional parts could fit.
This enables gap-filling strategies to improve utilization.

Algorithm:
1. Grid-based sampling of sheet
2. Check which grid points are empty
3. Cluster empty points into rectangular regions
4. Return gaps sorted by size and position

Expected improvement: +2-5% utilization
"""

from typing import List, Tuple, Set
from dataclasses import dataclass
import numpy as np

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from geometry.polygon import Polygon, BoundingBox
from geometry.collision import PlacedPart


@dataclass
class Gap:
    """Represents an empty rectangular region on the sheet"""
    x: float  # Bottom-left X
    y: float  # Bottom-left Y
    width: float
    height: float
    area: float
    
    def to_bbox(self) -> BoundingBox:
        """Convert to bounding box"""
        return BoundingBox(
            min_x=self.x,
            min_y=self.y,
            max_x=self.x + self.width,
            max_y=self.y + self.height
        )
    
    def can_fit(self, part_width: float, part_height: float) -> bool:
        """Check if a part of given size could fit in this gap"""
        return (self.width >= part_width and self.height >= part_height) or \
               (self.width >= part_height and self.height >= part_width)  # Try rotated
    
    def __repr__(self):
        return f"Gap({self.x:.0f},{self.y:.0f}, {self.width:.0f}x{self.height:.0f}, {self.area:.0f}mm²)"


class GapDetector:
    """
    Detect empty gaps on the sheet
    
    Uses grid-based sampling to find empty regions
    """
    
    def __init__(
        self,
        sheet_width: float,
        sheet_height: float,
        grid_size: float = 20.0,  # mm, size of sampling grid
        min_gap_size: float = 30.0  # mm, minimum gap size to report
    ):
        """
        Initialize gap detector
        
        Args:
            sheet_width: Sheet width
            sheet_height: Sheet height
            grid_size: Grid cell size for sampling
            min_gap_size: Minimum gap dimension to report
        """
        self.sheet_width = sheet_width
        self.sheet_height = sheet_height
        self.grid_size = grid_size
        self.min_gap_size = min_gap_size
        
        # Grid dimensions
        self.cols = int(sheet_width / grid_size) + 1
        self.rows = int(sheet_height / grid_size) + 1
    
    def detect_gaps(
        self,
        placed_parts: List[PlacedPart],
        margin_left: float = 0,
        margin_right: float = 0,
        margin_top: float = 0,
        margin_bottom: float = 0
    ) -> List[Gap]:
        """
        Detect gaps (empty regions) on the sheet
        
        Args:
            placed_parts: Parts already placed
            margin_*: Sheet margins to respect
        
        Returns:
            List of Gap objects, sorted by area (largest first)
        """
        # Create occupancy grid
        occupied = self._create_occupancy_grid(placed_parts)
        
        # Find empty rectangular regions
        gaps = self._find_rectangular_gaps(
            occupied,
            margin_left,
            margin_right,
            margin_top,
            margin_bottom
        )
        
        # Filter by minimum size
        gaps = [g for g in gaps if g.width >= self.min_gap_size and g.height >= self.min_gap_size]
        
        # Sort by area (largest first)
        gaps.sort(key=lambda g: g.area, reverse=True)
        
        return gaps
    
    def _create_occupancy_grid(self, placed_parts: List[PlacedPart]) -> np.ndarray:
        """
        Create binary occupancy grid
        
        Returns: 2D array where True = occupied, False = empty
        """
        grid = np.zeros((self.rows, self.cols), dtype=bool)
        
        # Mark occupied cells
        for part in placed_parts:
            bounds = part.get_bounds()
            
            # Find grid cells overlapping with this part
            min_col = int(bounds.min_x / self.grid_size)
            max_col = int(bounds.max_x / self.grid_size)
            min_row = int(bounds.min_y / self.grid_size)
            max_row = int(bounds.max_y / self.grid_size)
            
            # Mark as occupied (exact bounds, no buffer for gap detection)
            for row in range(max(0, min_row), min(self.rows, max_row + 1)):
                for col in range(max(0, min_col), min(self.cols, max_col + 1)):
                    grid[row, col] = True
        
        return grid
    
    def _find_rectangular_gaps(
        self,
        occupied: np.ndarray,
        margin_left: float,
        margin_right: float,
        margin_top: float,
        margin_bottom: float
    ) -> List[Gap]:
        """
        Find rectangular gaps in occupancy grid
        
        Uses greedy algorithm to find maximal rectangles
        """
        gaps = []
        visited = np.zeros_like(occupied, dtype=bool)
        
        # Scan grid for empty cells
        for row in range(self.rows):
            for col in range(self.cols):
                if not occupied[row, col] and not visited[row, col]:
                    # Found empty cell - try to grow a rectangle
                    gap = self._grow_rectangle(occupied, visited, row, col)
                    
                    if gap:
                        # Convert grid coordinates to mm
                        x = gap[1] * self.grid_size
                        y = gap[0] * self.grid_size
                        width = gap[3] * self.grid_size
                        height = gap[2] * self.grid_size
                        
                        # Check if in valid region (not in margins)
                        if (x >= margin_left and
                            x + width <= self.sheet_width - margin_right and
                            y >= margin_bottom and
                            y + height <= self.sheet_height - margin_top):
                            
                            gap_obj = Gap(
                                x=x,
                                y=y,
                                width=width,
                                height=height,
                                area=width * height
                            )
                            gaps.append(gap_obj)
        
        return gaps
    
    def _grow_rectangle(
        self,
        occupied: np.ndarray,
        visited: np.ndarray,
        start_row: int,
        start_col: int
    ) -> Tuple[int, int, int, int]:
        """
        Grow a maximal rectangle from starting point
        
        Returns: (row, col, height, width) in grid cells, or None
        """
        # Find maximum width for first row
        max_width = 0
        for col in range(start_col, self.cols):
            if occupied[start_row, col]:
                break
            max_width += 1
        
        if max_width == 0:
            return None
        
        # Grow downward while maintaining width
        height = 1
        for row in range(start_row + 1, self.rows):
            # Check if this row can extend the rectangle
            can_extend = True
            for col in range(start_col, start_col + max_width):
                if col >= self.cols or occupied[row, col]:
                    can_extend = False
                    break
            
            if can_extend:
                height += 1
            else:
                break
        
        # Mark as visited
        for row in range(start_row, start_row + height):
            for col in range(start_col, start_col + max_width):
                if row < self.rows and col < self.cols:
                    visited[row, col] = True
        
        return (start_row, start_col, height, max_width)


def detect_gaps(
    placed_parts: List[PlacedPart],
    sheet_width: float,
    sheet_height: float,
    margin_left: float = 0,
    margin_right: float = 0,
    margin_top: float = 0,
    margin_bottom: float = 0,
    grid_size: float = 20.0,
    min_gap_size: float = 30.0
) -> List[Gap]:
    """
    Convenience function to detect gaps
    
    Example:
        gaps = detect_gaps(placed_parts, 1220, 2440)
        print(f"Found {len(gaps)} gaps")
        for gap in gaps[:5]:
            print(f"  {gap}")
    """
    detector = GapDetector(sheet_width, sheet_height, grid_size, min_gap_size)
    return detector.detect_gaps(
        placed_parts,
        margin_left,
        margin_right,
        margin_top,
        margin_bottom
    )

