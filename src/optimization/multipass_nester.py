"""
Multi-Pass Nesting Strategy

Uses multiple passes to achieve higher utilization:
- Pass 1: Large parts (>5000mm²) - establish layout
- Pass 2: Medium parts (1000-5000mm²) - fill space
- Pass 3: Small parts (<1000mm²) - fill gaps

Expected improvement: 2-3x better utilization than single pass
"""

from typing import List, Tuple, Dict
import time

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from geometry.polygon import Polygon
from geometry.collision import CollisionDetector, PlacedPart
from scoring.multi_objective import NestingSolution
from ai.features import extract_features
from engine.config import NestingConfig


class MultiPassNester:
    """
    Multi-pass nesting for maximum utilization
    
    Strategy:
    1. Categorize parts by size (large, medium, small)
    2. Place large parts first (establishes layout)
    3. Place medium parts (fills main space)
    4. Place small parts (fills remaining gaps)
    
    Each pass uses progressively finer grid search
    """
    
    def __init__(
        self,
        config: NestingConfig,
        large_threshold: float = 5000.0,  # mm²
        small_threshold: float = 1000.0,  # mm²
        verbose: bool = False
    ):
        """
        Initialize multi-pass nester
        
        Args:
            config: Nesting configuration
            large_threshold: Area threshold for large parts
            small_threshold: Area threshold for small parts
            verbose: Print progress
        """
        self.config = config
        self.large_threshold = large_threshold
        self.small_threshold = small_threshold
        self.verbose = verbose
        
        # Collision detector (shared across passes)
        self.detector = CollisionDetector(
            config.sheet_width,
            config.sheet_height,
            use_spatial_index=True,
            min_spacing=0.1  # Tight spacing for better util
        )
    
    def nest(self, parts: List[Polygon]) -> NestingSolution:
        """
        Nest parts using multi-pass strategy
        
        Args:
            parts: List of polygons to nest
        
        Returns:
            Nesting solution
        """
        if self.verbose:
            print(f"\n🔧 Multi-Pass Intelligent Nesting")
            print(f"   Total parts: {len(parts)}")
        
        start_time = time.time()
        
        # Normalize ALL parts to origin first
        normalized_parts = []
        for p in parts:
            bounds = p.bounds
            normalized = p.translate(-bounds.min_x, -bounds.min_y)
            normalized_parts.append(normalized)
        
        # Categorize by size
        large_parts = []
        medium_parts = []
        small_parts = []
        
        for p in normalized_parts:
            if p.area >= self.large_threshold:
                large_parts.append(p)
            elif p.area >= self.small_threshold:
                medium_parts.append(p)
            else:
                small_parts.append(p)
        
        if self.verbose:
            print(f"   Large parts: {len(large_parts)} (≥{self.large_threshold}mm²)")
            print(f"   Medium parts: {len(medium_parts)} ({self.small_threshold}-{self.large_threshold}mm²)")
            print(f"   Small parts: {len(small_parts)} (<{self.small_threshold}mm²)")
        
        # Clear detector
        self.detector.clear()
        
        # Pass 1: Large parts (coarse grid, fast)
        if large_parts:
            if self.verbose:
                print(f"\n  Pass 1: Placing {len(large_parts)} large parts...")
            placed_large = self._place_parts(large_parts, grid_step=10.0, max_positions=15)
            if self.verbose:
                print(f"    Placed: {placed_large}/{len(large_parts)}")
        
        # Pass 2: Medium parts (medium grid, balanced)
        if medium_parts:
            if self.verbose:
                print(f"\n  Pass 2: Placing {len(medium_parts)} medium parts...")
            # Limit to 50 medium parts for speed
            medium_subset = medium_parts[:50]
            placed_medium = self._place_parts(medium_subset, grid_step=7.0, max_positions=20)
            if self.verbose:
                print(f"    Placed: {placed_medium}/{len(medium_subset)}")
        
        # Pass 3: Small parts (fine grid, limited count)
        if small_parts:
            if self.verbose:
                print(f"\n  Pass 3: Placing {len(small_parts)} small parts...")
            # Limit to 30 small parts for speed
            small_subset = small_parts[:30]
            placed_small = self._place_parts(small_subset, grid_step=5.0, max_positions=25)
            if self.verbose:
                print(f"    Placed: {placed_small}/{len(small_subset)}")
        
        elapsed = time.time() - start_time
        
        if self.verbose:
            print(f"\n   Completed in {elapsed:.2f}s")
            print(f"   Total placed: {len(self.detector.placed_parts)}/{len(parts)}")
            print(f"   Utilization: {self.detector.get_utilization():.2f}%")
        
        # Convert to solution
        return self._to_solution(elapsed)
    
    def _place_parts(
        self,
        parts: List[Polygon],
        grid_step: float,
        max_positions: int
    ) -> int:
        """
        Place a batch of parts
        
        Args:
            parts: Parts to place
            grid_step: Grid step for this pass
            max_positions: Max positions to check per part
        
        Returns:
            Number of parts successfully placed
        """
        # Sort by AI difficulty (hard first, then large first)
        features = [extract_features(p) for p in parts]
        sorted_indices = sorted(
            range(len(parts)),
            key=lambda i: (features[i].packing_difficulty, -parts[i].area),
            reverse=True
        )
        sorted_parts = [parts[i] for i in sorted_indices]
        
        placed_count = 0
        
        for part in sorted_parts:
            best_pos = self._find_best_position(part, grid_step, max_positions)
            
            if best_pos:
                x, y, rot = best_pos
                if self.detector.add_part(part, x, y, rot):
                    placed_count += 1
        
        return placed_count
    
    def _find_best_position(
        self,
        part: Polygon,
        grid_step: float,
        max_positions: int
    ) -> Tuple[float, float, float]:
        """Find best position for a part with given grid step"""
        best_position = None
        best_score = -float('inf')
        
        rotations = self.config.get_allowed_rotations(part)
        
        for rot in rotations:
            bounds = part.bounds
            
            # Define search space
            x_min = self.config.margin_left
            x_max = self.config.sheet_width - self.config.margin_right - bounds.width * 1.5
            y_min = self.config.margin_bottom
            y_max = self.config.sheet_height - self.config.margin_top - bounds.height * 1.5
            
            if x_max < x_min or y_max < y_min:
                continue
            
            # Grid search
            x_steps = min(max_positions, int((x_max - x_min) / grid_step) + 1)
            y_steps = min(max_positions, int((y_max - y_min) / grid_step) + 1)
            
            positions_checked = 0
            
            for x_idx in range(x_steps):
                for y_idx in range(y_steps):
                    x = x_min + x_idx * grid_step
                    y = y_min + y_idx * grid_step
                    
                    # Check collision
                    test_part = PlacedPart(part, x, y, rot)
                    if self.detector.check_placement(test_part):
                        # Valid! Score it
                        score = self._score_position(x, y, rot)
                        
                        if score > best_score:
                            best_score = score
                            best_position = (x, y, rot)
                    
                    positions_checked += 1
                    
                    # Early exit if found excellent position
                    if best_score > 5000 and positions_checked > 30:
                        return best_position
        
        return best_position
    
    def _score_position(self, x: float, y: float, rotation: float) -> float:
        """Score a position using bottom-left + compactness"""
        score = 0.0
        
        # Bottom-left bias (exponential)
        max_x = self.config.sheet_width
        max_y = self.config.sheet_height
        
        x_score = (max_x - x) / max_x
        y_score = (max_y - y) / max_y
        bl_score = (x_score ** 2.0 + y_score ** 2.0) * 200
        score += bl_score
        
        # Compactness (near existing parts)
        if self.detector.placed_parts:
            min_dist = float('inf')
            for placed in self.detector.placed_parts:
                dist = ((x - placed.x)**2 + (y - placed.y)**2) ** 0.5
                min_dist = min(min_dist, dist)
            
            compactness = 5000 / (min_dist + 1)
            score += compactness
        else:
            corner_dist = (x**2 + y**2) ** 0.5
            score += 2000 / (corner_dist + 1)
        
        # Rotation penalty (slight preference for 0°)
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


def multipass_nest(
    parts: List[Polygon],
    config: NestingConfig,
    verbose: bool = False
) -> NestingSolution:
    """
    Convenience function for multi-pass nesting
    
    Example:
        config = load_config("config.json")
        parts = import_dxf_file("parts.dxf")
        solution = multipass_nest(parts, config, verbose=True)
        print(f"Utilization: {solution.utilization:.1f}%")
    """
    nester = MultiPassNester(config, verbose=verbose)
    return nester.nest(parts)

