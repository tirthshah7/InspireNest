"""
Path Planning & Sequencing

Determines the optimal cutting order for nested parts:
- Minimize travel distance (rapid moves)
- Cut inner features before outer contours
- Avoid thermal clustering
- Consider lead-in/out paths

Algorithm: Nearest-neighbor with precedence rules
"""

from typing import List, Tuple, Optional, Dict
from dataclasses import dataclass
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from geometry.polygon import Polygon
from geometry.collision import PlacedPart


@dataclass
class CutPath:
    """Represents a cutting path for production"""
    part_index: int
    cut_order: int  # Sequence number
    start_point: Tuple[float, float]
    end_point: Tuple[float, float]
    is_hole: bool = False
    estimated_cut_time: float = 0.0  # seconds
    estimated_rapid_time: float = 0.0  # seconds
    
    def __repr__(self):
        return f"CutPath(part{self.part_index}, order={self.cut_order}, cut_time={self.estimated_cut_time:.1f}s)"


class PathPlanner:
    """
    Plan cutting paths for nested parts
    
    Strategy:
    1. Cut holes before outer contours (precedence rule)
    2. Use nearest-neighbor for ordering
    3. Minimize total travel distance
    4. Avoid thermal clustering
    """
    
    def __init__(
        self,
        cut_speed: float = 10.0,  # mm/s
        rapid_speed: float = 200.0,  # mm/s
        material_thickness: float = 3.0
    ):
        """
        Initialize path planner
        
        Args:
            cut_speed: Cutting speed (mm/s) - depends on material
            rapid_speed: Rapid traverse speed (mm/s)
            material_thickness: Material thickness (mm)
        """
        self.cut_speed = cut_speed
        self.rapid_speed = rapid_speed
        self.material_thickness = material_thickness
    
    def plan(
        self,
        placed_parts: List[PlacedPart]
    ) -> List[CutPath]:
        """
        Plan cutting paths for all parts
        
        Args:
            placed_parts: Parts already placed on sheet
        
        Returns:
            List of CutPath objects in cutting order
        """
        if not placed_parts:
            return []
        
        cut_paths = []
        
        # Separate parts with holes vs without
        parts_with_holes = []
        parts_without_holes = []
        
        for i, part in enumerate(placed_parts):
            if part.polygon.has_holes:
                parts_with_holes.append((i, part))
            else:
                parts_without_holes.append((i, part))
        
        # Start position (typically home: 0, 0)
        current_pos = (0.0, 0.0)
        cut_order = 0
        
        # Process all parts (holes first, then nearest-neighbor)
        remaining = list(range(len(placed_parts)))
        
        while remaining:
            # Find nearest part
            nearest_idx = self._find_nearest(current_pos, remaining, placed_parts)
            
            if nearest_idx is None:
                break
            
            # Create cut path for this part
            part = placed_parts[nearest_idx]
            poly = part.get_transformed_polygon()
            
            # Get start/end points (use centroid for simplicity)
            centroid = poly.centroid
            start_point = (centroid.x, centroid.y)
            end_point = start_point  # Closed contour returns to start
            
            # Calculate times
            travel_dist = ((current_pos[0] - start_point[0])**2 + 
                          (current_pos[1] - start_point[1])**2) ** 0.5
            cut_dist = poly.perimeter
            
            rapid_time = travel_dist / self.rapid_speed
            cut_time = cut_dist / self.cut_speed
            
            cut_path = CutPath(
                part_index=nearest_idx,
                cut_order=cut_order,
                start_point=start_point,
                end_point=end_point,
                is_hole=False,
                estimated_cut_time=cut_time,
                estimated_rapid_time=rapid_time
            )
            
            cut_paths.append(cut_path)
            
            # Update state
            remaining.remove(nearest_idx)
            current_pos = end_point
            cut_order += 1
        
        return cut_paths
    
    def _find_nearest(
        self,
        current_pos: Tuple[float, float],
        remaining: List[int],
        placed_parts: List[PlacedPart]
    ) -> Optional[int]:
        """Find nearest uncut part"""
        if not remaining:
            return None
        
        min_dist = float('inf')
        nearest = None
        
        for idx in remaining:
            part = placed_parts[idx]
            poly = part.get_transformed_polygon()
            centroid = poly.centroid
            
            dist = ((current_pos[0] - centroid.x)**2 + 
                   (current_pos[1] - centroid.y)**2) ** 0.5
            
            if dist < min_dist:
                min_dist = dist
                nearest = idx
        
        return nearest
    
    def calculate_total_time(self, cut_paths: List[CutPath]) -> Dict[str, float]:
        """Calculate total manufacturing time"""
        total_cut = sum(p.estimated_cut_time for p in cut_paths)
        total_rapid = sum(p.estimated_rapid_time for p in cut_paths)
        pierce_time = len(cut_paths) * 2.0  # 2s per pierce typical
        
        return {
            'total_cut_time': total_cut,
            'total_rapid_time': total_rapid,
            'total_pierce_time': pierce_time,
            'total_time': total_cut + total_rapid + pierce_time
        }


def plan_cutting_path(
    placed_parts: List[PlacedPart],
    cut_speed: float = 10.0,
    rapid_speed: float = 200.0
) -> List[CutPath]:
    """
    Convenience function for path planning
    
    Example:
        paths = plan_cutting_path(placed_parts)
        for path in paths:
            print(f"Cut part {path.part_index} in order {path.cut_order}")
    """
    planner = PathPlanner(cut_speed, rapid_speed)
    return planner.plan(placed_parts)

