"""
Robust Polygon Class - Foundation of Geometric Engine

This module provides a production-ready polygon representation with:
- Clean API for geometric operations
- Automatic validation and repair
- Manufacturing-aware operations
- Efficient computation with caching
"""

from typing import List, Tuple, Optional, Union
from dataclasses import dataclass, field
import numpy as np
from shapely.geometry import Polygon as ShapelyPolygon, Point as ShapelyPoint
from shapely.ops import unary_union
from shapely import affinity
import hashlib


@dataclass(frozen=True)
class Point:
    """Immutable 2D point"""
    x: float
    y: float
    
    def __iter__(self):
        return iter((self.x, self.y))
    
    def distance_to(self, other: 'Point') -> float:
        """Euclidean distance to another point"""
        return np.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)
    
    def to_tuple(self) -> Tuple[float, float]:
        return (self.x, self.y)


@dataclass
class BoundingBox:
    """Axis-aligned bounding box"""
    min_x: float
    min_y: float
    max_x: float
    max_y: float
    
    @property
    def width(self) -> float:
        return self.max_x - self.min_x
    
    @property
    def height(self) -> float:
        return self.max_y - self.min_y
    
    @property
    def area(self) -> float:
        return self.width * self.height
    
    @property
    def center(self) -> Point:
        return Point(
            (self.min_x + self.max_x) / 2,
            (self.min_y + self.max_y) / 2
        )
    
    def intersects(self, other: 'BoundingBox') -> bool:
        """Check if two bounding boxes intersect"""
        return not (
            self.max_x < other.min_x or
            self.min_x > other.max_x or
            self.max_y < other.min_y or
            self.min_y > other.max_y
        )
    
    def contains_point(self, point: Point) -> bool:
        """Check if point is inside bounding box"""
        return (
            self.min_x <= point.x <= self.max_x and
            self.min_y <= point.y <= self.max_y
        )


