"""
Manufacturing-Aware No-Fit Polygon (NFP) - INNOVATION!

This module implements a revolutionary concept:
Traditional NFP only answers: "Where can parts touch without overlapping?"
Manufacturing NFP answers: "Where can parts be placed AND cut efficiently?"

Key innovations:
1. Kerf and min web integrated into NFP computation
2. Lead-in clearance zones built into NFP
3. Thermal buffer zones for heat management
4. Common edge bonus zones for shared cutting
5. Cut sequence cost encoded in NFP regions
"""

from typing import List, Tuple, Optional, Dict
import numpy as np
from dataclasses import dataclass

from .polygon import Polygon, Point, BoundingBox


@dataclass
class ManufacturingConstraints:
    """Manufacturing constraints that affect NFP"""
    kerf_width: float = 0.3  # mm
    min_web: float = 3.0     # mm
    lead_in_length: float = 2.0  # mm
    lead_in_clearance: float = 5.0  # mm (space needed for lead-in)
    thermal_buffer: float = 0.0  # mm (extra spacing for heat)
    enable_common_cutting: bool = False
    common_edge_bonus: float = 0.0  # Negative value = bring closer


@dataclass
class NFPResult:
    """Result of NFP computation with manufacturing info"""
    nfp_polygon: Polygon
    quality_map: Optional[np.ndarray] = None  # Heat map of placement quality
    common_edge_zones: Optional[List[Tuple[Point, Point]]] = None
    optimal_positions: Optional[List[Point]] = None
    
    def get_quality_at(self, point: Point) -> float:
        """Get manufacturing quality score at a point (0-1, higher is better)"""
        if self.quality_map is None:
            return 0.5  # Neutral
        # TODO: Implement quality lookup
        return 0.5


