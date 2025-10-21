"""
AI-Powered Geometric Shape Analyzer

This module provides intelligent analysis of geometric shapes to understand:
- Shape complexity and packing difficulty
- Optimal orientation and placement strategies
- Geometric relationships and constraints
- Intelligent grouping and sequencing
"""

import numpy as np
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from geometry.polygon import Polygon, Point
from ai.features import ShapeFeatures, extract_features


class ShapeComplexity(Enum):
    """Shape complexity classification"""
    SIMPLE = "simple"          # Rectangles, circles
    MODERATE = "moderate"      # Polygons with few vertices
    COMPLEX = "complex"        # High vertex count, irregular shapes
    VERY_COMPLEX = "very_complex"  # Very irregular, many holes


class PackingStrategy(Enum):
    """AI-recommended packing strategy"""
    GRID_LIKE = "grid_like"           # Place in regular grid
    TIGHT_PACK = "tight_pack"         # Maximize density
    EDGE_ALIGN = "edge_align"         # Align with sheet edges
    NESTED = "nested"                 # Nest within other shapes
    SCATTERED = "scattered"           # Distribute across sheet


@dataclass
class GeometricInsight:
    """AI-generated insights about a shape"""
    complexity: ShapeComplexity
    packing_difficulty: float  # 0.0 (easy) to 1.0 (very hard)
    optimal_orientation: float  # Best rotation angle
    placement_strategy: PackingStrategy
    preferred_position: Tuple[float, float]  # Suggested starting position
    compatibility_score: float  # How well it fits with other shapes
    geometric_relationships: Dict[str, float]  # Relationships with other shapes


@dataclass
class PlacementIntelligence:
    """AI-powered placement recommendations"""
    shape_insights: List[GeometricInsight]
    optimal_sequence: List[int]  # Recommended placement order
    spatial_groupings: List[List[int]]  # Shapes that work well together
    conflict_predictions: List[Tuple[int, int, float]]  # Potential conflicts
    utilization_estimate: float  # Predicted utilization