class Polygon:
    """
    Production-ready polygon class with manufacturing awareness
    
    Features:
    - Automatic validation and repair
    - Efficient operations with caching
    - Manufacturing-aware methods
    - Integration with Shapely for complex operations
    """
    
    def __init__(
        self,
        vertices: List[Union[Tuple[float, float], Point]],
        holes: Optional[List[List[Union[Tuple[float, float], Point]]]] = None,
        part_id: Optional[str] = None,
        metadata: Optional[dict] = None
    ):
        """
        Initialize polygon
        
        Args:
            vertices: List of (x, y) tuples or Point objects
            holes: Optional list of hole contours
            part_id: Optional unique identifier
            metadata: Optional metadata dict
        """
        # Convert to Points if needed
        self._vertices = [
            Point(v[0], v[1]) if isinstance(v, (tuple, list)) else v
            for v in vertices
        ]
        
        # Handle holes
        self._holes = []
        if holes:
            for hole in holes:
                hole_points = [
                    Point(v[0], v[1]) if isinstance(v, (tuple, list)) else v
                    for v in hole
                ]
                self._holes.append(hole_points)
        
        self.part_id = part_id or self._generate_id()
        self.metadata = metadata or {}
        
        # Cached properties
        self._shapely_polygon: Optional[ShapelyPolygon] = None
        self._area: Optional[float] = None
        self._bounds: Optional[BoundingBox] = None
        self._centroid: Optional[Point] = None
        self._is_valid: Optional[bool] = None
        
        # Manufacturing properties (will be set by constraints)
        self.kerf_offset: float = 0.0
        self.min_web_offset: float = 0.0
        self.rotation: float = 0.0
        self.position: Optional[Point] = None
    
    def _generate_id(self) -> str:
        """Generate unique ID based on geometry"""
        vertices_str = str([(p.x, p.y) for p in self._vertices])
        return hashlib.md5(vertices_str.encode()).hexdigest()[:8]
    
    @property
    def vertices(self) -> List[Point]:
        """Get polygon vertices"""
        return self._vertices.copy()
    
    @property
    def holes(self) -> List[List[Point]]:
        """Get hole vertices"""
        return [hole.copy() for hole in self._holes]
    
    @property
    def num_vertices(self) -> int:
        """Number of vertices in outer contour"""
        return len(self._vertices)
    
    @property
    def num_holes(self) -> int:
        """Number of holes"""
        return len(self._holes)
    
    @property
    def has_holes(self) -> bool:
        """Check if polygon has holes"""
        return len(self._holes) > 0
    
    def to_shapely(self) -> ShapelyPolygon:
        """Convert to Shapely polygon (cached)"""
        if self._shapely_polygon is None:
            exterior = [(p.x, p.y) for p in self._vertices]
            holes = [[(p.x, p.y) for p in hole] for hole in self._holes]
            self._shapely_polygon = ShapelyPolygon(exterior, holes)
        return self._shapely_polygon
    
    @property
    def area(self) -> float:
        """Calculate polygon area (cached)"""
        if self._area is None:
            self._area = abs(self.to_shapely().area)
        return self._area
    
    @property
    def bounds(self) -> BoundingBox:
        """Get bounding box (cached)"""
        if self._bounds is None:
            min_x = min(p.x for p in self._vertices)
            max_x = max(p.x for p in self._vertices)
            min_y = min(p.y for p in self._vertices)
            max_y = max(p.y for p in self._vertices)
            self._bounds = BoundingBox(min_x, min_y, max_x, max_y)
        return self._bounds
    
    @property
    def centroid(self) -> Point:
        """Calculate centroid (cached)"""
        if self._centroid is None:
            shapely_centroid = self.to_shapely().centroid
            self._centroid = Point(shapely_centroid.x, shapely_centroid.y)
        return self._centroid
    
    @property
    def perimeter(self) -> float:
        """Calculate perimeter length"""
        return self.to_shapely().length
    
    def is_valid(self) -> bool:
        """Check if polygon is geometrically valid (cached)"""
        if self._is_valid is None:
            self._is_valid = self.to_shapely().is_valid
        return self._is_valid
    
    def is_clockwise(self) -> bool:
        """Check if vertices are in clockwise order"""
        return not self.to_shapely().exterior.is_ccw
    
    def make_clockwise(self) -> 'Polygon':
        """Return polygon with clockwise vertex ordering"""
        if self.is_clockwise():
            return self
        return Polygon(
            list(reversed(self._vertices)),
            holes=[list(reversed(hole)) for hole in self._holes],
            part_id=self.part_id,
            metadata=self.metadata.copy()
        )
    
    def rotate(self, angle: float, origin: Optional[Point] = None) -> 'Polygon':
        """
        Rotate polygon
        
        Args:
            angle: Rotation angle in degrees (counter-clockwise)
            origin: Point to rotate around (default: centroid)
        
        Returns:
            New rotated polygon
        """
        if origin is None:
            origin = self.centroid
        
        shapely_poly = self.to_shapely()
        rotated = affinity.rotate(
            shapely_poly,
            angle,
            origin=(origin.x, origin.y),
            use_radians=False
        )
        
        exterior_coords = list(rotated.exterior.coords[:-1])  # Remove duplicate last point
        hole_coords = [list(hole.coords[:-1]) for hole in rotated.interiors]
        
        new_poly = Polygon(
            exterior_coords,
            holes=hole_coords if hole_coords else None,
            part_id=self.part_id,
            metadata=self.metadata.copy()
        )
        new_poly.rotation = (self.rotation + angle) % 360
        return new_poly
    
    def translate(self, dx: float, dy: float) -> 'Polygon':
        """Translate polygon by (dx, dy)"""
        new_vertices = [Point(p.x + dx, p.y + dy) for p in self._vertices]
        new_holes = [[Point(p.x + dx, p.y + dy) for p in hole] for hole in self._holes]
        
        new_poly = Polygon(
            new_vertices,
            holes=new_holes if new_holes else None,
            part_id=self.part_id,
            metadata=self.metadata.copy()
        )
        new_poly.rotation = self.rotation
        if self.position:
            new_poly.position = Point(self.position.x + dx, self.position.y + dy)
        return new_poly
    
    def scale(self, factor: float, origin: Optional[Point] = None) -> 'Polygon':
        """Scale polygon uniformly"""
        if origin is None:
            origin = self.centroid
        
        shapely_poly = self.to_shapely()
        scaled = affinity.scale(
            shapely_poly,
            xfact=factor,
            yfact=factor,
            origin=(origin.x, origin.y)
        )
        
        exterior_coords = list(scaled.exterior.coords[:-1])
        hole_coords = [list(hole.coords[:-1]) for hole in scaled.interiors]
        
        return Polygon(
            exterior_coords,
            holes=hole_coords if hole_coords else None,
            part_id=self.part_id,
            metadata=self.metadata.copy()
        )
    
    def buffer(self, distance: float) -> 'Polygon':
        """
        Buffer (offset) polygon
        
        Positive distance = outward offset
        Negative distance = inward offset
        """
        buffered = self.to_shapely().buffer(
            distance,
            join_style='mitre',
            mitre_limit=2.0
        )
        
        if buffered.is_empty:
            return None
        
        exterior_coords = list(buffered.exterior.coords[:-1])
        hole_coords = [list(hole.coords[:-1]) for hole in buffered.interiors]
        
        return Polygon(
            exterior_coords,
            holes=hole_coords if hole_coords else None,
            part_id=self.part_id,
            metadata=self.metadata.copy()
        )
    
    def intersects(self, other: 'Polygon') -> bool:
        """Check if polygon intersects another polygon"""
        # Quick bounding box check first
        if not self.bounds.intersects(other.bounds):
            return False
        
        # Precise check
        return self.to_shapely().intersects(other.to_shapely())
    
    def contains(self, other: 'Polygon') -> bool:
        """Check if polygon fully contains another polygon"""
        return self.to_shapely().contains(other.to_shapely())
    
    def contains_point(self, point: Point) -> bool:
        """Check if point is inside polygon"""
        shapely_point = ShapelyPoint(point.x, point.y)
        return self.to_shapely().contains(shapely_point)
    
    def distance_to(self, other: 'Polygon') -> float:
        """Minimum distance to another polygon"""
        return self.to_shapely().distance(other.to_shapely())
    
    def intersection(self, other: 'Polygon') -> Optional['Polygon']:
        """Compute intersection with another polygon"""
        result = self.to_shapely().intersection(other.to_shapely())
        
        if result.is_empty:
            return None
        
        if result.geom_type == 'Polygon':
            exterior_coords = list(result.exterior.coords[:-1])
            hole_coords = [list(hole.coords[:-1]) for hole in result.interiors]
            return Polygon(exterior_coords, holes=hole_coords if hole_coords else None)
        
        return None  # MultiPolygon or other types not handled yet
    
    def union(self, other: 'Polygon') -> 'Polygon':
        """Compute union with another polygon"""
        result = self.to_shapely().union(other.to_shapely())
        
        if result.geom_type == 'Polygon':
            exterior_coords = list(result.exterior.coords[:-1])
            hole_coords = [list(hole.coords[:-1]) for hole in result.interiors]
            return Polygon(exterior_coords, holes=hole_coords if hole_coords else None)
        
        return None
    
    def simplify(self, tolerance: float = 0.01) -> 'Polygon':
        """Simplify polygon using Douglas-Peucker"""
        simplified = self.to_shapely().simplify(
            tolerance,
            preserve_topology=True
        )
        
        exterior_coords = list(simplified.exterior.coords[:-1])
        hole_coords = [list(hole.coords[:-1]) for hole in simplified.interiors]
        
        return Polygon(
            exterior_coords,
            holes=hole_coords if hole_coords else None,
            part_id=self.part_id,
            metadata=self.metadata.copy()
        )
    
    def convex_hull(self) -> 'Polygon':
        """Compute convex hull"""
        hull = self.to_shapely().convex_hull
        exterior_coords = list(hull.exterior.coords[:-1])
        return Polygon(exterior_coords)
    
    @property
    def convexity(self) -> float:
        """
        Calculate convexity: area / convex_hull_area
        1.0 = perfectly convex, <1.0 = concave
        """
        hull_area = self.convex_hull().area
        if hull_area == 0:
            return 0.0
        return self.area / hull_area
    
    @property
    def aspect_ratio(self) -> float:
        """Calculate aspect ratio: width / height"""
        bounds = self.bounds
        if bounds.height == 0:
            return float('inf')
        return bounds.width / bounds.height
    
    @property
    def compactness(self) -> float:
        """
        Calculate compactness: 4π * area / perimeter²
        1.0 = circle, <1.0 = less compact
        """
        if self.perimeter == 0:
            return 0.0
        return (4 * np.pi * self.area) / (self.perimeter ** 2)
    
    def to_dict(self) -> dict:
        """Convert to dictionary representation"""
        return {
            'part_id': self.part_id,
            'vertices': [(p.x, p.y) for p in self._vertices],
            'holes': [[(p.x, p.y) for p in hole] for hole in self._holes],
            'area': self.area,
            'rotation': self.rotation,
            'position': (self.position.x, self.position.y) if self.position else None,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Polygon':
        """Create polygon from dictionary"""
        poly = cls(
            vertices=data['vertices'],
            holes=data.get('holes'),
            part_id=data.get('part_id'),
            metadata=data.get('metadata', {})
        )
        poly.rotation = data.get('rotation', 0.0)
        if data.get('position'):
            poly.position = Point(*data['position'])
        return poly
    
    def normalize_to_origin(self) -> 'Polygon':
        """
        Normalize polygon to origin (0,0) by translating it so its bottom-left corner is at (0,0)
        
        Returns:
            New polygon with vertices translated to origin
        """
        bounds = self.bounds
        dx = -bounds.min_x
        dy = -bounds.min_y
        
        # Translate vertices
        normalized_vertices = [Point(v.x + dx, v.y + dy) for v in self.vertices]
        
        # Translate holes
        normalized_holes = []
        if self.has_holes:
            for hole in self.holes:
                normalized_hole = [Point(p.x + dx, p.y + dy) for p in hole]
                normalized_holes.append(normalized_hole)
        
        return Polygon(
            vertices=normalized_vertices,
            holes=normalized_holes,
            part_id=self.part_id
        )
    
    def __repr__(self) -> str:
        holes_str = f", {self.num_holes} holes" if self.has_holes else ""
        return f"Polygon(id={self.part_id}, vertices={self.num_vertices}{holes_str}, area={self.area:.2f})"
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, Polygon):
            return False
        return self.part_id == other.part_id
    
    def __hash__(self) -> int:
        return hash(self.part_id)

