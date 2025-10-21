"""
Multi-Objective Scorer - Simultaneous optimization of multiple goals

This is a KEY INNOVATION: Instead of optimizing just one thing (utilization),
we optimize EVERYTHING that matters for manufacturing profit.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
import numpy as np


@dataclass
class ScoringWeights:
    """
    Weights for different objectives
    
    All weights should sum to 1.0
    Default weights prioritize profitability
    """
    utilization: float = 0.35      # Material waste is expensive
    cut_length: float = 0.20       # Machine time costs money
    pierce_count: float = 0.15     # Pierces are slow
    machine_time: float = 0.15     # Total time = labor cost
    thermal_risk: float = 0.05     # Quality/rework cost
    remnant_value: float = 0.05    # Salvage value
    total_cost: float = 0.05       # Overall cost (composite)
    
    def __post_init__(self):
        """Validate weights sum to 1.0"""
        total = (
            self.utilization +
            self.cut_length +
            self.pierce_count +
            self.machine_time +
            self.thermal_risk +
            self.remnant_value +
            self.total_cost
        )
        if abs(total - 1.0) > 0.01:
            raise ValueError(f"Weights must sum to 1.0, got {total}")
    
    @classmethod
    def maximize_utilization(cls) -> 'ScoringWeights':
        """Preset: Maximize material usage (traditional approach)"""
        return cls(
            utilization=0.8,
            cut_length=0.05,
            pierce_count=0.05,
            machine_time=0.05,
            thermal_risk=0.025,
            remnant_value=0.025,
            total_cost=0.0
        )
    
    @classmethod
    def minimize_time(cls) -> 'ScoringWeights':
        """Preset: Minimize total production time"""
        return cls(
            utilization=0.2,
            cut_length=0.3,
            pierce_count=0.2,
            machine_time=0.25,
            thermal_risk=0.025,
            remnant_value=0.0,
            total_cost=0.025
        )
    
    @classmethod
    def maximize_profit(cls) -> 'ScoringWeights':
        """Preset: Maximize profit (balanced approach)"""
        return cls(
            utilization=0.30,
            cut_length=0.20,
            pierce_count=0.15,
            machine_time=0.20,
            thermal_risk=0.05,
            remnant_value=0.05,
            total_cost=0.05
        )


@dataclass
class NestingSolution:
    """
    Represents a complete nesting solution
    
    This includes all placed parts and their positions,
    plus computed metrics for scoring.
    """
    placed_parts: List[Any] = field(default_factory=list)  # List of placed polygons
    failed_parts: List[Any] = field(default_factory=list)  # Parts that didn't fit
    
    # Geometric metrics
    sheet_width: float = 0.0
    sheet_height: float = 0.0
    used_area: float = 0.0
    total_part_area: float = 0.0
    
    # Manufacturing metrics
    cut_path_length: float = 0.0
    pierce_count: int = 0
    estimated_cut_time: float = 0.0      # seconds
    estimated_rapid_time: float = 0.0    # seconds
    estimated_pierce_time: float = 0.0   # seconds
    
    # Cost metrics
    material_cost: float = 0.0
    machine_time_cost: float = 0.0
    total_cost: float = 0.0
    
    # Quality metrics
    thermal_risk_score: float = 0.0      # 0-1, higher = more risk
    remnant_value_score: float = 0.0     # 0-1, higher = better remnants
    
    # Computed scores (cached)
    objective_scores: Dict[str, float] = field(default_factory=dict)
    weighted_score: float = 0.0
    
    @property
    def utilization(self) -> float:
        """Material utilization percentage"""
        sheet_area = self.sheet_width * self.sheet_height
        if sheet_area == 0:
            return 0.0
        return (self.used_area / sheet_area) * 100.0
    
    @property
    def total_machine_time(self) -> float:
        """Total machine time in seconds"""
        return (
            self.estimated_cut_time +
            self.estimated_rapid_time +
            self.estimated_pierce_time
        )
    
    @property
    def parts_placed_ratio(self) -> float:
        """Ratio of placed parts to total parts"""
        total_parts = len(self.placed_parts) + len(self.failed_parts)
        if total_parts == 0:
            return 0.0
        return len(self.placed_parts) / total_parts
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization"""
        return {
            'num_placed_parts': len(self.placed_parts),
            'num_failed_parts': len(self.failed_parts),
            'utilization_percent': self.utilization,
            'cut_path_length_mm': self.cut_path_length,
            'pierce_count': self.pierce_count,
            'total_machine_time_sec': self.total_machine_time,
            'total_cost': self.total_cost,
            'thermal_risk_score': self.thermal_risk_score,
            'remnant_value_score': self.remnant_value_score,
            'weighted_score': self.weighted_score,
            'objective_scores': self.objective_scores
        }