class GeometricAnalyzer:
    """
    AI-powered geometric shape analyzer that understands shapes and provides
    intelligent placement recommendations.
    """
    
    def __init__(self):
        self.feature_extractor = ShapeFeatureExtractor()
        self.placement_model = PlacementIntelligenceModel()
    
    def analyze_shape(self, polygon: Polygon, context_shapes: List[Polygon] = None) -> GeometricInsight:
        """
        Analyze a single shape and provide AI insights
        
        Args:
            polygon: The shape to analyze
            context_shapes: Other shapes for relationship analysis
            
        Returns:
            GeometricInsight with AI recommendations
        """
        # Extract geometric features
        features = self.feature_extractor.extract_features(polygon)
        
        # Analyze complexity
        complexity = self._classify_complexity(features)
        
        # Calculate packing difficulty
        packing_difficulty = self._calculate_packing_difficulty(features, complexity)
        
        # Determine optimal orientation
        optimal_orientation = self._find_optimal_orientation(polygon, features)
        
        # Choose placement strategy
        placement_strategy = self._choose_placement_strategy(features, complexity)
        
        # Suggest starting position
        preferred_position = self._suggest_starting_position(polygon, features)
        
        # Calculate compatibility with other shapes
        compatibility_score = self._calculate_compatibility(polygon, context_shapes or [])
        
        # Analyze geometric relationships
        geometric_relationships = self._analyze_relationships(polygon, context_shapes or [])
        
        return GeometricInsight(
            complexity=complexity,
            packing_difficulty=packing_difficulty,
            optimal_orientation=optimal_orientation,
            placement_strategy=placement_strategy,
            preferred_position=preferred_position,
            compatibility_score=compatibility_score,
            geometric_relationships=geometric_relationships
        )
    
    def analyze_placement_intelligence(self, shapes: List[Polygon]) -> PlacementIntelligence:
        """
        Analyze all shapes and provide intelligent placement recommendations
        
        Args:
            shapes: List of shapes to analyze
            
        Returns:
            PlacementIntelligence with AI recommendations
        """
        # Analyze each shape
        shape_insights = []
        for shape in shapes:
            insight = self.analyze_shape(shape, shapes)
            shape_insights.append(insight)
        
        # Determine optimal placement sequence
        optimal_sequence = self._determine_optimal_sequence(shape_insights)
        
        # Find spatial groupings
        spatial_groupings = self._find_spatial_groupings(shape_insights)
        
        # Predict potential conflicts
        conflict_predictions = self._predict_conflicts(shape_insights)
        
        # Estimate utilization
        utilization_estimate = self._estimate_utilization(shape_insights)
        
        return PlacementIntelligence(
            shape_insights=shape_insights,
            optimal_sequence=optimal_sequence,
            spatial_groupings=spatial_groupings,
            conflict_predictions=conflict_predictions,
            utilization_estimate=utilization_estimate
        )
    
    def _classify_complexity(self, features: ShapeFeatures) -> ShapeComplexity:
        """Classify shape complexity based on features"""
        # Simple heuristics for complexity classification
        if features.num_vertices <= 4 and features.convexity > 0.95:
            return ShapeComplexity.SIMPLE
        elif features.num_vertices <= 8 and features.convexity > 0.8:
            return ShapeComplexity.MODERATE
        elif features.num_vertices <= 20 and features.convexity > 0.5:
            return ShapeComplexity.COMPLEX
        else:
            return ShapeComplexity.VERY_COMPLEX
    
    def _calculate_packing_difficulty(self, features: ShapeFeatures, complexity: ShapeComplexity) -> float:
        """Calculate how difficult this shape is to pack"""
        # Base difficulty from complexity
        base_difficulty = {
            ShapeComplexity.SIMPLE: 0.1,
            ShapeComplexity.MODERATE: 0.3,
            ShapeComplexity.COMPLEX: 0.6,
            ShapeComplexity.VERY_COMPLEX: 0.9
        }[complexity]
        
        # Adjust based on other factors
        aspect_ratio_factor = min(features.aspect_ratio, 1.0 / features.aspect_ratio) * 0.2
        hole_factor = features.num_holes * 0.1
        
        difficulty = base_difficulty + aspect_ratio_factor + hole_factor
        return min(difficulty, 1.0)
    
    def _find_optimal_orientation(self, polygon: Polygon, features: ShapeFeatures) -> float:
        """Find the optimal rotation angle for this shape"""
        # For now, use simple heuristics
        if features.aspect_ratio > 2.0:
            # Long shapes benefit from 0 or 90 degree rotation
            return 0.0 if features.aspect_ratio > 1.0 else 90.0
        elif features.convexity < 0.7:
            # Complex shapes might benefit from specific orientations
            return 45.0
        else:
            return 0.0
    
    def _choose_placement_strategy(self, features: ShapeFeatures, complexity: ShapeComplexity) -> PackingStrategy:
        """Choose the best placement strategy for this shape"""
        if complexity == ShapeComplexity.SIMPLE and features.aspect_ratio < 1.5:
            return PackingStrategy.GRID_LIKE
        elif features.convexity > 0.9:
            return PackingStrategy.TIGHT_PACK
        elif features.aspect_ratio > 3.0:
            return PackingStrategy.EDGE_ALIGN
        elif complexity in [ShapeComplexity.COMPLEX, ShapeComplexity.VERY_COMPLEX]:
            return PackingStrategy.NESTED
        else:
            return PackingStrategy.SCATTERED
    
    def _suggest_starting_position(self, polygon: Polygon, features: ShapeFeatures) -> Tuple[float, float]:
        """Suggest a starting position for placement"""
        # Simple heuristic: start from bottom-left for most shapes
        return (0.0, 0.0)
    
    def _calculate_compatibility(self, polygon: Polygon, context_shapes: List[Polygon]) -> float:
        """Calculate how compatible this shape is with others"""
        if not context_shapes:
            return 0.5
        
        # Simple compatibility based on size similarity
        areas = [shape.area for shape in context_shapes]
        avg_area = np.mean(areas)
        
        size_ratio = polygon.area / avg_area
        if 0.5 <= size_ratio <= 2.0:
            return 0.8
        elif 0.25 <= size_ratio <= 4.0:
            return 0.6
        else:
            return 0.3
    
    def _analyze_relationships(self, polygon: Polygon, context_shapes: List[Polygon]) -> Dict[str, float]:
        """Analyze geometric relationships with other shapes"""
        relationships = {}
        
        for i, other_shape in enumerate(context_shapes):
            if other_shape == polygon:
                continue
            
            # Calculate various relationship metrics
            area_ratio = polygon.area / other_shape.area
            size_similarity = 1.0 - abs(np.log(area_ratio))
            
            # Check if shapes could nest together
            nesting_potential = self._calculate_nesting_potential(polygon, other_shape)
            
            relationships[f"shape_{i}"] = {
                "size_similarity": size_similarity,
                "nesting_potential": nesting_potential,
                "area_ratio": area_ratio
            }
        
        return relationships
    
    def _calculate_nesting_potential(self, shape1: Polygon, shape2: Polygon) -> float:
        """Calculate how well two shapes could nest together"""
        # Simple heuristic based on area ratio and convexity
        area_ratio = min(shape1.area, shape2.area) / max(shape1.area, shape2.area)
        
        # Both shapes should be reasonably convex for good nesting
        convexity_factor = (shape1.convexity + shape2.convexity) / 2.0
        
        return area_ratio * convexity_factor
    
    def _determine_optimal_sequence(self, insights: List[GeometricInsight]) -> List[int]:
        """Determine the optimal placement sequence"""
        # Sort by packing difficulty (easy shapes first) and area (large shapes first)
        indexed_insights = [(i, insight) for i, insight in enumerate(insights)]
        
        # Multi-criteria sorting
        def sort_key(item):
            idx, insight = item
            # Lower difficulty first, then larger area first
            return (insight.packing_difficulty, -insights[idx].preferred_position[0])
        
        sorted_insights = sorted(indexed_insights, key=sort_key)
        return [idx for idx, _ in sorted_insights]
    
    def _find_spatial_groupings(self, insights: List[GeometricInsight]) -> List[List[int]]:
        """Find groups of shapes that work well together spatially"""
        # Simple grouping based on compatibility
        groups = []
        used = set()
        
        for i, insight in enumerate(insights):
            if i in used:
                continue
            
            group = [i]
            used.add(i)
            
            # Find compatible shapes
            for j, other_insight in enumerate(insights):
                if j in used:
                    continue
                
                if insight.compatibility_score > 0.7:
                    group.append(j)
                    used.add(j)
            
            if len(group) > 1:
                groups.append(group)
        
        return groups
    
    def _predict_conflicts(self, insights: List[GeometricInsight]) -> List[Tuple[int, int, float]]:
        """Predict potential placement conflicts"""
        conflicts = []
        
        for i, insight1 in enumerate(insights):
            for j, insight2 in enumerate(insights):
                if i >= j:
                    continue
                
                # Calculate conflict probability
                complexity_factor = (insight1.packing_difficulty + insight2.packing_difficulty) / 2.0
                strategy_conflict = insight1.placement_strategy == insight2.placement_strategy
                
                conflict_probability = complexity_factor * (0.8 if strategy_conflict else 0.3)
                
                if conflict_probability > 0.5:
                    conflicts.append((i, j, conflict_probability))
        
        return conflicts
    
    def _estimate_utilization(self, insights: List[GeometricInsight]) -> float:
        """Estimate potential utilization based on shape analysis"""
        # Simple estimation based on complexity and strategy
        total_area = sum(insight.compatibility_score for insight in insights)
        avg_complexity = np.mean([insight.packing_difficulty for insight in insights])
        
        # Estimate utilization based on complexity
        base_utilization = 0.8 - (avg_complexity * 0.4)
        return max(0.3, min(0.9, base_utilization))


class ShapeFeatureExtractor:
    """Extract detailed geometric features for AI analysis"""
    
    def extract_features(self, polygon: Polygon) -> ShapeFeatures:
        """Extract comprehensive features from a polygon"""
        return extract_features(polygon)


class PlacementIntelligenceModel:
    """AI model for placement intelligence (placeholder for future ML model)"""
    
    def __init__(self):
        self.model = None  # Placeholder for actual ML model
    
    def predict_placement(self, features: List[ShapeFeatures]) -> Dict:
        """Predict optimal placement (placeholder for ML model)"""
        # Placeholder implementation
        return {"confidence": 0.8, "strategy": "ai_optimized"}
