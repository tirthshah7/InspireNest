"""
Topology Solver - Group Disconnected Segments into Shapes

Many DXF files (especially from CAD programs) export closed shapes
as disconnected LINE/ARC segments that need to be grouped together.

This module:
1. Groups connected segments into closed shapes
2. Detects and associates holes with parent shapes
3. Handles complex topological relationships
"""

from typing import List, Tuple, Set, Dict, Optional
from collections import defaultdict
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from geometry.polygon import Polygon, Point

import time


class TopologySolver:
    """
    Solve topological relationships in disconnected geometry
    
    Features:
    - Group connected segments into closed shapes
    - Detect parent-child relationships (holes)
    - Handle self-intersecting geometry
    - Validate and fix topology
    """
    
    def __init__(self, tolerance: float = 0.1):
        """
        Initialize topology solver
        
        Args:
            tolerance: Point matching tolerance (mm)
        """
        self.tolerance = tolerance
        self.tolerance_sq = tolerance * tolerance
    
    def group_segments(
        self,
        segments: List[List[Point]]
    ) -> List[List[Point]]:
        """
        Group disconnected segments into closed shapes
        
        Args:
            segments: List of segment point lists (each segment is 2+ points)
        
        Returns:
            List of closed shape point lists
        
        Algorithm:
        1. Build connectivity graph
        2. Find connected components
        3. Order segments into closed loops
        """
        if not segments:
            return []
        
        start_time = time.time()
        
        # Build connectivity graph
        graph = self._build_connectivity_graph(segments)
        
        # Find connected components (separate shapes)
        components = self._find_connected_components(graph, segments)
        
        # Order each component into a closed loop
        closed_shapes = []
        for component_indices in components:
            component_segments = [segments[i] for i in component_indices]
            ordered_shape = self._order_segments(component_segments)
            
            if ordered_shape and len(ordered_shape) >= 3:
                closed_shapes.append(ordered_shape)
        
        elapsed = time.time() - start_time
        
        if len(segments) > 10:
            print(f"  Topology solver: {len(segments)} segments → {len(closed_shapes)} shapes in {elapsed*1000:.1f}ms")
        
        return closed_shapes
    
    def _build_connectivity_graph(
        self,
        segments: List[List[Point]]
    ) -> Dict[int, Set[int]]:
        """
        Build graph where segments are nodes, connected if they share endpoints
        
        Returns: Dict mapping segment index to set of connected segment indices
        """
        graph = defaultdict(set)
        
        # Check each pair of segments
        for i in range(len(segments)):
            for j in range(i + 1, len(segments)):
                if self._segments_connected(segments[i], segments[j]):
                    graph[i].add(j)
                    graph[j].add(i)
        
        return graph
    
    def _segments_connected(
        self,
        seg1: List[Point],
        seg2: List[Point]
    ) -> bool:
        """Check if two segments share an endpoint"""
        if not seg1 or not seg2:
            return False
        
        # Get endpoints
        seg1_start = seg1[0]
        seg1_end = seg1[-1]
        seg2_start = seg2[0]
        seg2_end = seg2[-1]
        
        # Check if any endpoints match
        return (
            self._points_close(seg1_start, seg2_start) or
            self._points_close(seg1_start, seg2_end) or
            self._points_close(seg1_end, seg2_start) or
            self._points_close(seg1_end, seg2_end)
        )
    
    def _points_close(self, p1: Point, p2: Point) -> bool:
        """Check if two points are within tolerance"""
        dx = p1.x - p2.x
        dy = p1.y - p2.y
        return (dx*dx + dy*dy) < self.tolerance_sq
    
    def _find_connected_components(
        self,
        graph: Dict[int, Set[int]],
        segments: List[List[Point]]
    ) -> List[List[int]]:
        """
        Find connected components in graph using DFS
        
        Returns: List of component index lists
        """
        visited = set()
        components = []
        
        for start_idx in range(len(segments)):
            if start_idx not in visited:
                # DFS to find connected component
                component = []
                stack = [start_idx]
                
                while stack:
                    idx = stack.pop()
                    if idx not in visited:
                        visited.add(idx)
                        component.append(idx)
                        
                        # Add neighbors
                        if idx in graph:
                            for neighbor in graph[idx]:
                                if neighbor not in visited:
                                    stack.append(neighbor)
                
                if component:
                    components.append(component)
        
        return components
    
    def _order_segments(
        self,
        segments: List[List[Point]]
    ) -> Optional[List[Point]]:
        """
        Order disconnected segments into a continuous path
        
        Strategy:
        1. Start with first segment
        2. Find next segment that connects to current endpoint
        3. Flip segment if needed
        4. Continue until loop closes or no more segments
        """
        if not segments:
            return None
        
        if len(segments) == 1:
            # Already a single continuous segment
            return segments[0]
        
        # Start with first segment
        ordered_points = list(segments[0])
        used_indices = {0}
        
        # Try to connect remaining segments
        max_iterations = len(segments) * 2  # Prevent infinite loops
        iterations = 0
        
        while len(used_indices) < len(segments) and iterations < max_iterations:
            iterations += 1
            current_end = ordered_points[-1]
            found_connection = False
            
            # Find segment that connects to current end
            for i, segment in enumerate(segments):
                if i in used_indices:
                    continue
                
                seg_start = segment[0]
                seg_end = segment[-1]
                
                if self._points_close(current_end, seg_start):
                    # Connects in forward direction
                    ordered_points.extend(segment[1:])  # Skip duplicate point
                    used_indices.add(i)
                    found_connection = True
                    break
                
                elif self._points_close(current_end, seg_end):
                    # Connects in reverse direction
                    ordered_points.extend(reversed(segment[:-1]))
                    used_indices.add(i)
                    found_connection = True
                    break
            
            if not found_connection:
                break  # Can't connect more segments
        
        # Remove duplicate closing point if present
        if len(ordered_points) > 1:
            if self._points_close(ordered_points[0], ordered_points[-1]):
                ordered_points = ordered_points[:-1]
        
        return ordered_points if len(ordered_points) >= 3 else None
    
    def detect_holes(
        self,
        shapes: List[Polygon]
    ) -> List[Polygon]:
        """
        Detect which shapes are holes inside other shapes
        
        Returns: List of Polygon objects with holes properly associated
        
        Algorithm:
        1. Sort shapes by area (largest first)
        2. For each shape, check if smaller shapes are inside it
        3. Associate holes with parent shapes
        """
        if len(shapes) <= 1:
            return shapes
        
        start_time = time.time()
        
        # Sort by area (largest first)
        sorted_shapes = sorted(shapes, key=lambda p: p.area, reverse=True)
        
        # Track which shapes are holes
        is_hole = [False] * len(sorted_shapes)
        hole_parent = [-1] * len(sorted_shapes)
        
        # For each shape, find holes inside it
        for i, parent in enumerate(sorted_shapes):
            if is_hole[i]:
                continue  # Skip shapes that are already holes
            
            for j, potential_hole in enumerate(sorted_shapes):
                if i == j or is_hole[j]:
                    continue
                
                # Check if potential_hole is inside parent
                if parent.contains(potential_hole):
                    is_hole[j] = True
                    hole_parent[j] = i
        
        # Build result with holes associated
        result = []
        processed = set()
        
        for i, shape in enumerate(sorted_shapes):
            if i in processed or is_hole[i]:
                continue
            
            # Find all holes for this shape
            holes = []
            for j, h_parent in enumerate(hole_parent):
                if h_parent == i:
                    # Convert hole vertices to relative coordinates within the parent
                    hole_shape = sorted_shapes[j]
                    parent_bounds = shape.bounds
                    relative_hole = []
                    for vertex in hole_shape.vertices:
                        relative_x = vertex.x - parent_bounds.min_x
                        relative_y = vertex.y - parent_bounds.min_y
                        relative_hole.append(Point(relative_x, relative_y))
                    holes.append(relative_hole)
                    processed.add(j)
            
            # Create polygon with holes
            if holes:
                poly = Polygon(
                    shape.vertices,
                    holes=holes,
                    part_id=shape.part_id,
                    metadata=shape.metadata
                )
            else:
                poly = shape
            
            result.append(poly)
            processed.add(i)
        
        elapsed = time.time() - start_time
        holes_found = sum(1 for h in is_hole if h)
        
        if holes_found > 0:
            print(f"  Hole detection: {holes_found} holes found in {elapsed*1000:.1f}ms")
        
        return result


# Convenience function
def group_disconnected_segments(
    segments: List[List[Point]],
    tolerance: float = 0.1
) -> List[List[Point]]:
    """
    Group disconnected segments into closed shapes
    
    Example:
        # 4 LINE segments forming a rectangle
        segments = [
            [Point(0,0), Point(10,0)],
            [Point(10,0), Point(10,5)],
            [Point(10,5), Point(0,5)],
            [Point(0,5), Point(0,0)]
        ]
        
        shapes = group_disconnected_segments(segments)
        # Returns: [[Point(0,0), Point(10,0), Point(10,5), Point(0,5)]]
    """
    solver = TopologySolver(tolerance)
    return solver.group_segments(segments)

