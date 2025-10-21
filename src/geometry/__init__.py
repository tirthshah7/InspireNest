"""
Geometry Engine - Core geometric operations for intelligent nesting

This module provides robust geometric primitives and operations:
- Polygon representation and manipulation
- No-Fit Polygon (NFP) computation
- Manufacturing-aware geometric operations
- Offset and buffer operations
- Geometric validation and repair
"""

from .polygon import Polygon, Point, BoundingBox
from .nfp_manufacturing import ManufacturingAwareNFP, ManufacturingConstraints

# TODO Day 2: Add these modules
# from .nfp import compute_nfp, compute_inner_fit_polygon
# from .offset import offset_polygon, kerf_compensation
# from .validation import validate_polygon, fix_polygon
# from .transforms import rotate_polygon, translate_polygon, scale_polygon

__all__ = [
    'Polygon',
    'Point',
    'BoundingBox',
    'ManufacturingAwareNFP',
    'ManufacturingConstraints',
]

__version__ = '1.0.0'

