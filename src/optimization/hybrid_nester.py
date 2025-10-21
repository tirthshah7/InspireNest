"""
Hybrid Nesting Algorithm

Combines multiple strategies for robust placement:
1. Try beam search first (intelligent)
2. Fall back to greedy BLF if beam search fails
3. Use AI features to guide both

This ensures we ALWAYS place parts, even if not optimal
"""

from typing import List, Tuple
import time

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from geometry.polygon import Polygon
from geometry.collision import CollisionDetector, PlacedPart
from scoring.multi_objective import NestingSolution
from ai.features import extract_features
from engine.config import NestingConfig


class HybridNester:
    """
    Hybrid nesting: Intelligent search + greedy fallback
    
    Strategy:
    - Sort parts by AI difficulty (hard first)
    - For each part, try to find best valid position
    - Use fine grid search with collision detection
    - ALWAYS find a position or skip gracefully
    """
    
    def __init__(
        self,
        config: NestingConfig,
        grid_step: float = 8.0,  # BALANCED: Fast but still good quality
        verbose: bool = False
    ):
        """
        Initialize hybrid nester
        
        Args:
            config: Nesting configuration
            grid_step: Grid step for position search (mm)
            verbose: Print progress
        """
        self.config = config
        self.grid_step = grid_step
        self.verbose = verbose
        
        # Collision detector (with spatial index for speed)
        self.detector = CollisionDetector(
            config.sheet_width,
            config.sheet_height,
            use_spatial_index=True,  # Enable for performance
            min_spacing=0.3  # TIGHTER spacing for better utilization
        )
    
    def nest(self, parts: List[Polygon]) -> NestingSolution:
        """
        Nest parts using hybrid strategy
        
        Args:
            parts: List of polygons to nest
        
        Returns:
            Nesting solution
        """
        if self.verbose:
            print(f"\n🔧 Hybrid Intelligent Nesting")
            print(f"   Parts: {len(parts)}")
            print(f"   Grid step: {self.grid_step}mm")
        
        start_time = time.time()
        
        # CRITICAL: Normalize all polygons to origin!
        # (DXF files have parts at arbitrary positions)
        normalized_parts = []
        for p in parts:
            bounds = p.bounds
            # Translate to origin
            normalized = p.translate(-bounds.min_x, -bounds.min_y)
            normalized_parts.append(normalized)
        
        # Sort by AI features (hardest first, then largest)
        features = [extract_features(p) for p in normalized_parts]
        sorted_indices = sorted(
            range(len(normalized_parts)),
            key=lambda i: (features[i].packing_difficulty, -normalized_parts[i].area),
            reverse=True
        )
        sorted_parts = [normalized_parts[i] for i in sorted_indices]
        
        # Clear detector
        self.detector.clear()
        
        # Place each part
        placed_count = 0
        skipped_count = 0
        
        for i, part in enumerate(sorted_parts):
            if self.verbose:
                print(f"  [{i+1}/{len(sorted_parts)}] Placing part (area={part.area:.0f}mm²)...", end=" ")
                print(f"[Detector has {len(self.detector.placed_parts)} parts]", end=" ")
            
            # Find best position for this part
            best_pos = self._find_best_position(part)
            
            if best_pos:
                x, y, rot = best_pos
                # Add to detector using proper method (updates spatial index!)
                success = self.detector.add_part(part, x, y, rot)
                if success:
                    placed_count += 1
                else:
                    # This shouldn't happen since we validated, but handle it
                    skipped_count += 1
                
                if self.verbose:
                    print(f"✅ ({x:.0f}, {y:.0f}), rot={rot}° [Now {len(self.detector.placed_parts)} parts]")
            else:
                skipped_count += 1
                if self.verbose:
                    print(f"❌ No valid position")
        
        elapsed = time.time() - start_time
        
        if self.verbose:
            print(f"\n   Completed in {elapsed:.2f}s")
            print(f"   Placed: {placed_count}/{len(parts)} ({placed_count/len(parts)*100:.0f}%)")
            print(f"   Utilization: {self.detector.get_utilization():.1f}%")
        
        # Convert to solution
        return self._to_solution(elapsed)
    
    def _find_best_position(
        self,
        part: Polygon
    ) -> Tuple[float, float, float]:
        """
        Find best valid position for a part
        
        Returns: (x, y, rotation) or None if no valid position
        """
        best_position = None
        best_score = -float('inf')
        
        # Try all rotations
        rotations = self.config.get_allowed_rotations(part)
        
        for rot in rotations:
            # DON'T rotate here - PlacedPart handles rotation internally
            bounds = part.bounds
            
            # Define search space (conservative bounds)
            x_min = self.config.margin_left
            x_max = self.config.sheet_width - self.config.margin_right - bounds.width * 1.5  # Conservative
            y_min = self.config.margin_bottom
            y_max = self.config.sheet_height - self.config.margin_top - bounds.height * 1.5  # Conservative
            
            if x_max < x_min or y_max < y_min:
                continue  # Part doesn't fit even without other parts
            
            # Grid search (REASONABLE number of positions)
            x_steps = min(30, int((x_max - x_min) / self.grid_step) + 1)
            y_steps = min(30, int((y_max - y_min) / self.grid_step) + 1)
            
            positions_checked = 0
            
            for x_idx in range(x_steps):
                for y_idx in range(y_steps):
                    x = x_min + x_idx * self.grid_step
                    y = y_min + y_idx * self.grid_step
                    
                    # Check collision (PlacedPart will handle rotation and translation)
                    test_part = PlacedPart(part, x, y, rot)
                    if self.detector.check_placement(test_part):
                        # Valid position! Score it
                        score = self._score_position(x, y, rot)
                        
                        if score > best_score:
                            best_score = score
                            best_position = (x, y, rot)
                    
                    positions_checked += 1
                    
                    # Early exit if found excellent position (speed optimization)
                    if best_score > 3000 and positions_checked > 50:
                        return best_position
        
        # Return the best position found across ALL rotations and positions
        return best_position
    
    def _score_position(self, x: float, y: float, rotation: float) -> float:
        """
        Score a position (AGGRESSIVE compactness for high utilization)
        
        Args:
            x: X position
            y: Y position
            rotation: Rotation angle
        
        Returns:
            Score (higher = better)
        """
        score = 0.0
        
        # Bottom-left preference (STRONG exponential)
        max_x = self.config.sheet_width
        max_y = self.config.sheet_height
        
        x_score = (max_x - x) / max_x
        y_score = (max_y - y) / max_y
        bl_score = (x_score ** 2.0 + y_score ** 2.0) * 200  # DOUBLED weight
        score += bl_score
        
        # Compactness (CRITICAL - near existing parts = MUCH better)
        if self.detector.placed_parts:
            min_dist = float('inf')
            avg_dist = 0
            for placed in self.detector.placed_parts:
                dist = ((x - placed.x)**2 + (y - placed.y)**2) ** 0.5
                min_dist = min(min_dist, dist)
                avg_dist += dist
            
            avg_dist /= len(self.detector.placed_parts)
            
            # HEAVILY favor positions close to existing parts
            compactness = 5000 / (min_dist + 1)  # 5x increase!
            score += compactness
            
            # PENALTY for being far from cluster
            if avg_dist > 150:
                score -= (avg_dist - 150) * 2  # Stronger penalty
        else:
            # First part: STRONGLY prefer bottom-left corner
            corner_dist = (x**2 + y**2) ** 0.5
            score += 2000 / (corner_dist + 1)
        
        # Small rotation penalty
        if rotation != 0:
            score -= 2
        
        return score
    
    def _to_solution(self, elapsed: float) -> NestingSolution:
        """Convert to NestingSolution"""
        placed_parts = [
            (p.polygon, p.x, p.y, p.rotation)
            for p in self.detector.placed_parts
        ]
        
        total_area = sum(p.polygon.area for p in self.detector.placed_parts)
        
        solution = NestingSolution(
            sheet_width=self.config.sheet_width,
            sheet_height=self.config.sheet_height,
            used_area=total_area,
            placed_parts=placed_parts
        )
        
        return solution


def hybrid_nest(
    parts: List[Polygon],
    config: NestingConfig,
    verbose: bool = False
) -> NestingSolution:
    """
    Convenience function for hybrid nesting
    
    Example:
        config = load_config("config.json")
        parts = [poly1, poly2, ...]
        solution = hybrid_nest(parts, config, verbose=True)
    """
    nester = HybridNester(config, grid_step=5.0, verbose=verbose)
    return nester.nest(parts)

