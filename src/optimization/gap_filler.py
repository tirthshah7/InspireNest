"""
Gap Filling Strategy (Simpler Approach)

Instead of detecting gaps explicitly, we:
1. Take remaining small parts
2. Try to place them in remaining space
3. Use VERY fine grid (2-3mm) to find any available spots
4. Focus search on areas not yet densely packed

This is simpler and more robust than complex gap detection
"""

from typing import List, Tuple, Optional
import time

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from geometry.polygon import Polygon
from geometry.collision import CollisionDetector, PlacedPart
from scoring.multi_objective import NestingSolution
from ai.features import extract_features
from engine.config import NestingConfig


class GapFillingNester:
    """
    Nesting with gap filling
    
    Strategy:
    1. Use multi-pass to place majority of parts
    2. Take remaining unplaced parts
    3. Use VERY fine grid to fill any gaps
    4. Focus on small parts that can fit in tight spaces
    """
    
    def __init__(
        self,
        config: NestingConfig,
        verbose: bool = False
    ):
        self.config = config
        self.verbose = verbose
        
        # Collision detector
        self.detector = CollisionDetector(
            config.sheet_width,
            config.sheet_height,
            use_spatial_index=True,
            min_spacing=0.1
        )
    
    def nest(self, parts: List[Polygon]) -> NestingSolution:
        """Nest with gap filling"""
        if self.verbose:
            print(f"\n🔧 Gap-Filling Nesting")
            print(f"   Total parts: {len(parts)}")
        
        start_time = time.time()
        
        # Normalize to origin
        normalized_parts = []
        for p in parts:
            bounds = p.bounds
            normalized = p.translate(-bounds.min_x, -bounds.min_y)
            normalized_parts.append(normalized)
        
        # Extract features
        features = [extract_features(p) for p in normalized_parts]
        
        # Sort by difficulty + area
        sorted_indices = sorted(
            range(len(normalized_parts)),
            key=lambda i: (features[i].packing_difficulty, -normalized_parts[i].area),
            reverse=True
        )
        
        sorted_parts = [normalized_parts[i] for i in sorted_indices]
        sorted_features = [features[i] for i in sorted_indices]
        
        # PASS 1: Main placement (larger parts, coarser grid)
        if self.verbose:
            print(f"\n  Pass 1: Main placement...")
        
        main_placed = 0
        for i, (part, feat) in enumerate(zip(sorted_parts, sorted_features)):
            # Adaptive grid
            if feat.area < 500:
                grid_step = 3.0  # Fine for tiny
            elif feat.area < 2000:
                grid_step = 5.0  # Medium for small
            else:
                grid_step = 8.0  # Coarse for large
            
            best_pos = self._find_best_position(part, grid_step, max_checks=500)
            
            if best_pos:
                x, y, rot = best_pos
                if self.detector.add_part(part, x, y, rot):
                    main_placed += 1
        
        if self.verbose:
            print(f"    Placed: {main_placed}/{len(sorted_parts)}")
        
        # PASS 2: Gap filling (remaining parts, VERY fine grid)
        remaining = sorted_parts[main_placed:]
        
        if remaining and self.verbose:
            print(f"\n  Pass 2: Gap filling ({len(remaining)} parts)...")
        
        gap_filled = 0
        for part in remaining[:20]:  # Limit for speed
            # Use VERY fine grid for gap filling
            best_pos = self._find_best_position(part, grid_step=2.0, max_checks=1000)
            
            if best_pos:
                x, y, rot = best_pos
                if self.detector.add_part(part, x, y, rot):
                    gap_filled += 1
        
        if self.verbose and gap_filled > 0:
            print(f"    Gap filled: {gap_filled} parts!")
        
        elapsed = time.time() - start_time
        
        if self.verbose:
            print(f"\n   Completed in {elapsed:.2f}s")
            print(f"   Total placed: {len(self.detector.placed_parts)}/{len(parts)}")
            print(f"   Utilization: {self.detector.get_utilization():.2f}%")
        
        return self._to_solution(elapsed)
    
    def _find_best_position(
        self,
        part: Polygon,
        grid_step: float,
        max_checks: int = 500
    ) -> Optional[Tuple[float, float, float]]:
        """Find best position with limited checks"""
        best_position = None
        best_score = -float('inf')
        
        # Try 0° and 90° only for speed
        rotations = [0]
        if 90 in self.config.get_allowed_rotations(part):
            rotations.append(90)
        
        checks = 0
        
        for rot in rotations:
            bounds = part.bounds
            
            x_min = self.config.margin_left
            x_max = self.config.sheet_width - self.config.margin_right - bounds.width * 1.5
            y_min = self.config.margin_bottom
            y_max = self.config.sheet_height - self.config.margin_top - bounds.height * 1.5
            
            if x_max < x_min or y_max < y_min:
                continue
            
            x_steps = min(40, int((x_max - x_min) / grid_step) + 1)
            y_steps = min(40, int((y_max - y_min) / grid_step) + 1)
            
            # Prioritize bottom-left (check those first)
            for y_idx in range(y_steps):
                for x_idx in range(x_steps):
                    x = x_min + x_idx * grid_step
                    y = y_min + y_idx * grid_step
                    
                    test_part = PlacedPart(part, x, y, rot)
                    
                    if self.detector.check_placement(test_part):
                        score = self._score_position(x, y, rot)
                        
                        if score > best_score:
                            best_score = score
                            best_position = (x, y, rot)
                        
                        # Early exit if excellent
                        if best_score > 8000:
                            return best_position
                    
                    checks += 1
                    if checks >= max_checks:
                        return best_position
            
            if best_position and best_score > 4000:
                return best_position
        
        return best_position
    
    def _score_position(self, x: float, y: float, rotation: float) -> float:
        """Score position with VERY aggressive compactness"""
        score = 0.0
        
        # Bottom-left bias
        x_score = (self.config.sheet_width - x) / self.config.sheet_width
        y_score = (self.config.sheet_height - y) / self.config.sheet_height
        bl_score = (x_score ** 2.5 + y_score ** 2.5) * 400
        score += bl_score
        
        # EXTREME compactness
        if self.detector.placed_parts:
            min_dist = float('inf')
            for placed in self.detector.placed_parts:
                dist = ((x - placed.x)**2 + (y - placed.y)**2) ** 0.5
                min_dist = min(min_dist, dist)
            
            # MASSIVE bonus for very close positions
            compactness = 15000 / (min_dist + 1)
            score += compactness
        else:
            corner_dist = (x**2 + y**2) ** 0.5
            score += 5000 / (corner_dist + 1)
        
        return score
    
    def _to_solution(self, elapsed: float) -> NestingSolution:
        """Convert to solution"""
        placed_parts = [
            (p.polygon, p.x, p.y, p.rotation)
            for p in self.detector.placed_parts
        ]
        
        total_area = sum(p.polygon.area for p in self.detector.placed_parts)
        
        return NestingSolution(
            sheet_width=self.config.sheet_width,
            sheet_height=self.config.sheet_height,
            used_area=total_area,
            placed_parts=placed_parts
        )


def gap_filling_nest(
    parts: List[Polygon],
    config: NestingConfig,
    verbose: bool = False
) -> NestingSolution:
    """
    Gap-filling nesting (simpler than explicit gap detection)
    
    Example:
        solution = gap_filling_nest(parts, config, verbose=True)
        print(f"Utilization: {solution.utilization:.1f}%")
    """
    nester = GapFillingNester(config, verbose=verbose)
    return nester.nest(parts)

