"""
Unit Tests for DXF Importer

Comprehensive tests for DXF import functionality
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

import pytest
import ezdxf
import tempfile
import os
from file_io.dxf_importer import DXFImporter, import_dxf_file, ImportStats
from geometry.polygon import Polygon, Point


class TestDXFImporter:
    """Tests for DXF importer"""
    
    def test_importer_creation(self):
        """Test creating DXF importer with default settings"""
        importer = DXFImporter()
        assert importer.spline_segments == 20
        assert importer.arc_segments == 16
        assert importer.min_segment_length == 0.1
    
    def test_importer_custom_settings(self):
        """Test creating DXF importer with custom settings"""
        importer = DXFImporter(
            spline_segments=50,
            arc_segments=32,
            min_segment_length=0.05
        )
        assert importer.spline_segments == 50
        assert importer.arc_segments == 32
        assert importer.min_segment_length == 0.05
    
    def test_import_empty_dxf(self):
        """Test importing empty DXF file"""
        # Create temporary empty DXF
        with tempfile.NamedTemporaryFile(mode='w', suffix='.dxf', delete=False) as f:
            doc = ezdxf.new('R2010')
            doc.saveas(f.name)
            temp_path = f.name
        
        try:
            polygons, stats = import_dxf_file(temp_path)
            assert len(polygons) == 0
            assert stats.total_entities == 0
        finally:
            os.unlink(temp_path)
    
    def test_import_single_circle(self):
        """Test importing DXF with single circle"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.dxf', delete=False) as f:
            doc = ezdxf.new('R2010')
            msp = doc.modelspace()
            msp.add_circle((50, 50), radius=25)
            doc.saveas(f.name)
            temp_path = f.name
        
        try:
            polygons, stats = import_dxf_file(temp_path)
            assert len(polygons) == 1
            assert stats.circles == 1
            
            circle = polygons[0]
            # Circle area = π * r²
            expected_area = 3.14159 * 25 * 25
            assert circle.area == pytest.approx(expected_area, rel=0.1)
        finally:
            os.unlink(temp_path)
    
    def test_import_single_rectangle(self):
        """Test importing DXF with single rectangle (LWPOLYLINE)"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.dxf', delete=False) as f:
            doc = ezdxf.new('R2010')
            msp = doc.modelspace()
            msp.add_lwpolyline([(0, 0), (100, 0), (100, 50), (0, 50), (0, 0)])
            doc.saveas(f.name)
            temp_path = f.name
        
        try:
            polygons, stats = import_dxf_file(temp_path)
            assert len(polygons) == 1
            assert stats.lwpolylines == 1
            
            rect = polygons[0]
            assert rect.area == pytest.approx(5000, rel=1e-2)
            assert rect.num_vertices == 5
        finally:
            os.unlink(temp_path)
    
    def test_import_arc(self):
        """Test importing DXF with arc"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.dxf', delete=False) as f:
            doc = ezdxf.new('R2010')
            msp = doc.modelspace()
            msp.add_arc(center=(50, 50), radius=25, start_angle=0, end_angle=90)
            doc.saveas(f.name)
            temp_path = f.name
        
        try:
            polygons, stats = import_dxf_file(temp_path)
            assert len(polygons) == 1
            assert stats.arcs == 1
            assert polygons[0].num_vertices > 4  # Arc approximated to multiple points
        finally:
            os.unlink(temp_path)
    
    def test_import_line(self):
        """Test importing DXF with single line"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.dxf', delete=False) as f:
            doc = ezdxf.new('R2010')
            msp = doc.modelspace()
            msp.add_line((0, 0), (100, 0))
            doc.saveas(f.name)
            temp_path = f.name
        
        try:
            polygons, stats = import_dxf_file(temp_path)
            assert stats.lines == 1
            # Single line won't create a polygon (need closed shape)
        finally:
            os.unlink(temp_path)
    
    def test_import_spline(self):
        """Test importing DXF with spline"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.dxf', delete=False) as f:
            doc = ezdxf.new('R2010')
            msp = doc.modelspace()
            control_points = [(0, 0), (50, 100), (100, 0)]
            msp.add_spline(control_points, degree=2)
            doc.saveas(f.name)
            temp_path = f.name
        
        try:
            polygons, stats = import_dxf_file(temp_path)
            assert stats.splines == 1
            # Spline should be approximated to multiple points
        finally:
            os.unlink(temp_path)
    
    def test_import_multiple_shapes(self):
        """Test importing DXF with multiple shapes"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.dxf', delete=False) as f:
            doc = ezdxf.new('R2010')
            msp = doc.modelspace()
            
            # Add 3 circles
            msp.add_circle((50, 50), radius=20)
            msp.add_circle((150, 50), radius=25)
            msp.add_circle((250, 50), radius=30)
            
            doc.saveas(f.name)
            temp_path = f.name
        
        try:
            polygons, stats = import_dxf_file(temp_path)
            assert len(polygons) == 3
            assert stats.circles == 3
        finally:
            os.unlink(temp_path)
    
    def test_import_mixed_entities(self):
        """Test importing DXF with mixed entity types"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.dxf', delete=False) as f:
            doc = ezdxf.new('R2010')
            msp = doc.modelspace()
            
            # Add different types
            msp.add_circle((50, 50), radius=20)
            msp.add_lwpolyline([(100, 0), (150, 0), (150, 50), (100, 50), (100, 0)])
            msp.add_arc(center=(200, 50), radius=30, start_angle=0, end_angle=180)
            
            doc.saveas(f.name)
            temp_path = f.name
        
        try:
            polygons, stats = import_dxf_file(temp_path)
            assert len(polygons) >= 2  # At least circle and rectangle
            assert stats.circles == 1
            assert stats.lwpolylines == 1
            assert stats.arcs == 1
        finally:
            os.unlink(temp_path)
    
    def test_tiny_part_import(self):
        """Test importing very small parts (precision test)"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.dxf', delete=False) as f:
            doc = ezdxf.new('R2010')
            msp = doc.modelspace()
            
            # 1mm x 1mm rectangle
            msp.add_lwpolyline([(0, 0), (1, 0), (1, 1), (0, 1), (0, 0)])
            
            doc.saveas(f.name)
            temp_path = f.name
        
        try:
            polygons, stats = import_dxf_file(temp_path)
            assert len(polygons) == 1
            assert polygons[0].area == pytest.approx(1.0, rel=0.1)
        finally:
            os.unlink(temp_path)
    
    def test_large_part_import(self):
        """Test importing very large parts (scale test)"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.dxf', delete=False) as f:
            doc = ezdxf.new('R2010')
            msp = doc.modelspace()
            
            # 5000mm x 3000mm rectangle
            msp.add_lwpolyline([(0, 0), (5000, 0), (5000, 3000), (0, 3000), (0, 0)])
            
            doc.saveas(f.name)
            temp_path = f.name
        
        try:
            polygons, stats = import_dxf_file(temp_path)
            assert len(polygons) == 1
            assert polygons[0].area == pytest.approx(15000000, rel=1e-2)
        finally:
            os.unlink(temp_path)
    
    def test_high_precision_coordinates(self):
        """Test importing coordinates with high precision"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.dxf', delete=False) as f:
            doc = ezdxf.new('R2010')
            msp = doc.modelspace()
            
            # Very precise coordinates
            msp.add_lwpolyline([
                (0.123456, 0.789012),
                (10.234567, 0.890123),
                (10.345678, 5.901234),
                (0.456789, 5.012345),
                (0.123456, 0.789012)
            ])
            
            doc.saveas(f.name)
            temp_path = f.name
        
        try:
            polygons, stats = import_dxf_file(temp_path)
            assert len(polygons) == 1
            # Check precision is preserved
            vertices = polygons[0].vertices
            assert vertices[0].x == pytest.approx(0.123456, abs=1e-4)
        finally:
            os.unlink(temp_path)
    
    def test_circle_approximation_quality(self):
        """Test that circle approximation is smooth"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.dxf', delete=False) as f:
            doc = ezdxf.new('R2010')
            msp = doc.modelspace()
            msp.add_circle((0, 0), radius=50)
            doc.saveas(f.name)
            temp_path = f.name
        
        try:
            polygons, stats = import_dxf_file(temp_path)
            circle = polygons[0]
            
            # Should have reasonable number of vertices (not too few, not too many)
            assert 16 <= circle.num_vertices <= 100
            
            # Area should be close to πr²
            expected_area = 3.14159 * 50 * 50
            assert circle.area == pytest.approx(expected_area, rel=0.05)
        finally:
            os.unlink(temp_path)
    
    def test_closed_vs_open_polyline(self):
        """Test handling of closed vs open polylines"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.dxf', delete=False) as f:
            doc = ezdxf.new('R2010')
            msp = doc.modelspace()
            
            # Closed polyline
            poly = msp.add_lwpolyline([(0, 0), (10, 0), (10, 10), (0, 10)])
            poly.close()
            
            doc.saveas(f.name)
            temp_path = f.name
        
        try:
            polygons, stats = import_dxf_file(temp_path)
            assert len(polygons) == 1
        finally:
            os.unlink(temp_path)
    
    def test_import_stats_accuracy(self):
        """Test that import stats are accurate"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.dxf', delete=False) as f:
            doc = ezdxf.new('R2010')
            msp = doc.modelspace()
            
            # Add known entities
            msp.add_circle((0, 0), radius=10)
            msp.add_circle((50, 0), radius=15)
            msp.add_lwpolyline([(100, 0), (150, 0), (150, 50), (100, 50), (100, 0)])
            msp.add_arc(center=(200, 25), radius=20, start_angle=0, end_angle=90)
            
            doc.saveas(f.name)
            temp_path = f.name
        
        try:
            polygons, stats = import_dxf_file(temp_path)
            
            assert stats.circles == 2
            assert stats.lwpolylines == 1
            assert stats.arcs == 1
            assert stats.total_entities == 4
            assert stats.shapes_created == len(polygons)
        finally:
            os.unlink(temp_path)
    
    def test_duplicate_point_removal(self):
        """Test that duplicate points are handled (ezdxf may keep them)"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.dxf', delete=False) as f:
            doc = ezdxf.new('R2010')
            msp = doc.modelspace()
            
            # Polyline with duplicate consecutive points
            msp.add_lwpolyline([
                (0, 0), (0, 0), (10, 0), (10, 0), (10, 10), 
                (10, 10), (0, 10), (0, 10), (0, 0)
            ])
            
            doc.saveas(f.name)
            temp_path = f.name
        
        try:
            importer = DXFImporter()
            polygons = importer.import_file(temp_path)
            
            if polygons:
                # Should create valid polygon despite duplicates
                assert polygons[0].is_valid()
                assert polygons[0].area == pytest.approx(100, rel=1e-2)
        finally:
            os.unlink(temp_path)
    
    def test_real_file_circles(self):
        """Test importing actual test file: circles.dxf"""
        filepath = "Test files/01_simple/circles.dxf"
        
        if Path(filepath).exists():
            polygons, stats = import_dxf_file(filepath)
            assert len(polygons) == 6  # Known to have 6 circles
            assert stats.circles == 6
            assert all(p.area > 0 for p in polygons)
    
    def test_real_file_gears_splines(self):
        """Test importing actual test file with splines: gears.dxf"""
        filepath = "Test files/02_moderate/gears.dxf"
        
        if Path(filepath).exists():
            polygons, stats = import_dxf_file(filepath)
            assert stats.splines > 0  # Has splines
            assert len(polygons) > 0  # Successfully created shapes
            
            # Verify splines were approximated
            for poly in polygons:
                assert poly.num_vertices > 3  # Spline approximated to multiple points
    
    def test_real_file_concave_shapes(self):
        """Test importing concave shapes (L, T, U, +)"""
        filepath = "Test files/04_stress_test/06_irregular_concave.dxf"
        
        if Path(filepath).exists():
            polygons, stats = import_dxf_file(filepath)
            assert len(polygons) == 4  # L, T, U, + shapes
            
            # All should be valid
            for poly in polygons:
                assert poly.is_valid()
                assert poly.area > 0
    
    def test_tolerance_setting(self):
        """Test that tolerance setting works"""
        importer1 = DXFImporter(tolerance=0.01)
        importer2 = DXFImporter(tolerance=1.0)
        
        assert importer1.tolerance == 0.01
        assert importer2.tolerance == 1.0
    
    def test_error_handling_invalid_file(self):
        """Test error handling for invalid file path"""
        with pytest.raises(Exception):
            import_dxf_file("nonexistent_file.dxf")
    
    def test_zero_area_shapes_filtered(self):
        """Test that zero-area shapes are filtered out"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.dxf', delete=False) as f:
            doc = ezdxf.new('R2010')
            msp = doc.modelspace()
            
            # Add valid shape
            msp.add_circle((50, 50), radius=20)
            
            # Add degenerate shape (single point repeated)
            msp.add_lwpolyline([(0, 0), (0, 0), (0, 0)])
            
            doc.saveas(f.name)
            temp_path = f.name
        
        try:
            polygons, stats = import_dxf_file(temp_path)
            # Should only have 1 valid polygon
            assert all(p.area > 0.1 for p in polygons)
        finally:
            os.unlink(temp_path)
    
    def test_negative_coordinates(self):
        """Test handling negative coordinates"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.dxf', delete=False) as f:
            doc = ezdxf.new('R2010')
            msp = doc.modelspace()
            
            msp.add_lwpolyline([
                (-50, -50), (50, -50), (50, 50), (-50, 50), (-50, -50)
            ])
            
            doc.saveas(f.name)
            temp_path = f.name
        
        try:
            polygons, stats = import_dxf_file(temp_path)
            assert len(polygons) == 1
            assert polygons[0].area == pytest.approx(10000, rel=1e-2)
        finally:
            os.unlink(temp_path)
    
    def test_part_id_generation(self):
        """Test that unique part IDs are generated"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.dxf', delete=False) as f:
            doc = ezdxf.new('R2010')
            msp = doc.modelspace()
            
            msp.add_circle((0, 0), radius=10)
            msp.add_circle((50, 0), radius=10)
            
            doc.saveas(f.name)
            temp_path = f.name
        
        try:
            polygons, stats = import_dxf_file(temp_path)
            
            # Each should have unique ID
            ids = [p.part_id for p in polygons]
            assert len(ids) == len(set(ids))  # All unique
        finally:
            os.unlink(temp_path)


class TestImportStats:
    """Tests for ImportStats dataclass"""
    
    def test_stats_creation(self):
        stats = ImportStats()
        assert stats.total_entities == 0
        assert stats.shapes_created == 0
        assert stats.errors == []
    
    def test_stats_string_representation(self):
        stats = ImportStats(
            total_entities=10,
            circles=3,
            lwpolylines=2,
            shapes_created=5
        )
        
        stats_str = str(stats)
        assert "Total Entities: 10" in stats_str
        assert "Circles: 3" in stats_str
        assert "Shapes Created: 5" in stats_str


# Run tests if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v"])

