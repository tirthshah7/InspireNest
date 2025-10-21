"""
Unit Tests for AI Feature Extraction

Tests for shape feature extractor
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

import pytest
import numpy as np
from ai.features import ShapeFeatureExtractor, extract_features, ShapeFeatures
from geometry.polygon import Polygon, Point


class TestShapeFeatures:
    """Tests for ShapeFeatures dataclass"""
    
    def test_features_creation(self):
        features = ShapeFeatures(
            area=100, perimeter=40, num_vertices=4,
            bbox_width=10, bbox_height=10, bbox_area=100,
            aspect_ratio=1.0, convexity=1.0, compactness=0.8,
            has_holes=False, num_holes=0,
            area_bbox_ratio=1.0, perimeter_area_ratio=4.0,
            irregularity_score=0.0, concavity_depth=0.0,
            packing_difficulty=0.1
        )
        
        assert features.area == 100
        assert features.num_vertices == 4
    
    def test_features_to_dict(self):
        features = ShapeFeatures(
            area=100, perimeter=40, num_vertices=4,
            bbox_width=10, bbox_height=10, bbox_area=100,
            aspect_ratio=1.0, convexity=1.0, compactness=0.8,
            has_holes=False, num_holes=0,
            area_bbox_ratio=1.0, perimeter_area_ratio=4.0,
            irregularity_score=0.0, concavity_depth=0.0,
            packing_difficulty=0.1
        )
        
        d = features.to_dict()
        assert isinstance(d, dict)
        assert d['area'] == 100
        assert d['convexity'] == 1.0
    
    def test_features_to_array(self):
        features = ShapeFeatures(
            area=100, perimeter=40, num_vertices=4,
            bbox_width=10, bbox_height=10, bbox_area=100,
            aspect_ratio=1.0, convexity=1.0, compactness=0.8,
            has_holes=False, num_holes=0,
            area_bbox_ratio=1.0, perimeter_area_ratio=4.0,
            irregularity_score=0.0, concavity_depth=0.0,
            packing_difficulty=0.1
        )
        
        array = features.to_array()
        assert isinstance(array, np.ndarray)
        assert len(array) == 16
        assert array[0] == 100  # area


class TestShapeFeatureExtractor:
    """Tests for feature extractor"""
    
    def test_extractor_creation(self):
        extractor = ShapeFeatureExtractor()
        assert extractor.normalize == True
    
    def test_extract_rectangle_features(self):
        """Test extracting features from rectangle"""
        rect = Polygon([(0, 0), (100, 0), (100, 50), (0, 50)])
        features = extract_features(rect)
        
        assert features.area == pytest.approx(5000, rel=1e-2)
        assert features.num_vertices == 4
        assert features.convexity == pytest.approx(1.0, abs=0.01)  # Perfect convex
        assert features.has_holes == False
    
    def test_extract_circle_features(self):
        """Test extracting features from circle"""
        # Approximate circle
        from math import cos, sin, pi
        circle = Polygon([
            Point(50 + 30 * cos(theta * pi / 180), 
                  50 + 30 * sin(theta * pi / 180))
            for theta in range(0, 360, 10)
        ])
        
        features = extract_features(circle)
        
        assert features.convexity == pytest.approx(1.0, abs=0.01)  # Circle is convex
        assert features.compactness > 0.95  # Circle is very compact
        assert features.packing_difficulty < 0.2  # Circle is easy to pack
    
    def test_extract_l_shape_features(self):
        """Test extracting features from L-shape (concave)"""
        l_shape = Polygon([
            (0, 0), (100, 0), (100, 30),
            (30, 30), (30, 100), (0, 100)
        ])
        
        features = extract_features(l_shape)
        
        assert features.convexity < 1.0  # Concave
        assert features.packing_difficulty > 0.2  # Harder to pack than convex
        assert features.irregularity_score > 0  # Is irregular
    
    def test_extract_with_holes(self):
        """Test extracting features from shape with holes"""
        outer = [(0, 0), (100, 0), (100, 100), (0, 100)]
        hole = [(25, 25), (75, 25), (75, 75), (25, 75)]
        
        poly = Polygon(outer, holes=[hole])
        features = extract_features(poly)
        
        assert features.has_holes == True
        assert features.num_holes == 1
    
    def test_aspect_ratio_calculation(self):
        """Test aspect ratio calculation"""
        # Wide rectangle
        wide = Polygon([(0, 0), (100, 0), (100, 20), (0, 20)])
        features_wide = extract_features(wide)
        assert features_wide.aspect_ratio == pytest.approx(5.0, rel=0.1)
        
        # Tall rectangle
        tall = Polygon([(0, 0), (20, 0), (20, 100), (0, 100)])
        features_tall = extract_features(tall)
        assert features_tall.aspect_ratio == pytest.approx(0.2, rel=0.1)
        
        # Square
        square = Polygon([(0, 0), (50, 0), (50, 50), (0, 50)])
        features_square = extract_features(square)
        assert features_square.aspect_ratio == pytest.approx(1.0, rel=0.1)
    
    def test_packing_difficulty_ordering(self):
        """Test that packing difficulty correctly orders shapes"""
        # Easy: Square (convex, compact, aspect=1)
        square = Polygon([(0, 0), (50, 0), (50, 50), (0, 50)])
        
        # Medium: Moderate rectangle (convex, aspect=2)
        rect = Polygon([(0, 0), (100, 0), (100, 50), (0, 50)])
        
        # Hard: L-shape (concave)
        l_shape = Polygon([
            (0, 0), (100, 0), (100, 30),
            (30, 30), (30, 100), (0, 100)
        ])
        
        f_square = extract_features(square)
        f_rect = extract_features(rect)
        f_l = extract_features(l_shape)
        
        # Square should be easiest
        assert f_square.packing_difficulty < f_rect.packing_difficulty
        
        # L-shape should be harder than square (concave)
        assert f_l.packing_difficulty > f_square.packing_difficulty
    
    def test_batch_extraction(self):
        """Test extracting features from multiple shapes"""
        shapes = [
            Polygon([(0, 0), (10, 0), (10, 10), (0, 10)]),
            Polygon([(0, 0), (20, 0), (20, 20), (0, 20)]),
            Polygon([(0, 0), (30, 0), (30, 30), (0, 30)])
        ]
        
        extractor = ShapeFeatureExtractor()
        features = extractor.extract_batch(shapes)
        
        assert len(features) == 3
        assert all(isinstance(f, ShapeFeatures) for f in features)
        
        # Should have increasing areas
        assert features[0].area < features[1].area < features[2].area
    
    def test_feature_vector_consistency(self):
        """Test that feature vector is consistent"""
        shape = Polygon([(0, 0), (10, 0), (10, 5), (0, 5)])
        
        features1 = extract_features(shape)
        features2 = extract_features(shape)
        
        array1 = features1.to_array()
        array2 = features2.to_array()
        
        # Should be identical
        np.testing.assert_array_equal(array1, array2)
    
    def test_rotation_invariance(self):
        """Test that features are rotation invariant"""
        rect = Polygon([(0, 0), (100, 0), (100, 50), (0, 50)])
        rect_rotated = rect.rotate(45)
        
        f1 = extract_features(rect)
        f2 = extract_features(rect_rotated)
        
        # Area should be identical
        assert f1.area == pytest.approx(f2.area, rel=1e-2)
        
        # Convexity should be identical
        assert f1.convexity == pytest.approx(f2.convexity, abs=0.01)
        
        # Compactness should be identical
        assert f1.compactness == pytest.approx(f2.compactness, abs=0.01)


# Run tests if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v"])

