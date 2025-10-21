"""
Common-Edge Cutting Detection

Detects when two parts share an edge that can be cut together,
reducing pierce count and cut time.

Benefits:
- Fewer pierces (expensive, slow)
- Reduced cut path length
- Less thermal stress
- Faster production

Example: Two rectangles side-by-side can share the middle edge
"""

from typing import List, Tuple, Set, Dict
from dataclasses import dataclass
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from geometry.polygon import Polygon
from geometry.collision import PlacedPart


@dataclass
class CommonEdge:
    """Represents a shared edge between two parts"""
    part1_index: int
    part2_index: int
    edge_length: float  # mm
    shared_vertices: List[Tuple[float, float]]
    
    def __repr__(self):
        return f"CommonEdge(part{self.part1_index}↔part{self.part2_index}, {self.edge_length:.1f}mm)"


class CommonEdgeDetector:
    """
    Detect common edges between placed parts
    
    Algorithm:
    1. For each pair of adjacent parts
    2. Check if they share edges (within tolerance)
    3. Calculate shared edge length
    4. Return list of common edges
    """
    
    def __init__(self, tolerance: float = 0.5):
        """
        Initialize common edge detector
        
        Args:
            tolerance: Distance tolerance for edge matching (mm)
        """
        self.tolerance = tolerance
    
    def detect(
        self,
        placed_parts: List[PlacedPart]
    ) -> List[CommonEdge]:
        """
        Detect common edges between placed parts
        
        Args:
            placed_parts: List of placed parts with positions
        
        Returns:
            List of CommonEdge objects
        """
        common_edges = []
        
        # Check each pair of parts
        for i in range(len(placed_parts)):
            for j in range(i + 1, len(placed_parts)):
                # Get transformed polygons
                poly1 = placed_parts[i].get_transformed_polygon()
                poly2 = placed_parts[j].get_transformed_polygon()
                
                # Check if bounding boxes are adjacent
                bounds1 = poly1.bounds
                bounds2 = poly2.bounds
                
                if not self._are_adjacent(bounds1, bounds2):
                    continue
                
                # Check for shared edges
                edge = self._find_shared_edge(poly1, poly2, i, j)
                
                if edge and edge.edge_length > 5.0:  # Only report edges > 5mm
                    common_edges.append(edge)
        
        # Sort by edge length (longest first)
        common_edges.sort(key=lambda e: e.edge_length, reverse=True)
        
        return common_edges
    
    def _are_adjacent(self, bounds1, bounds2) -> bool:
        """Quick check if bounding boxes are adjacent"""
        # Check if they touch horizontally
        h_adjacent = (
            abs(bounds1.max_x - bounds2.min_x) < self.tolerance or
            abs(bounds2.max_x - bounds1.min_x) < self.tolerance
        )
        
        # Check if they touch vertically
        v_adjacent = (
            abs(bounds1.max_y - bounds2.min_y) < self.tolerance or
            abs(bounds2.max_y - bounds1.min_y) < self.tolerance
        )
        
        # Must be adjacent AND overlap in other dimension
        if h_adjacent:
            # Check vertical overlap
            y_overlap = not (bounds1.max_y < bounds2.min_y or bounds2.max_y < bounds1.min_y)
            return y_overlap
        
        if v_adjacent:
            # Check horizontal overlap
            x_overlap = not (bounds1.max_x < bounds2.min_x or bounds2.max_x < bounds1.min_x)
            return x_overlap
        
        return False
    
    def _find_shared_edge(
        self,
        poly1: Polygon,
        poly2: Polygon,
        idx1: int,
        idx2: int
    ) -> CommonEdge:
        """Find shared edge between two polygons"""
        shared_vertices = []
        total_length = 0.0
        
        # Get vertices of both polygons
        vertices1 = poly1.vertices
        vertices2 = poly2.vertices
        coords1 = [(v.x, v.y) for v in vertices1]
        coords2 = [(v.x, v.y) for v in vertices2]
        
        # For each edge in poly1, check if any edge in poly2 coincides
        for i in range(len(coords1) - 1):
            p1_start = coords1[i]
            p1_end = coords1[i + 1]
            
            for j in range(len(coords2) - 1):
                p2_start = coords2[j]
                p2_end = coords2[j + 1]
                
                # Check if edges overlap (same line, opposite directions)
                if self._edges_coincide(p1_start, p1_end, p2_start, p2_end):
                    # Calculate overlap length
                    length = ((p1_end[0] - p1_start[0])**2 + (p1_end[1] - p1_start[1])**2) ** 0.5
                    total_length += length
                    
                    if p1_start not in shared_vertices:
                        shared_vertices.append(p1_start)
                    if p1_end not in shared_vertices:
                        shared_vertices.append(p1_end)
        
        if total_length > 0:
            return CommonEdge(
                part1_index=idx1,
                part2_index=idx2,
                edge_length=total_length,
                shared_vertices=shared_vertices
            )
        
        return None
    
    def _edges_coincide(
        self,
        p1_start: Tuple[float, float],
        p1_end: Tuple[float, float],
        p2_start: Tuple[float, float],
        p2_end: Tuple[float, float]
    ) -> bool:
        """Check if two edges coincide (same line segment)"""
        # Check if p1_start matches p2_end and p1_end matches p2_start (opposite direction)
        start_match = (
            abs(p1_start[0] - p2_end[0]) < self.tolerance and
            abs(p1_start[1] - p2_end[1]) < self.tolerance
        )
        end_match = (
            abs(p1_end[0] - p2_start[0]) < self.tolerance and
            abs(p1_end[1] - p2_start[1]) < self.tolerance
        )
        
        if start_match and end_match:
            return True
        
        # Or check if same direction (less common but possible)
        start_match2 = (
            abs(p1_start[0] - p2_start[0]) < self.tolerance and
            abs(p1_start[1] - p2_start[1]) < self.tolerance
        )
        end_match2 = (
            abs(p1_end[0] - p2_end[0]) < self.tolerance and
            abs(p1_end[1] - p2_end[1]) < self.tolerance
        )
        
        return start_match2 and end_match2
    
    def calculate_savings(self, common_edges: List[CommonEdge]) -> Dict[str, float]:
        """
        Calculate manufacturing savings from common-edge cutting
        
        Returns:
            Dictionary with:
            - total_common_length: mm of shared edges
            - pierce_savings: number of pierces saved
            - cut_length_savings: mm of cut path saved
            - estimated_time_savings: seconds saved (assuming 2s per pierce)
        """
        total_length = sum(e.edge_length for e in common_edges)
        pierce_savings = len(common_edges)  # One pierce saved per common edge
        
        return {
            'total_common_length': total_length,
            'pierce_savings': pierce_savings,
            'cut_length_savings': total_length,  # Don't need to cut shared edge twice
            'estimated_time_savings': pierce_savings * 2.0  # 2 seconds per pierce saved
        }


def detect_common_edges(
    placed_parts: List[PlacedPart],
    tolerance: float = 0.5
) -> List[CommonEdge]:
    """
    Convenience function to detect common edges
    
    Example:
        edges = detect_common_edges(placed_parts)
        print(f"Found {len(edges)} common edges")
        for edge in edges:
            print(f"  {edge}")
    """
    detector = CommonEdgeDetector(tolerance=tolerance)
    return detector.detect(placed_parts)

