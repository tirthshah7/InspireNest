"""
Shape Feature Extraction for Machine Learning

Extracts meaningful features from shapes for AI/ML algorithms:
- Geometric features (area, perimeter, convexity)
- Topological features (holes, concavity)
- Complexity features (vertex count, irregularity)
- Packing difficulty features (aspect ratio, compactness)

These features enable:
- Learned placement policies
- Difficulty prediction
- Strategy selection
- Performance estimation
"""

from typing import Dict, List, Any
from dataclasses import dataclass, asdict
import numpy as np
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from geometry.polygon import Polygon


@dataclass
class ShapeFeatures:
    """
    Complete feature set for a shape
    
    Features are normalized to 0-1 range where possible
    for machine learning compatibility
    """
    # Basic geometric features
    area: float
    perimeter: float
    num_vertices: int
    
    # Bounding box features
    bbox_width: float
    bbox_height: float
    bbox_area: float
    aspect_ratio: float  # width / height
    
    # Shape characteristics
    convexity: float  # 0-1, 1 = perfectly convex
    compactness: float  # 0-1, 1 = circle
    
    # Topology
    has_holes: bool
    num_holes: int
    
    # Derived features
    area_bbox_ratio: float  # area / bbox_area (packing efficiency)
    perimeter_area_ratio: float  # perimeter / sqrt(area)
    
    # Complexity indicators
    irregularity_score: float  # How irregular vs convex hull
    concavity_depth: float  # How deep are concave regions
    
    # Packing difficulty (0-1, higher = harder)
    packing_difficulty: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)
    
    def to_array(self) -> np.ndarray:
        """Convert to numpy array for ML"""
        return np.array([
            self.area,
            self.perimeter,
            float(self.num_vertices),
            self.bbox_width,
            self.bbox_height,
            self.bbox_area,
            self.aspect_ratio,
            self.convexity,
            self.compactness,
            float(self.has_holes),
            float(self.num_holes),
            self.area_bbox_ratio,
            self.perimeter_area_ratio,
            self.irregularity_score,
            self.concavity_depth,
            self.packing_difficulty
        ])
    
    @property
    def feature_dim(self) -> int:
        """Dimensionality of feature vector"""
        return 16


class ShapeFeatureExtractor:
    """
    Extract features from shapes for ML/AI
    
    Features are designed to be:
    - Rotation invariant (same features regardless of orientation)
    - Scale normalized (comparable across sizes)
    - Meaningful for packing (predict difficulty, guide placement)
    """
    
    def __init__(self, normalize: bool = True):
        """
        Initialize feature extractor
        
        Args:
            normalize: Whether to normalize features to similar scales
        """
        self.normalize = normalize
    
    def extract(self, shape: Polygon) -> ShapeFeatures:
        """
        Extract all features from a shape
        
        Args:
            shape: Polygon to extract features from
        
        Returns:
            ShapeFeatures object with all computed features
        """
        # Basic geometric features
        area = shape.area
        perimeter = shape.perimeter
        num_vertices = shape.num_vertices
        
        # Bounding box features
        bounds = shape.bounds
        bbox_width = bounds.width
        bbox_height = bounds.height
        bbox_area = bounds.area
        aspect_ratio = shape.aspect_ratio
        
        # Shape characteristics
        convexity = shape.convexity
        compactness = shape.compactness
        
        # Topology
        has_holes = shape.has_holes
        num_holes = shape.num_holes
        
        # Derived features
        area_bbox_ratio = area / max(bbox_area, 1e-6)  # How efficiently does bbox contain shape
        perimeter_area_ratio = perimeter / max(np.sqrt(area), 1e-6)
        
        # Irregularity (1 - convexity, but with more nuance)
        irregularity_score = 1.0 - convexity
        
        # Concavity depth (estimated from convex hull difference)
        hull_area = shape.convex_hull().area
        concavity_depth = (hull_area - area) / max(hull_area, 1e-6)
        
        # Packing difficulty score (0-1, higher = harder)
        packing_difficulty = self._estimate_packing_difficulty(
            convexity, compactness, aspect_ratio, num_vertices, concavity_depth
        )
        
        return ShapeFeatures(
            area=area,
            perimeter=perimeter,
            num_vertices=num_vertices,
            bbox_width=bbox_width,
            bbox_height=bbox_height,
            bbox_area=bbox_area,
            aspect_ratio=aspect_ratio,
            convexity=convexity,
            compactness=compactness,
            has_holes=has_holes,
            num_holes=num_holes,
            area_bbox_ratio=area_bbox_ratio,
            perimeter_area_ratio=perimeter_area_ratio,
            irregularity_score=irregularity_score,
            concavity_depth=concavity_depth,
            packing_difficulty=packing_difficulty
        )
    
    def extract_batch(self, shapes: List[Polygon]) -> List[ShapeFeatures]:
        """Extract features from multiple shapes"""
        return [self.extract(shape) for shape in shapes]
    
    def _estimate_packing_difficulty(
        self,
        convexity: float,
        compactness: float,
        aspect_ratio: float,
        num_vertices: int,
        concavity_depth: float
    ) -> float:
        """
        Estimate how difficult a shape is to pack (0-1)
        
        Factors:
        - Low convexity → harder (concave shapes)
        - Low compactness → harder (elongated shapes)
        - Extreme aspect ratio → harder (very wide or tall)
        - Many vertices → harder (complex outlines)
        - Deep concavity → harder (complex fitting)
        
        Returns: 0 (easy) to 1 (very hard)
        """
        difficulty = 0.0
        
        # Convexity penalty (concave shapes are harder)
        difficulty += (1.0 - convexity) * 0.3
        
        # Compactness penalty (elongated shapes are harder)
        difficulty += (1.0 - compactness) * 0.2
        
        # Aspect ratio penalty (extreme ratios are harder)
        # Ideal aspect ratio is near 1.0
        aspect_penalty = abs(np.log(aspect_ratio)) / 2.0  # Log scale
        difficulty += min(aspect_penalty, 1.0) * 0.2
        
        # Vertex count penalty (complex shapes are harder)
        vertex_penalty = min(num_vertices / 50.0, 1.0)  # Normalize to 0-1
        difficulty += vertex_penalty * 0.15
        
        # Concavity depth penalty
        difficulty += concavity_depth * 0.15
        
        # Clamp to 0-1
        return min(max(difficulty, 0.0), 1.0)


# Convenience function
def extract_features(shape: Polygon) -> ShapeFeatures:
    """
    Convenience function to extract features from a shape
    
    Example:
        polygon = Polygon([(0,0), (10,0), (10,5), (0,5)])
        features = extract_features(polygon)
        
        print(f"Area: {features.area}")
        print(f"Convexity: {features.convexity}")
        print(f"Packing difficulty: {features.packing_difficulty}")
    """
    extractor = ShapeFeatureExtractor()
    return extractor.extract(shape)