class MultiObjectiveScorer:
    """
    Multi-objective scoring system
    
    INNOVATION: Scores layouts based on ALL manufacturing objectives,
    not just material utilization.
    """
    
    def __init__(self, weights: Optional[ScoringWeights] = None):
        """
        Initialize scorer with custom weights
        
        Args:
            weights: Custom weights (default: balanced profit maximization)
        """
        self.weights = weights or ScoringWeights.maximize_profit()
    
    def score(self, solution: NestingSolution) -> float:
        """
        Compute overall weighted score for a solution
        
        Returns: Score between 0-100 (higher is better)
        """
        # Compute individual objective scores
        scores = {}
        
        # 1. Utilization (0-100, higher is better)
        scores['utilization'] = self._score_utilization(solution)
        
        # 2. Cut length (0-100, higher is better = shorter cuts)
        scores['cut_length'] = self._score_cut_length(solution)
        
        # 3. Pierce count (0-100, higher is better = fewer pierces)
        scores['pierce_count'] = self._score_pierce_count(solution)
        
        # 4. Machine time (0-100, higher is better = less time)
        scores['machine_time'] = self._score_machine_time(solution)
        
        # 5. Thermal risk (0-100, higher is better = less risk)
        scores['thermal_risk'] = 100.0 * (1.0 - solution.thermal_risk_score)
        
        # 6. Remnant value (0-100, higher is better)
        scores['remnant_value'] = 100.0 * solution.remnant_value_score
        
        # 7. Total cost (0-100, higher is better = lower cost)
        scores['total_cost'] = self._score_total_cost(solution)
        
        # Store individual scores
        solution.objective_scores = scores
        
        # Compute weighted sum
        weighted_score = (
            scores['utilization'] * self.weights.utilization +
            scores['cut_length'] * self.weights.cut_length +
            scores['pierce_count'] * self.weights.pierce_count +
            scores['machine_time'] * self.weights.machine_time +
            scores['thermal_risk'] * self.weights.thermal_risk +
            scores['remnant_value'] * self.weights.remnant_value +
            scores['total_cost'] * self.weights.total_cost
        )
        
        solution.weighted_score = weighted_score
        return weighted_score
    
    def _score_utilization(self, solution: NestingSolution) -> float:
        """
        Score material utilization
        
        Target: 80-90% utilization is excellent
        Returns: 0-100
        """
        utilization = solution.utilization
        
        # Sigmoid curve: 80% = 90 points, 85% = 95 points, 90% = 98 points
        # Above 90% = diminishing returns
        if utilization >= 90:
            return 98.0 + (utilization - 90) * 0.2  # Cap at 100
        elif utilization >= 80:
            return 90.0 + (utilization - 80) * 0.8
        elif utilization >= 70:
            return 70.0 + (utilization - 70) * 2.0
        elif utilization >= 60:
            return 40.0 + (utilization - 60) * 3.0
        else:
            return utilization * 0.67  # Linear below 60%
    
    def _score_cut_length(self, solution: NestingSolution) -> float:
        """
        Score cut path length
        
        Shorter cuts = higher score
        Normalized against theoretical minimum (perimeter of all parts)
        """
        if solution.total_part_area == 0:
            return 0.0
        
        # Estimate theoretical minimum (perimeter of all parts)
        # Assume parts are roughly square: perimeter ≈ 4 * sqrt(area)
        theoretical_min = 4.0 * np.sqrt(solution.total_part_area)
        
        # Actual cut length should be reasonable multiple of this
        # Common line cutting can reduce length significantly
        ratio = solution.cut_path_length / max(theoretical_min, 1.0)
        
        # Good ratio is 1.5-2.5x theoretical minimum
        if ratio <= 1.5:
            return 100.0  # Exceptional (common cutting working well)
        elif ratio <= 2.5:
            return 100.0 - (ratio - 1.5) * 40.0  # 100 down to 60
        elif ratio <= 4.0:
            return 60.0 - (ratio - 2.5) * 20.0   # 60 down to 30
        else:
            return max(0.0, 30.0 - (ratio - 4.0) * 10.0)
    
    def _score_pierce_count(self, solution: NestingSolution) -> float:
        """
        Score pierce count
        
        Fewer pierces = higher score
        Each pierce adds ~0.5-1.0 seconds
        """
        num_parts = len(solution.placed_parts)
        if num_parts == 0:
            return 0.0
        
        # Minimum pierces = number of parts (one pierce per part)
        # Each hole adds one pierce
        min_pierces = num_parts
        actual_pierces = solution.pierce_count
        
        if actual_pierces <= min_pierces:
            return 100.0  # Perfect (no extra pierces)
        
        extra_pierces = actual_pierces - min_pierces
        
        # Penalize extra pierces
        # Every extra pierce = -5 points
        return max(0.0, 100.0 - extra_pierces * 5.0)
    
    def _score_machine_time(self, solution: NestingSolution) -> float:
        """
        Score total machine time
        
        Less time = higher score
        Time = cost
        """
        total_time = solution.total_machine_time
        
        if total_time == 0:
            return 0.0
        
        # Rough target: 1 minute per 1000 mm² of parts
        expected_time = solution.total_part_area / 1000.0 * 60.0  # seconds
        
        ratio = total_time / max(expected_time, 1.0)
        
        if ratio <= 0.8:
            return 100.0  # Very fast
        elif ratio <= 1.2:
            return 100.0 - (ratio - 0.8) * 125.0  # 100 down to 50
        else:
            return max(0.0, 50.0 - (ratio - 1.2) * 25.0)
    
    def _score_total_cost(self, solution: NestingSolution) -> float:
        """
        Score total cost
        
        Lower cost = higher score
        """
        if solution.total_cost == 0:
            return 50.0  # Neutral if cost not computed
        
        # Cost per square mm of parts
        cost_per_area = solution.total_cost / max(solution.total_part_area, 1.0)
        
        # Target: $0.001-0.002 per mm² ($1-2 per 1000 mm²)
        if cost_per_area <= 0.001:
            return 100.0
        elif cost_per_area <= 0.002:
            return 100.0 - (cost_per_area - 0.001) * 50000.0
        else:
            return max(0.0, 50.0 - (cost_per_area - 0.002) * 25000.0)
    
    def compare(self, solution_a: NestingSolution, solution_b: NestingSolution) -> int:
        """
        Compare two solutions
        
        Returns:
            1 if solution_a is better
            -1 if solution_b is better
            0 if equal
        """
        score_a = self.score(solution_a)
        score_b = self.score(solution_b)
        
        if abs(score_a - score_b) < 0.1:
            return 0
        return 1 if score_a > score_b else -1
    
    def explain_score(self, solution: NestingSolution) -> str:
        """
        Generate human-readable explanation of score
        
        Useful for debugging and user feedback
        """
        self.score(solution)  # Ensure scores are computed
        
        lines = [
            "═══ Multi-Objective Score Breakdown ═══",
            f"Overall Score: {solution.weighted_score:.1f}/100",
            "",
            "Individual Objectives:",
        ]
        
        for obj_name, score in solution.objective_scores.items():
            weight = getattr(self.weights, obj_name)
            contribution = score * weight
            lines.append(f"  {obj_name:15s}: {score:5.1f}/100 (weight {weight:.2f}) → {contribution:5.1f}")
        
        lines.extend([
            "",
            "Key Metrics:",
            f"  Utilization:    {solution.utilization:.1f}%",
            f"  Cut Length:     {solution.cut_path_length:.1f} mm",
            f"  Pierces:        {solution.pierce_count}",
            f"  Machine Time:   {solution.total_machine_time:.1f}s",
            f"  Total Cost:     ${solution.total_cost:.2f}",
        ])
        
        return "\n".join(lines)


# Convenience function
def score_solution(
    solution: NestingSolution,
    weights: Optional[ScoringWeights] = None
) -> float:
    """
    Quick function to score a solution
    
    Example:
        score = score_solution(my_solution, ScoringWeights.maximize_profit())
    """
    scorer = MultiObjectiveScorer(weights)
    return scorer.score(solution)

