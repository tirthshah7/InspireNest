"""
Unit Tests for Multi-Objective Scoring System

Tests for scoring framework and metrics
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

import pytest
from scoring.multi_objective import (
    ScoringWeights,
    NestingSolution,
    MultiObjectiveScorer,
    score_solution
)


class TestScoringWeights:
    """Tests for scoring weights"""
    
    def test_default_weights_sum_to_one(self):
        weights = ScoringWeights()
        total = (
            weights.utilization +
            weights.cut_length +
            weights.pierce_count +
            weights.machine_time +
            weights.thermal_risk +
            weights.remnant_value +
            weights.total_cost
        )
        assert total == pytest.approx(1.0, abs=1e-6)
    
    def test_maximize_utilization_preset(self):
        weights = ScoringWeights.maximize_utilization()
        assert weights.utilization == 0.8
        assert weights.utilization > weights.cut_length
    
    def test_minimize_time_preset(self):
        weights = ScoringWeights.minimize_time()
        assert weights.machine_time > weights.utilization
    
    def test_maximize_profit_preset(self):
        weights = ScoringWeights.maximize_profit()
        # Should be balanced
        assert 0.15 <= weights.utilization <= 0.35
        assert 0.15 <= weights.cut_length <= 0.25
    
    def test_invalid_weights_raises_error(self):
        """Test that invalid weights (not summing to 1.0) raise error"""
        with pytest.raises(ValueError):
            ScoringWeights(
                utilization=0.5,
                cut_length=0.5,
                pierce_count=0.5,  # Total > 1.0
                machine_time=0,
                thermal_risk=0,
                remnant_value=0,
                total_cost=0
            )


class TestNestingSolution:
    """Tests for nesting solution dataclass"""
    
    def test_solution_creation_empty(self):
        solution = NestingSolution()
        assert len(solution.placed_parts) == 0
        assert len(solution.failed_parts) == 0
    
    def test_solution_utilization_calculation(self):
        solution = NestingSolution(
            sheet_width=1000,
            sheet_height=1000,
            used_area=500000  # 50 cm²
        )
        
        # 500,000 / 1,000,000 = 50%
        assert solution.utilization == pytest.approx(50.0, abs=1e-2)
    
    def test_solution_utilization_zero_sheet(self):
        solution = NestingSolution(
            sheet_width=0,
            sheet_height=0,
            used_area=1000
        )
        
        assert solution.utilization == 0.0
    
    def test_solution_total_machine_time(self):
        solution = NestingSolution(
            estimated_cut_time=100,
            estimated_rapid_time=20,
            estimated_pierce_time=10
        )
        
        assert solution.total_machine_time == 130
    
    def test_solution_parts_placed_ratio(self):
        solution = NestingSolution()
        solution.placed_parts = [None] * 8
        solution.failed_parts = [None] * 2
        
        # 8 / 10 = 0.8
        assert solution.parts_placed_ratio == pytest.approx(0.8, abs=1e-6)
    
    def test_solution_to_dict(self):
        solution = NestingSolution(
            sheet_width=1000,
            sheet_height=1000,
            used_area=755000  # 75.5% utilization
        )
        solution.placed_parts = [None] * 5
        solution.weighted_score = 85.3
        
        data = solution.to_dict()
        
        assert data['num_placed_parts'] == 5
        assert data['utilization_percent'] == pytest.approx(75.5, abs=1e-2)
        assert data['weighted_score'] == pytest.approx(85.3, abs=1e-2)


class TestMultiObjectiveScorer:
    """Tests for multi-objective scorer"""
    
    def test_scorer_creation_default(self):
        scorer = MultiObjectiveScorer()
        assert scorer.weights is not None
    
    def test_scorer_creation_custom_weights(self):
        weights = ScoringWeights.maximize_utilization()
        scorer = MultiObjectiveScorer(weights)
        assert scorer.weights.utilization == 0.8
    
    def test_score_high_utilization_solution(self):
        """Test scoring a high-utilization solution"""
        solution = NestingSolution(
            sheet_width=1000,
            sheet_height=1000,
            used_area=850000,  # 85% utilization
            total_part_area=850000,
            cut_path_length=5000,
            pierce_count=20,
            estimated_cut_time=100,
            estimated_rapid_time=20,
            estimated_pierce_time=10
        )
        solution.placed_parts = [None] * 20
        
        scorer = MultiObjectiveScorer(ScoringWeights.maximize_utilization())
        score = scorer.score(solution)
        
        # High utilization should get high score
        assert score > 80
    
    def test_score_low_utilization_solution(self):
        """Test scoring a low-utilization solution"""
        solution = NestingSolution(
            sheet_width=1000,
            sheet_height=1000,
            used_area=100000,  # 10% utilization
            total_part_area=100000,
            cut_path_length=2000,
            pierce_count=5,
            estimated_cut_time=40,
            estimated_rapid_time=10,
            estimated_pierce_time=2.5
        )
        solution.placed_parts = [None] * 5
        
        scorer = MultiObjectiveScorer(ScoringWeights.maximize_utilization())
        score = scorer.score(solution)
        
        # Low utilization should get lower score
        assert score < 60
    
    def test_score_optimal_pierces(self):
        """Test that optimal pierce count gets perfect score"""
        solution = NestingSolution(
            sheet_width=1000,
            sheet_height=1000,
            used_area=500000,
            total_part_area=500000,
            pierce_count=10  # Exactly 1 per part
        )
        solution.placed_parts = [None] * 10
        
        scorer = MultiObjectiveScorer()
        scorer.score(solution)
        
        # Pierce count score should be perfect
        assert solution.objective_scores['pierce_count'] == 100.0
    
    def test_score_extra_pierces_penalty(self):
        """Test that extra pierces are penalized"""
        solution = NestingSolution(
            sheet_width=1000,
            sheet_height=1000,
            used_area=500000,
            total_part_area=500000,
            pierce_count=25  # 15 extra pierces
        )
        solution.placed_parts = [None] * 10
        
        scorer = MultiObjectiveScorer()
        scorer.score(solution)
        
        # Should be penalized
        assert solution.objective_scores['pierce_count'] < 100.0
    
    def test_score_stores_individual_scores(self):
        """Test that individual scores are stored"""
        solution = NestingSolution(
            sheet_width=1000,
            sheet_height=1000,
            used_area=800000
        )
        solution.placed_parts = [None] * 10
        
        scorer = MultiObjectiveScorer()
        scorer.score(solution)
        
        # Should have all objective scores
        assert 'utilization' in solution.objective_scores
        assert 'cut_length' in solution.objective_scores
        assert 'pierce_count' in solution.objective_scores
        assert 'machine_time' in solution.objective_scores
        assert 'thermal_risk' in solution.objective_scores
    
    def test_score_sets_weighted_score(self):
        """Test that weighted score is set"""
        solution = NestingSolution(
            sheet_width=1000,
            sheet_height=1000,
            used_area=700000
        )
        solution.placed_parts = [None] * 10
        
        scorer = MultiObjectiveScorer()
        score = scorer.score(solution)
        
        assert solution.weighted_score == score
        assert 0 <= score <= 100
    
    def test_compare_solutions_better(self):
        """Test comparing two solutions - first is better"""
        solution_a = NestingSolution(
            sheet_width=1000, sheet_height=1000,
            used_area=850000  # 85% utilization
        )
        solution_a.placed_parts = [None] * 20
        
        solution_b = NestingSolution(
            sheet_width=1000, sheet_height=1000,
            used_area=600000  # 60% utilization
        )
        solution_b.placed_parts = [None] * 15
        
        scorer = MultiObjectiveScorer()
        result = scorer.compare(solution_a, solution_b)
        
        assert result == 1  # solution_a is better
    
    def test_compare_solutions_worse(self):
        """Test comparing two solutions - second is better"""
        solution_a = NestingSolution(
            sheet_width=1000, sheet_height=1000,
            used_area=400000
        )
        solution_a.placed_parts = [None] * 10
        
        solution_b = NestingSolution(
            sheet_width=1000, sheet_height=1000,
            used_area=800000
        )
        solution_b.placed_parts = [None] * 20
        
        scorer = MultiObjectiveScorer()
        result = scorer.compare(solution_a, solution_b)
        
        assert result == -1  # solution_b is better
    
    def test_compare_solutions_equal(self):
        """Test comparing nearly equal solutions"""
        solution_a = NestingSolution(
            sheet_width=1000, sheet_height=1000,
            used_area=750000
        )
        solution_a.placed_parts = [None] * 15
        
        solution_b = NestingSolution(
            sheet_width=1000, sheet_height=1000,
            used_area=751000  # Very close
        )
        solution_b.placed_parts = [None] * 15
        
        scorer = MultiObjectiveScorer()
        result = scorer.compare(solution_a, solution_b)
        
        assert result == 0  # Nearly equal
    
    def test_explain_score_generates_text(self):
        """Test that score explanation is generated"""
        solution = NestingSolution(
            sheet_width=1000,
            sheet_height=1000,
            used_area=750000,
            cut_path_length=10000,
            pierce_count=15
        )
        solution.placed_parts = [None] * 15
        
        scorer = MultiObjectiveScorer()
        explanation = scorer.explain_score(solution)
        
        assert isinstance(explanation, str)
        assert len(explanation) > 100
        assert 'Overall Score' in explanation
        assert 'utilization' in explanation
    
    def test_convenience_function(self):
        """Test convenience score_solution function"""
        solution = NestingSolution(
            sheet_width=1000,
            sheet_height=1000,
            used_area=800000
        )
        solution.placed_parts = [None] * 20
        
        score = score_solution(solution)
        assert 0 <= score <= 100
    
    def test_different_weights_different_scores(self):
        """Test that different weight presets produce different scores"""
        solution = NestingSolution(
            sheet_width=1000,
            sheet_height=1000,
            used_area=600000,  # 60% utilization
            cut_path_length=20000,  # Long cut path
            pierce_count=10
        )
        solution.placed_parts = [None] * 10
        
        score_util = score_solution(solution, ScoringWeights.maximize_utilization())
        score_time = score_solution(solution, ScoringWeights.minimize_time())
        
        # Different weights should produce different scores
        assert abs(score_util - score_time) > 1.0


# Run tests if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v"])

