"""
Lead-In/Lead-Out Generation

Generates lead-in and lead-out paths for laser cutting to:
- Avoid damaging part edges
- Ensure clean pierce points
- Prevent tip-ups and thermal warping
- Follow best practices for laser cutting

Types of lead-ins:
- Linear: Straight line approach
- Arc: Curved approach (smoother)
- Loop: Full loop for clean entry
"""

from typing import List, Tuple, Optional
from dataclasses import dataclass
from math import cos, sin, pi, atan2
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from geometry.polygon import Polygon, Point


@dataclass
class LeadInOut:
    """Lead-in/lead-out path for a part"""
    part_index: int
    pierce_point: Tuple[float, float]  # Where laser pierces
    lead_in_start: Tuple[float, float]  # Start of lead-in
    lead_in_path: List[Tuple[float, float]]  # Full lead-in path
    lead_out_end: Tuple[float, float]  # End of lead-out
    lead_out_path: List[Tuple[float, float]]  # Full lead-out path
    lead_type: str  # 'linear', 'arc', or 'loop'
    
    def __repr__(self):
        return f"LeadInOut(part{self.part_index}, {self.lead_type}, pierce at {self.pierce_point})"


class LeadInOutGenerator:
    """
    Generate lead-in/lead-out paths for laser cutting
    
    Best practices:
    - Lead-in length: 1-5mm depending on material thickness
    - Pierce point: Away from part edges (inside material)
    - Arc lead-ins preferred for thick materials
    - Linear for thin materials
    """
    
    def __init__(
        self,
        lead_in_length: float = 3.0,  # mm
        lead_in_type: str = 'arc',  # 'linear', 'arc', or 'loop'
        material_thickness: float = 3.0  # mm
    ):
        """
        Initialize lead-in/out generator
        
        Args:
            lead_in_length: Length of lead-in path (mm)
            lead_in_type: Type of lead-in ('linear', 'arc', 'loop')
            material_thickness: Material thickness (affects lead-in strategy)
        """
        self.lead_in_length = lead_in_length
        self.lead_in_type = lead_in_type
        self.material_thickness = material_thickness
        
        # Adjust lead-in based on thickness
        if material_thickness > 6.0:
            self.lead_in_length = max(5.0, lead_in_length)
            self.lead_in_type = 'arc'  # Arc better for thick
        elif material_thickness < 2.0:
            self.lead_in_length = max(2.0, lead_in_length)
            self.lead_in_type = 'linear'  # Linear ok for thin
    
    def generate(
        self,
        polygon: Polygon,
        part_index: int = 0
    ) -> LeadInOut:
        """
        Generate lead-in/out for a polygon
        
        Args:
            polygon: Polygon to generate lead-in for
            part_index: Index of this part
        
        Returns:
            LeadInOut object with paths
        """
        # Find a good pierce point (start of contour, or longest edge midpoint)
        pierce_point = self._find_pierce_point(polygon)
        
        # Generate lead-in based on type
        if self.lead_in_type == 'linear':
            lead_in_path = self._generate_linear_lead_in(polygon, pierce_point)
        elif self.lead_in_type == 'arc':
            lead_in_path = self._generate_arc_lead_in(polygon, pierce_point)
        else:  # loop
            lead_in_path = self._generate_loop_lead_in(polygon, pierce_point)
        
        # Lead-out is typically reverse of lead-in
        lead_out_path = list(reversed(lead_in_path))
        
        return LeadInOut(
            part_index=part_index,
            pierce_point=pierce_point,
            lead_in_start=lead_in_path[0] if lead_in_path else pierce_point,
            lead_in_path=lead_in_path,
            lead_out_end=lead_out_path[-1] if lead_out_path else pierce_point,
            lead_out_path=lead_out_path,
            lead_type=self.lead_in_type
        )
    
    def generate_batch(
        self,
        polygons: List[Polygon]
    ) -> List[LeadInOut]:
        """Generate lead-ins for multiple polygons"""
        return [self.generate(poly, i) for i, poly in enumerate(polygons)]
    
    def _find_pierce_point(self, polygon: Polygon) -> Tuple[float, float]:
        """
        Find optimal pierce point for polygon
        
        Strategy: Use start of contour (typically bottom-left)
        """
        vertices = polygon.vertices
        
        if len(vertices) > 0:
            return (vertices[0].x, vertices[0].y)
        
        # Fallback: centroid
        centroid = polygon.centroid
        return (centroid.x, centroid.y)
    
    def _generate_linear_lead_in(
        self,
        polygon: Polygon,
        pierce_point: Tuple[float, float]
    ) -> List[Tuple[float, float]]:
        """
        Generate straight-line lead-in
        
        Approach from outside at 45° angle
        """
        px, py = pierce_point
        
        # Approach at 45° from outside
        angle = -pi / 4  # -45 degrees (from lower-left)
        
        start_x = px + self.lead_in_length * cos(angle)
        start_y = py + self.lead_in_length * sin(angle)
        
        return [
            (start_x, start_y),
            pierce_point
        ]
    
    def _generate_arc_lead_in(
        self,
        polygon: Polygon,
        pierce_point: Tuple[float, float]
    ) -> List[Tuple[float, float]]:
        """
        Generate arc lead-in (smoother than linear)
        
        Creates a quarter-circle approach
        """
        px, py = pierce_point
        
        # Arc parameters
        radius = self.lead_in_length
        num_segments = 8
        
        # Start angle: -90° (from below)
        start_angle = -pi / 2
        end_angle = 0  # Tangent to part edge
        
        path = []
        for i in range(num_segments + 1):
            t = i / num_segments
            angle = start_angle + t * (end_angle - start_angle)
            
            x = px + radius * cos(angle)
            y = py + radius * sin(angle)
            path.append((x, y))
        
        return path
    
    def _generate_loop_lead_in(
        self,
        polygon: Polygon,
        pierce_point: Tuple[float, float]
    ) -> List[Tuple[float, float]]:
        """
        Generate loop lead-in (best for thick materials)
        
        Creates a small circle for clean pierce
        """
        px, py = pierce_point
        
        # Loop parameters
        radius = self.lead_in_length * 0.5
        num_segments = 12
        
        path = []
        for i in range(num_segments + 1):
            angle = 2 * pi * i / num_segments
            
            x = px + radius * cos(angle)
            y = py + radius * sin(angle)
            path.append((x, y))
        
        return path


def generate_lead_ins(
    polygons: List[Polygon],
    material_thickness: float = 3.0,
    lead_in_type: str = 'arc'
) -> List[LeadInOut]:
    """
    Convenience function to generate lead-ins
    
    Example:
        polygons = [poly1, poly2, poly3]
        lead_ins = generate_lead_ins(polygons, material_thickness=3.0)
        
        for lead in lead_ins:
            print(f"Part {lead.part_index}: Pierce at {lead.pierce_point}")
    """
    generator = LeadInOutGenerator(
        lead_in_length=3.0,
        lead_in_type=lead_in_type,
        material_thickness=material_thickness
    )
    return generator.generate_batch(polygons)

