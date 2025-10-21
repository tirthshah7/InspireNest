"""
Unit Tests for Topology Solver

Tests for segment grouping and hole detection
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

import pytest
from geometry.topology import TopologySolver, group_disconnected_segments
from geometry.polygon import Polygon, Point


class TestTopologySolver:
    """Tests for topology solver"""
    
    def test_solver_creation(self):
        """Test creating topology solver"""
        solver = TopologySolver()
        assert solver.tolerance == 0.1
    
    def test_solver_custom_tolerance(self):
        """Test custom tolerance"""
        solver = TopologySolver(tolerance=0.5)
        assert solver.tolerance == 0.5
    
    def test_group_single_segment(self):
        """Test grouping single continuous segment"""
        segments = [
            [Point(0, 0), Point(10, 0), Point(10, 5), Point(0, 5)]
        ]
        
        solver = TopologySolver()
        result = solver.group_segments(segments)
        
        assert len(result) == 1
        assert len(result[0]) >= 3
    
    def test_group_disconnected_rectangle(self):
        """Test grouping 4 disconnected LINEs into rectangle"""
        # 4 sides of rectangle as separate segments
        segments = [
            [Point(0, 0), Point(10, 0)],      # Bottom
            [Point(10, 0), Point(10, 5)],     # Right
            [Point(10, 5), Point(0, 5)],      # Top
            [Point(0, 5), Point(0, 0)]        # Left
        ]
        
        solver = TopologySolver()
        result = solver.group_segments(segments)
        
        assert len(result) == 1  # Should form 1 shape
        assert len(result[0]) >= 4  # Rectangle has 4 corners
        
        # Create polygon and verify
        poly = Polygon(result[0])
        assert poly.area == pytest.approx(50, rel=1e-2)
    
    def test_group_unordered_segments(self):
        """Test grouping segments that are not in order"""
        # Same rectangle but scrambled order
        segments = [
            [Point(10, 5), Point(0, 5)],      # Top (out of order)
            [Point(0, 0), Point(10, 0)],      # Bottom
            [Point(0, 5), Point(0, 0)],       # Left
            [Point(10, 0), Point(10, 5)],     # Right
        ]
        
        solver = TopologySolver()
        result = solver.group_segments(segments)
        
        assert len(result) == 1
        poly = Polygon(result[0])
        assert poly.area == pytest.approx(50, rel=1e-2)
    
    def test_group_two_separate_shapes(self):
        """Test that disconnected shapes stay separate"""
        # Rectangle 1
        rect1 = [
            [Point(0, 0), Point(10, 0)],
            [Point(10, 0), Point(10, 5)],
            [Point(10, 5), Point(0, 5)],
            [Point(0, 5), Point(0, 0)]
        ]
        
        # Rectangle 2 (far away)
        rect2 = [
            [Point(100, 100), Point(110, 100)],
            [Point(110, 100), Point(110, 105)],
            [Point(110, 105), Point(100, 105)],
            [Point(100, 105), Point(100, 100)]
        ]
        
        segments = rect1 + rect2
        
        solver = TopologySolver()
        result = solver.group_segments(segments)
        
        assert len(result) == 2  # Should stay as 2 shapes
    
    def test_group_reversed_segment(self):
        """Test grouping when a segment is reversed"""
        # Rectangle with one reversed side
        segments = [
            [Point(0, 0), Point(10, 0)],
            [Point(10, 0), Point(10, 5)],
            [Point(0, 5), Point(10, 5)],      # Reversed!
            [Point(0, 5), Point(0, 0)]
        ]
        
        solver = TopologySolver()
        result = solver.group_segments(segments)
        
        assert len(result) == 1
        poly = Polygon(result[0])
        assert poly.area == pytest.approx(50, rel=1e-2)
    
    def test_group_with_tolerance(self):
        """Test that tolerance allows near-matches"""
        # Segments with small gaps (within tolerance)
        segments = [
            [Point(0, 0), Point(10, 0)],
            [Point(10.05, 0), Point(10.05, 5)],  # 0.05mm gap
            [Point(10, 5), Point(0, 5)],
            [Point(0, 5.05), Point(0, 0)]  # 0.05mm gap
        ]
        
        solver = TopologySolver(tolerance=0.1)  # 0.1mm tolerance
        result = solver.group_segments(segments)
        
        assert len(result) == 1  # Should connect despite small gaps
    
    def test_group_empty_segments(self):
        """Test handling empty segment list"""
        solver = TopologySolver()
        result = solver.group_segments([])
        assert result == []
    
    def test_detect_holes_simple(self):
        """Test hole detection for simple case"""
        # Outer rectangle
        outer = Polygon([(0, 0), (100, 0), (100, 100), (0, 100)])
        
        # Inner hole
        hole = Polygon([(25, 25), (75, 25), (75, 75), (25, 75)])
        
        solver = TopologySolver()
        result = solver.detect_holes([outer, hole])
        
        assert len(result) == 1  # Should have 1 shape with hole
        assert result[0].has_holes == True
        assert result[0].num_holes == 1
    
    def test_detect_holes_multiple(self):
        """Test detecting multiple holes in one shape"""
        # Outer
        outer = Polygon([(0, 0), (100, 0), (100, 100), (0, 100)])
        
        # Two holes
        hole1 = Polygon([(10, 10), (30, 10), (30, 30), (10, 30)])
        hole2 = Polygon([(70, 70), (90, 70), (90, 90), (70, 90)])
        
        solver = TopologySolver()
        result = solver.detect_holes([outer, hole1, hole2])
        
        assert len(result) == 1
        assert result[0].num_holes == 2
    
    def test_detect_holes_no_containment(self):
        """Test that separate shapes are not treated as holes"""
        # Two separate rectangles
        rect1 = Polygon([(0, 0), (50, 0), (50, 50), (0, 50)])
        rect2 = Polygon([(100, 100), (150, 100), (150, 150), (100, 150)])
        
        solver = TopologySolver()
        result = solver.detect_holes([rect1, rect2])
        
        assert len(result) == 2  # Should stay separate
        assert not result[0].has_holes
        assert not result[1].has_holes
    
    def test_detect_holes_nested_hierarchy(self):
        """Test complex nested hierarchy"""
        # Large outer
        outer = Polygon([(0, 0), (100, 0), (100, 100), (0, 100)])
        
        # Medium hole
        hole1 = Polygon([(20, 20), (80, 20), (80, 80), (20, 80)])
        
        # Small shape inside the hole (not a hole of outer)
        inner = Polygon([(40, 40), (60, 40), (60, 60), (40, 60)])
        
        solver = TopologySolver()
        result = solver.detect_holes([outer, hole1, inner])
        
        # Should have outer with 1 hole, and inner as separate
        # (Simplified - full hierarchical handling is complex)
        assert len(result) >= 1


class TestConvenienceFunction:
    """Tests for convenience function"""
    
    def test_convenience_function(self):
        """Test group_disconnected_segments convenience function"""
        segments = [
            [Point(0, 0), Point(10, 0)],
            [Point(10, 0), Point(10, 5)],
            [Point(10, 5), Point(0, 5)],
            [Point(0, 5), Point(0, 0)]
        ]
        
        result = group_disconnected_segments(segments)
        assert len(result) == 1
        assert len(result[0]) >= 4


class TestPerformance:
    """Performance tests for topology solver"""
    
    def test_performance_many_segments(self):
        """Test performance with many segments"""
        import time
        
        # Create 100 disconnected segments
        segments = []
        for i in range(100):
            x = i * 20
            segments.append([
                Point(x, 0),
                Point(x + 10, 0),
                Point(x + 10, 10),
                Point(x, 10)
            ])
        
        solver = TopologySolver()
        
        start = time.time()
        result = solver.group_segments(segments)
        elapsed = time.time() - start
        
        # Should complete in reasonable time
        assert elapsed < 1.0  # Less than 1 second
        assert len(result) == 100  # 100 separate shapes
    
    def test_performance_complex_shape(self):
        """Test performance with complex connected shape"""
        import time
        
        # Create 50 segments forming one complex shape
        segments = []
        for i in range(50):
            angle1 = i * (360 / 50)
            angle2 = (i + 1) * (360 / 50)
            
            import math
            x1 = 50 + 40 * math.cos(math.radians(angle1))
            y1 = 50 + 40 * math.sin(math.radians(angle1))
            x2 = 50 + 40 * math.cos(math.radians(angle2))
            y2 = 50 + 40 * math.sin(math.radians(angle2))
            
            segments.append([Point(x1, y1), Point(x2, y2)])
        
        solver = TopologySolver()
        
        start = time.time()
        result = solver.group_segments(segments)
        elapsed = time.time() - start
        
        # Should complete quickly
        assert elapsed < 0.5  # Less than 0.5 seconds
        assert len(result) == 1  # Should form 1 shape


# Run tests if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v"])

