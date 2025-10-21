"""
Unit Tests for Polygon Class

Comprehensive tests for all polygon operations
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

import pytest
import numpy as np
from geometry.polygon import Polygon, Point, BoundingBox


class TestPoint:
    """Tests for Point class"""
    
    def test_point_creation(self):
        p = Point(10.5, 20.3)
        assert p.x == 10.5
        assert p.y == 20.3
    
    def test_point_distance(self):
        p1 = Point(0, 0)
        p2 = Point(3, 4)
        assert p1.distance_to(p2) == 5.0  # 3-4-5 triangle
    
    def test_point_to_tuple(self):
        p = Point(10, 20)
        assert p.to_tuple() == (10, 20)
    
    def test_point_iteration(self):
        p = Point(10, 20)
        x, y = p
        assert x == 10 and y == 20


class TestBoundingBox:
    """Tests for BoundingBox class"""
    
    def test_bbox_properties(self):
        bbox = BoundingBox(0, 0, 100, 50)
        assert bbox.width == 100
        assert bbox.height == 50
        assert bbox.area == 5000
        assert bbox.center == Point(50, 25)
    
    def test_bbox_intersects(self):
        b1 = BoundingBox(0, 0, 10, 10)
        b2 = BoundingBox(5, 5, 15, 15)
        b3 = BoundingBox(20, 20, 30, 30)
        
        assert b1.intersects(b2) == True
        assert b1.intersects(b3) == False
    
    def test_bbox_contains_point(self):
        bbox = BoundingBox(0, 0, 10, 10)
        assert bbox.contains_point(Point(5, 5)) == True
        assert bbox.contains_point(Point(15, 15)) == False


class TestPolygon:
    """Tests for Polygon class"""
    
    def test_rectangle_creation(self):
        """Test creating a simple rectangle"""
        rect = Polygon([
            Point(0, 0),
            Point(100, 0),
            Point(100, 50),
            Point(0, 50)
        ])
        
        assert rect.num_vertices == 4
        assert rect.has_holes == False
        assert rect.area == pytest.approx(5000, rel=1e-2)
    
    def test_rectangle_with_tuple_vertices(self):
        """Test creating polygon with tuple vertices"""
        rect = Polygon([(0, 0), (10, 0), (10, 5), (0, 5)])
        assert rect.area == pytest.approx(50, rel=1e-2)
    
    def test_polygon_bounds(self):
        """Test bounding box calculation"""
        rect = Polygon([(0, 0), (100, 0), (100, 50), (0, 50)])
        
        bounds = rect.bounds
        assert bounds.min_x == 0
        assert bounds.max_x == 100
        assert bounds.min_y == 0
        assert bounds.max_y == 50
        assert bounds.width == 100
        assert bounds.height == 50
    
    def test_polygon_centroid(self):
        """Test centroid calculation"""
        rect = Polygon([(0, 0), (100, 0), (100, 50), (0, 50)])
        centroid = rect.centroid
        
        assert centroid.x == pytest.approx(50, rel=1e-2)
        assert centroid.y == pytest.approx(25, rel=1e-2)
    
    def test_polygon_area(self):
        """Test area calculation for various shapes"""
        # Rectangle
        rect = Polygon([(0, 0), (10, 0), (10, 5), (0, 5)])
        assert rect.area == pytest.approx(50, rel=1e-2)
        
        # Triangle
        triangle = Polygon([(0, 0), (10, 0), (5, 10)])
        assert triangle.area == pytest.approx(50, rel=1e-2)
    
    def test_polygon_perimeter(self):
        """Test perimeter calculation"""
        rect = Polygon([(0, 0), (10, 0), (10, 5), (0, 5)])
        assert rect.perimeter == pytest.approx(30, rel=1e-2)
    
    def test_polygon_rotation(self):
        """Test polygon rotation"""
        rect = Polygon([(0, 0), (10, 0), (10, 5), (0, 5)])
        rotated = rect.rotate(90)
        
        # Area should be preserved
        assert rotated.area == pytest.approx(rect.area, rel=1e-2)
        
        # Bounds should change
        assert rotated.bounds.width == pytest.approx(5, rel=1e-1)
        assert rotated.bounds.height == pytest.approx(10, rel=1e-1)
    
    def test_polygon_translation(self):
        """Test polygon translation"""
        rect = Polygon([(0, 0), (10, 0), (10, 5), (0, 5)])
        translated = rect.translate(20, 30)
        
        # Area should be preserved
        assert translated.area == rect.area
        
        # Bounds should shift
        assert translated.bounds.min_x == 20
        assert translated.bounds.min_y == 30
    
    def test_polygon_scale(self):
        """Test polygon scaling"""
        rect = Polygon([(0, 0), (10, 0), (10, 5), (0, 5)])
        scaled = rect.scale(2.0)
        
        # Area should scale by factor²
        assert scaled.area == pytest.approx(rect.area * 4, rel=1e-2)
    
    def test_polygon_buffer(self):
        """Test polygon buffer (offset)"""
        rect = Polygon([(0, 0), (10, 0), (10, 5), (0, 5)])
        
        # Outward offset
        buffered = rect.buffer(1.0)
        assert buffered.area > rect.area
        
        # Inward offset
        shrunk = rect.buffer(-0.5)
        assert shrunk.area < rect.area
    
    def test_polygon_with_holes(self):
        """Test polygon with holes"""
        outer = [(0, 0), (100, 0), (100, 100), (0, 100)]
        hole = [(25, 25), (75, 25), (75, 75), (25, 75)]
        
        poly = Polygon(outer, holes=[hole])
        
        assert poly.has_holes == True
        assert poly.num_holes == 1
        
        # Area should be outer - hole
        expected_area = (100 * 100) - (50 * 50)
        assert poly.area == pytest.approx(expected_area, rel=1e-2)
    
    def test_polygon_convexity(self):
        """Test convexity metric"""
        # Rectangle is convex
        rect = Polygon([(0, 0), (10, 0), (10, 5), (0, 5)])
        assert rect.convexity == pytest.approx(1.0, rel=1e-2)
        
        # L-shape is concave
        l_shape = Polygon([
            (0, 0), (10, 0), (10, 5),
            (5, 5), (5, 10), (0, 10)
        ])
        assert l_shape.convexity < 1.0
    
    def test_polygon_intersects(self):
        """Test intersection detection"""
        rect1 = Polygon([(0, 0), (10, 0), (10, 10), (0, 10)])
        rect2 = Polygon([(5, 5), (15, 5), (15, 15), (5, 15)])
        rect3 = Polygon([(20, 20), (30, 20), (30, 30), (20, 30)])
        
        assert rect1.intersects(rect2) == True  # Overlap
        assert rect1.intersects(rect3) == False  # Separate
    
    def test_polygon_contains(self):
        """Test containment"""
        outer = Polygon([(0, 0), (100, 0), (100, 100), (0, 100)])
        inner = Polygon([(25, 25), (75, 25), (75, 75), (25, 75)])
        separate = Polygon([(200, 200), (300, 200), (300, 300), (200, 300)])
        
        assert outer.contains(inner) == True
        assert outer.contains(separate) == False
    
    def test_polygon_distance(self):
        """Test distance calculation"""
        rect1 = Polygon([(0, 0), (10, 0), (10, 10), (0, 10)])
        rect2 = Polygon([(20, 0), (30, 0), (30, 10), (20, 10)])
        
        distance = rect1.distance_to(rect2)
        assert distance == pytest.approx(10.0, rel=1e-2)
    
    def test_polygon_simplify(self):
        """Test polygon simplification"""
        # Create polygon with many points on straight line
        points = [(i, 0) for i in range(100)] + [(100, 10), (0, 10)]
        poly = Polygon(points)
        
        simplified = poly.simplify(tolerance=1.0)
        
        # Should have far fewer vertices
        assert simplified.num_vertices < poly.num_vertices
        # But similar area
        assert simplified.area == pytest.approx(poly.area, rel=0.1)


# Run tests if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v"])

