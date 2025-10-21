"""
Multi-Objective Scoring Framework - INNOVATION!

Traditional nesting: Optimize ONLY material utilization
Our approach: Optimize ALL manufacturing objectives simultaneously

Objectives:
1. Material utilization (maximize)
2. Cut path length (minimize)
3. Pierce count (minimize)
4. Machine time (minimize)
5. Thermal distortion risk (minimize)
6. Total cost (minimize)
7. Remnant value (maximize)

Uses Pareto optimization to find trade-off solutions
"""

from .multi_objective import MultiObjectiveScorer, ScoringWeights, NestingSolution

# TODO Day 2-3: Add these modules
# from .objectives import (...)
# from .pareto import ParetoFront, dominates

__all__ = [
    'MultiObjectiveScorer',
    'ScoringWeights',
    'NestingSolution',
]

