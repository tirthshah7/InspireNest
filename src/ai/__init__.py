"""
AI Module - Intelligent Learning Components

This module provides AI-enhanced nesting capabilities:
- Shape feature extraction for ML
- Learned placement policies
- Adaptive rotation optimization
- Strategy selection
- Failure prediction

Key Innovation: System learns from every job to improve over time
"""

from .features import ShapeFeatureExtractor, extract_features
# from .placement_policy import PlacementPolicy, RandomPolicy  # Building next
# from .rotation_optimizer import RotationOptimizer  # Day 5
# from .strategy_selector import StrategySelector  # Day 5
# from .failure_predictor import FailurePredictor  # Day 6

__all__ = [
    'ShapeFeatureExtractor',
    'extract_features',
]

__version__ = '1.0.0'

