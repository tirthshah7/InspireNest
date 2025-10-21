"""
Manufacturing Module - Production-Ready Features

This module provides manufacturing-specific features:
- Common-edge cutting optimization
- Lead-in/lead-out generation
- Path planning and sequencing
- Cut time estimation
- Pierce optimization

Key Innovation: Manufacturing-aware nesting that considers
actual cutting process, not just geometry
"""

from .common_edge import CommonEdgeDetector, detect_common_edges
from .lead_in_out import LeadInOutGenerator, generate_lead_ins
# from .path_planner import PathPlanner  # Building next
# from .cut_estimator import CutTimeEstimator  # Building next

__all__ = [
    'CommonEdgeDetector',
    'detect_common_edges',
    'LeadInOutGenerator',
    'generate_lead_ins',
]

__version__ = '1.0.0'

