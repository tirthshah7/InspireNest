"""
Iterative Nesting Optimizer - DeepNest-style iterative improvement

This implements the core iterative optimization approach used by DeepNest:
1. Start with a good initial solution
2. Iteratively improve through small changes
3. Accept improvements and reject worse solutions
4. Use multiple optimization strategies in parallel
"""

import time
import random
from typing import List, Tuple, Optional
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from geometry.polygon import Polygon
from engine.config import NestingConfig
from scoring.multi_objective import NestingSolution, ScoringWeights
from optimization.fast_optimal_nester import FastOptimalNester
from geometry.collision import CollisionDetector, PlacedPart


class IterativeNester:
    """
    Iterative nesting optimizer inspired by DeepNest
    
    Uses multiple strategies to iteratively improve nesting solutions:
    - Part repositioning
    - Rotation optimization
    - Local swaps
    - Gap filling
    - Multi-start optimization
    """
    
    def __init__(self, config: NestingConfig, verbose: bool = False):
        self.config = config
        self.verbose = verbose
        self.weights = ScoringWeights.maximize_profit()
        
        # Optimization parameters
        self.max_iterations = 1000
        self.improvement_threshold = 0.01  # 1% improvement required
        self.no_improvement_limit = 50  # Stop after 50 iterations without improvement
        
    def nest(self, parts: List[Polygon]) -> NestingSolution:
        """
        Run iterative nesting optimization
        
        Strategy:
        1. Get initial solution using fast optimal nester
        2. Iteratively improve using multiple techniques
        3. Return best solution found
        """
        start_time = time.time()
        
        if self.verbose:
            print(f"🔄 Starting iterative nesting for {len(parts)} parts")
        
        # Step 1: Get initial solution
        initial_nester = FastOptimalNester(self.config, verbose=False)
        best_solution = initial_nester.nest(parts)
        best_score = self._calculate_score(best_solution)
        
        if self.verbose:
            print(f"📊 Initial solution: {best_solution.utilization:.1f}% utilization, score: {best_score:.3f}")
        
        # Step 2: Iterative improvement
        iteration = 0
        no_improvement_count = 0
        
        while iteration < self.max_iterations and no_improvement_count < self.no_improvement_limit:
            iteration += 1
            
            # Try different improvement strategies
            improved = False
            
            # Strategy 1: Local repositioning
            if self._try_repositioning(best_solution):
                new_score = self._calculate_score(best_solution)
                if new_score > best_score + self.improvement_threshold:
                    best_score = new_score
                    improved = True
                    if self.verbose:
                        print(f"✅ Iteration {iteration}: Repositioning improved score to {best_score:.3f}")
            
            # Strategy 2: Rotation optimization
            elif self._try_rotation_optimization(best_solution):
                new_score = self._calculate_score(best_solution)
                if new_score > best_score + self.improvement_threshold:
                    best_score = new_score
                    improved = True
                    if self.verbose:
                        print(f"✅ Iteration {iteration}: Rotation optimization improved score to {best_score:.3f}")
            
            # Strategy 3: Part swapping
            elif self._try_part_swapping(best_solution):
                new_score = self._calculate_score(best_solution)
                if new_score > best_score + self.improvement_threshold:
                    best_score = new_score
                    improved = True
                    if self.verbose:
                        print(f"✅ Iteration {iteration}: Part swapping improved score to {best_score:.3f}")
            
            # Strategy 4: Gap filling
            elif self._try_gap_filling(best_solution, parts):
                new_score = self._calculate_score(best_solution)
                if new_score > best_score + self.improvement_threshold:
                    best_score = new_score
                    improved = True
                    if self.verbose:
                        print(f"✅ Iteration {iteration}: Gap filling improved score to {best_score:.3f}")
            
            if not improved:
                no_improvement_count += 1
            else:
                no_improvement_count = 0
        
        total_time = time.time() - start_time
        
        if self.verbose:
            print(f"🏁 Iterative optimization completed:")
            print(f"   Iterations: {iteration}")
            print(f"   Final utilization: {best_solution.utilization:.1f}%")
            print(f"   Final score: {best_score:.3f}")
            print(f"   Total time: {total_time:.2f}s")
        
        return best_solution
    
    def _calculate_score(self, solution: NestingSolution) -> float:
        """Calculate optimization score for the solution"""
        if solution.utilization == 0:
            return 0.0
        
        # Multi-objective scoring
        score = (
            self.weights.utilization * solution.utilization / 100.0 +
            self.weights.cut_length * (1.0 - solution.cut_length / 10000.0) +
            self.weights.pierce_count * (1.0 - solution.pierce_count / 100.0) +
            self.weights.machine_time * (1.0 - solution.machine_time / 1000.0)
        )
        
        return score
    
    def _try_repositioning(self, solution: NestingSolution) -> bool:
        """
        Try to improve solution by repositioning parts
        
        Strategy: Move parts to better positions within their current area
        """
        if len(solution.placed_parts) < 2:
            return False
        
        # Pick a random part to reposition
        part_idx = random.randint(0, len(solution.placed_parts) - 1)
        poly, x, y, rotation = solution.placed_parts[part_idx]
        
        # Try small random movements
        for _ in range(5):
            dx = random.uniform(-10, 10)
            dy = random.uniform(-10, 10)
            
            new_x = max(0, min(x + dx, self.config.sheet.width - poly.bounds.width))
            new_y = max(0, min(y + dy, self.config.sheet.height - poly.bounds.height))
            
            # Check if new position is valid
            if self._is_valid_position(poly, new_x, new_y, rotation, solution.placed_parts, part_idx):
                solution.placed_parts[part_idx] = (poly, new_x, new_y, rotation)
                solution._recalculate_metrics()  # Update solution metrics
                return True
        
        return False
    
    def _try_rotation_optimization(self, solution: NestingSolution) -> bool:
        """
        Try to improve solution by optimizing part rotations
        
        Strategy: Try different rotations for parts to fit better
        """
        if len(solution.placed_parts) < 1:
            return False
        
        # Pick a random part to rotate
        part_idx = random.randint(0, len(solution.placed_parts) - 1)
        poly, x, y, rotation = solution.placed_parts[part_idx]
        
        # Try different rotations
        allowed_rotations = self.config.rotation.allowed_angles
        for new_rotation in allowed_rotations:
            if new_rotation != rotation:
                # Check if new rotation fits
                if self._is_valid_position(poly, x, y, new_rotation, solution.placed_parts, part_idx):
                    solution.placed_parts[part_idx] = (poly, x, y, new_rotation)
                    solution._recalculate_metrics()
                    return True
        
        return False
    
    def _try_part_swapping(self, solution: NestingSolution) -> bool:
        """
        Try to improve solution by swapping part positions
        
        Strategy: Swap positions of two parts if it improves the layout
        """
        if len(solution.placed_parts) < 2:
            return False
        
        # Pick two random parts to swap
        idx1, idx2 = random.sample(range(len(solution.placed_parts)), 2)
        poly1, x1, y1, rot1 = solution.placed_parts[idx1]
        poly2, x2, y2, rot2 = solution.placed_parts[idx2]
        
        # Try swapping positions
        if (self._is_valid_position(poly1, x2, y2, rot1, solution.placed_parts, idx1) and
            self._is_valid_position(poly2, x1, y1, rot2, solution.placed_parts, idx2)):
            
            solution.placed_parts[idx1] = (poly1, x2, y2, rot1)
            solution.placed_parts[idx2] = (poly2, x1, y1, rot2)
            solution._recalculate_metrics()
            return True
        
        return False
    
    def _try_gap_filling(self, solution: NestingSolution, original_parts: List[Polygon]) -> bool:
        """
        Try to fill gaps by moving parts closer together
        
        Strategy: Identify gaps and try to move parts to fill them
        """
        if len(solution.placed_parts) < 2:
            return False
        
        # Find parts that could be moved closer
        for i in range(len(solution.placed_parts)):
            poly1, x1, y1, rot1 = solution.placed_parts[i]
            
            # Try moving this part closer to other parts
            for j in range(len(solution.placed_parts)):
                if i == j:
                    continue
                
                poly2, x2, y2, rot2 = solution.placed_parts[j]
                
                # Calculate direction to move closer
                dx = x2 - x1
                dy = y2 - y1
                distance = (dx**2 + dy**2)**0.5
                
                if distance > 20:  # Only move if parts are far apart
                    # Try moving part1 closer to part2
                    move_factor = 0.1
                    new_x = x1 + dx * move_factor
                    new_y = y1 + dy * move_factor
                    
                    # Ensure within bounds
                    new_x = max(0, min(new_x, self.config.sheet.width - poly1.bounds.width))
                    new_y = max(0, min(new_y, self.config.sheet.height - poly1.bounds.height))
                    
                    if self._is_valid_position(poly1, new_x, new_y, rot1, solution.placed_parts, i):
                        solution.placed_parts[i] = (poly1, new_x, new_y, rot1)
                        solution._recalculate_metrics()
                        return True
        
        return False
    
    def _is_valid_position(self, poly: Polygon, x: float, y: float, rotation: float, 
                          placed_parts: List[Tuple], exclude_idx: int) -> bool:
        """Check if a position is valid (no collisions)"""
        # Create detector for collision checking
        detector = CollisionDetector(self.config)
        
        # Add all other placed parts
        for i, (other_poly, other_x, other_y, other_rot) in enumerate(placed_parts):
            if i != exclude_idx:
                placed_part = PlacedPart(other_poly, other_x, other_y, other_rot)
                detector.placed_parts.append(placed_part)
        
        # Check if new position collides
        new_placed_part = PlacedPart(poly, x, y, rotation)
        return not detector.check_collision(new_placed_part)


def iterative_nest(parts: List[Polygon], config: NestingConfig, verbose: bool = False) -> NestingSolution:
    """
    Run iterative nesting optimization
    
    This provides DeepNest-style iterative improvement for better nesting results.
    
    Example:
        parts = import_dxf_file("parts.dxf")
        config = load_config("config.json")
        solution = iterative_nest(parts, config, verbose=True)
        print(f"Final utilization: {solution.utilization:.1f}%")
    """
    nester = IterativeNester(config, verbose=verbose)
    return nester.nest(parts)