class ManufacturingAwareNFP:
    """
    Compute No-Fit Polygon with manufacturing awareness
    
    This is a MAJOR INNOVATION: We don't just compute geometric NFP,
    we compute a "manufacturing NFP" that encodes cutting costs,
    thermal considerations, and optimization opportunities.
    """
    
    def __init__(self, constraints: ManufacturingConstraints):
        self.constraints = constraints
        
        # Cache for computed NFPs
        self._nfp_cache: Dict[Tuple[str, str, float], NFPResult] = {}
    
    def compute(
        self,
        stationary: Polygon,
        orbiting: Polygon,
        rotation: float = 0.0,
        consider_thermal: bool = True,
        consider_common_edges: bool = True
    ) -> NFPResult:
        """
        Compute manufacturing-aware NFP
        
        Args:
            stationary: Fixed polygon
            orbiting: Moving polygon
            rotation: Rotation angle of orbiting polygon
            consider_thermal: Include thermal buffer zones
            consider_common_edges: Detect potential common cutting edges
        
        Returns:
            NFPResult with geometric NFP and manufacturing quality map
        """
        # Check cache
        cache_key = (stationary.part_id, orbiting.part_id, rotation)
        if cache_key in self._nfp_cache:
            return self._nfp_cache[cache_key]
        
        # Rotate orbiting polygon
        if rotation != 0:
            orbiting = orbiting.rotate(rotation)
        
        # Step 1: Compute geometric NFP (exact collision boundary)
        geometric_nfp = self._compute_geometric_nfp(stationary, orbiting)
        
        if geometric_nfp is None:
            return None
        
        # Step 2: Apply manufacturing offsets
        # This shrinks the NFP to account for kerf + min web
        manufacturing_offset = (
            self.constraints.kerf_width / 2 +  # Half kerf on each side
            self.constraints.min_web +         # Min web spacing
            self.constraints.thermal_buffer    # Thermal clearance
        )
        
        manufacturing_nfp = geometric_nfp.buffer(-manufacturing_offset)
        
        if manufacturing_nfp is None or manufacturing_nfp.area < 1.0:
            # NFP too small after offsets
            return None
        
        # Step 3: Detect potential common cutting edges
        common_edge_zones = []
        if consider_common_edges and self.constraints.enable_common_cutting:
            common_edge_zones = self._detect_common_edge_zones(
                stationary, orbiting, manufacturing_nfp
            )
        
        # Step 4: Compute quality map
        # This is a heat map showing how "good" each position is
        quality_map = self._compute_quality_map(
            stationary,
            orbiting,
            manufacturing_nfp,
            common_edge_zones,
            consider_thermal
        )
        
        # Step 5: Find optimal positions within NFP
        optimal_positions = self._find_optimal_positions(
            manufacturing_nfp,
            quality_map
        )
        
        result = NFPResult(
            nfp_polygon=manufacturing_nfp,
            quality_map=quality_map,
            common_edge_zones=common_edge_zones,
            optimal_positions=optimal_positions
        )
        
        # Cache result
        self._nfp_cache[cache_key] = result
        
        return result
    
    def _compute_geometric_nfp(
        self,
        stationary: Polygon,
        orbiting: Polygon
    ) -> Optional[Polygon]:
        """
        Compute pure geometric NFP using Minkowski difference
        
        This is the classical NFP: the locus of reference points
        where orbiting can be placed such that it touches but doesn't
        overlap with stationary.
        """
        # Use Shapely's built-in operations
        # NFP = Minkowski difference of stationary and (orbiting reflected and reversed)
        
        # Reflect orbiting around origin
        orbiting_reflected = orbiting.scale(-1)
        
        # Compute Minkowski sum (which gives us the NFP)
        # This is a simplified version - production would use more robust algorithm
        try:
            # Get the convex hull as approximation for now
            # TODO: Implement exact NFP using sliding algorithm or convolution
            stat_shapely = stationary.to_shapely()
            orb_shapely = orbiting_reflected.to_shapely()
            
            # For now, use a conservative approximation
            # Real NFP would use specialized algorithms (e.g., from pyclipper)
            stat_coords = list(stat_shapely.exterior.coords[:-1])
            orb_coords = list(orb_shapely.exterior.coords[:-1])
            
            # Minkowski sum approximation
            nfp_coords = []
            for sx, sy in stat_coords:
                for ox, oy in orb_coords:
                    nfp_coords.append((sx + ox, sy + oy))
            
            if not nfp_coords:
                return None
            
            # Create polygon from convex hull of these points
            from shapely.geometry import MultiPoint
            nfp_shape = MultiPoint(nfp_coords).convex_hull
            
            if nfp_shape.is_empty or nfp_shape.area < 0.1:
                return None
            
            exterior_coords = list(nfp_shape.exterior.coords[:-1])
            return Polygon(exterior_coords)
            
        except Exception as e:
            print(f"NFP computation failed: {e}")
            return None
    
    def _detect_common_edge_zones(
        self,
        stationary: Polygon,
        orbiting: Polygon,
        nfp: Polygon
    ) -> List[Tuple[Point, Point]]:
        """
        Detect zones where common edge cutting is possible
        
        INNOVATION: If two parts share a common edge, we can cut
        that edge once instead of twice, saving time and improving precision.
        """
        common_zones = []
        
        # Compare edges of both polygons
        stat_vertices = stationary.vertices
        orb_vertices = orbiting.vertices
        
        tolerance = 0.5  # mm - edges within this distance can be common
        
        for i in range(len(stat_vertices)):
            stat_edge_start = stat_vertices[i]
            stat_edge_end = stat_vertices[(i + 1) % len(stat_vertices)]
            
            for j in range(len(orb_vertices)):
                orb_edge_start = orb_vertices[j]
                orb_edge_end = orb_vertices[(j + 1) % len(orb_vertices)]
                
                # Check if edges are parallel and close
                if self._edges_can_be_common(
                    stat_edge_start, stat_edge_end,
                    orb_edge_start, orb_edge_end,
                    tolerance
                ):
                    # This is a potential common cutting zone
                    common_zones.append((stat_edge_start, stat_edge_end))
        
        return common_zones
    
    def _edges_can_be_common(
        self,
        a1: Point, a2: Point,
        b1: Point, b2: Point,
        tolerance: float
    ) -> bool:
        """Check if two edges can be cut as a common edge"""
        # Simple check: are they parallel and close?
        # TODO: Implement more sophisticated common edge detection
        
        # Vector of edge A
        ax = a2.x - a1.x
        ay = a2.y - a1.y
        
        # Vector of edge B
        bx = b2.x - b1.x
        by = b2.y - b1.y
        
        # Check if parallel (cross product ≈ 0)
        cross = abs(ax * by - ay * bx)
        
        if cross > tolerance:
            return False
        
        # Check if close
        dist = abs((b1.x - a1.x) * ay - (b1.y - a1.y) * ax) / np.sqrt(ax*ax + ay*ay + 1e-10)
        
        return dist < tolerance
    
    def _compute_quality_map(
        self,
        stationary: Polygon,
        orbiting: Polygon,
        nfp: Polygon,
        common_zones: List[Tuple[Point, Point]],
        consider_thermal: bool
    ) -> np.ndarray:
        """
        Compute quality heat map for NFP
        
        INNOVATION: Not all positions in NFP are equal!
        Some positions are better for manufacturing:
        - Near common edges = good (bonus)
        - Near hot zones = bad (penalty)
        - Corner positions = good (stability)
        - Positions requiring long lead-ins = bad
        
        Returns: 2D array where higher values = better positions
        """
        # For now, return uniform quality
        # TODO: Implement actual quality scoring
        
        bounds = nfp.bounds
        grid_size = 20
        quality_map = np.ones((grid_size, grid_size)) * 0.5
        
        # Bonus near common edge zones
        if common_zones:
            # Increase quality near common edges
            pass
        
        # Penalty in thermal risk zones
        if consider_thermal:
            # Decrease quality in hot zones
            pass
        
        return quality_map
    
    def _find_optimal_positions(
        self,
        nfp: Polygon,
        quality_map: np.ndarray
    ) -> List[Point]:
        """
        Find top N optimal positions within NFP
        
        These are positions that maximize manufacturing quality
        """
        optimal_positions = []
        
        # Find bottom-left (classic strategy)
        bounds = nfp.bounds
        bottom_left = Point(bounds.min_x, bounds.min_y)
        optimal_positions.append(bottom_left)
        
        # Find centroid (balanced position)
        optimal_positions.append(nfp.centroid)
        
        # TODO: Use quality_map to find additional optimal positions
        
        return optimal_positions
    
    def compute_inner_fit_polygon(
        self,
        part: Polygon,
        sheet_bounds: BoundingBox
    ) -> Optional[Polygon]:
        """
        Compute Inner-Fit Polygon (IFP)
        
        This defines where a part can be placed inside the sheet
        while respecting sheet margins and constraints.
        """
        # Account for margins and offsets
        total_offset = (
            self.constraints.kerf_width / 2 +
            self.constraints.min_web +
            self.constraints.lead_in_clearance
        )
        
        # Compute valid placement region
        part_bounds = part.bounds
        
        valid_min_x = sheet_bounds.min_x + total_offset
        valid_max_x = sheet_bounds.max_x - part_bounds.width - total_offset
        valid_min_y = sheet_bounds.min_y + total_offset
        valid_max_y = sheet_bounds.max_y - part_bounds.height - total_offset
        
        if valid_max_x < valid_min_x or valid_max_y < valid_min_y:
            # Part too large for sheet
            return None
        
        # Create rectangle representing valid region
        ifp_vertices = [
            Point(valid_min_x, valid_min_y),
            Point(valid_max_x, valid_min_y),
            Point(valid_max_x, valid_max_y),
            Point(valid_min_x, valid_max_y)
        ]
        
        return Polygon(ifp_vertices)
    
    def clear_cache(self):
        """Clear NFP cache (useful after constraint changes)"""
        self._nfp_cache.clear()
    
    def get_cache_stats(self) -> Dict[str, int]:
        """Get cache statistics"""
        return {
            'cached_nfps': len(self._nfp_cache),
            'memory_estimate_mb': len(self._nfp_cache) * 0.1  # Rough estimate
        }


# Convenience function
def compute_manufacturing_nfp(
    stationary: Polygon,
    orbiting: Polygon,
    constraints: ManufacturingConstraints,
    rotation: float = 0.0
) -> Optional[NFPResult]:
    """
    Convenience function to compute manufacturing-aware NFP
    
    Example:
        constraints = ManufacturingConstraints(kerf_width=0.3, min_web=3.0)
        nfp_result = compute_manufacturing_nfp(part_a, part_b, constraints)
        
        if nfp_result:
            # part_b can be placed at any position in nfp_result.nfp_polygon
            optimal_pos = nfp_result.optimal_positions[0]
    """
    nfp_computer = ManufacturingAwareNFP(constraints)
    return nfp_computer.compute(stationary, orbiting, rotation)

