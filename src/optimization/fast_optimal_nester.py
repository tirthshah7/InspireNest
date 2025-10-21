"""
Fast & Optimal Nesting Algorithm

Optimized for BOTH speed AND utilization:
- Smart part ordering (AI-guided)
- Adaptive grid step (fine for small, coarse for large)
- Early termination (stop when good position found)
- Collision caching (avoid redundant checks)
- Progressive placement (best parts first)

Target: 12-18% utilization in <10s for 50 parts
"""

from typing import List, Tuple, Optional, Dict
import time

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from geometry.polygon import Polygon
from geometry.collision import CollisionDetector, PlacedPart
from scoring.multi_objective import NestingSolution
from ai.features import extract_features, ShapeFeatures
from engine.config import NestingConfig


class FastOptimalNester:
    """
    Fast & optimal nesting algorithm
    
    Key optimizations:
    1. Adaptive grid (based on part size)
    2. Smart ordering (difficulty + area)
    3. Early termination (when found good position)
    4. Limit rotations (0° and 90° only for speed)
    5. Progressive reduction (fewer checks for later parts)
    """
    
    def __init__(
        self,
        config: NestingConfig,
        max_parts: int = 100,  # Limit for speed
        verbose: bool = False,
        use_minkowski: bool = False
    ):
        """
        Initialize fast optimal nester
        
        Args:
            config: Nesting configuration
            max_parts: Maximum parts to place (for speed)
            verbose: Print progress
        """
        self.config = config
        self.max_parts = max_parts
        self.verbose = verbose
        self.use_minkowski = use_minkowski
        
        # Collision detector
        if use_minkowski:
            from geometry.minkowski_collision import MinkowskiCollisionDetector
            self.detector = MinkowskiCollisionDetector(config)
        else:
            self.detector = CollisionDetector(
                config.sheet_width,
                config.sheet_height,
                use_spatial_index=True,
                min_spacing=0.1  # Tight spacing
            )
        
        # Cache for features (avoid recomputation)
        self.feature_cache: Dict[int, ShapeFeatures] = {}
    
    def nest(self, parts: List[Polygon]) -> NestingSolution:
        """
        Nest parts using fast optimal strategy
        
        Args:
            parts: List of polygons to nest
        
        Returns:
            Nesting solution
        """
        if self.verbose:
            print(f"\n⚡ Fast Optimal Nesting")
            print(f"   Parts: {len(parts)} (limit: {self.max_parts})")
        
        start_time = time.time()
        
        # Limit parts for speed
        parts_to_nest = parts[:self.max_parts]
        
        # Normalize ALL parts to origin
        normalized_parts = []
        for p in parts_to_nest:
            bounds = p.bounds
            normalized = p.translate(-bounds.min_x, -bounds.min_y)
            normalized_parts.append(normalized)
        
        # Extract features and sort intelligently
        features = []
        for i, p in enumerate(normalized_parts):
            feat = extract_features(p)
            features.append(feat)
            self.feature_cache[i] = feat
        
        # Smart sorting: Mix of difficulty and area
        # Place difficult parts first, but also consider size
        sorted_indices = sorted(
            range(len(normalized_parts)),
            key=lambda i: (
                features[i].packing_difficulty * 0.6 +  # 60% weight on difficulty
                (1 - features[i].area / 10000) * 0.4    # 40% weight on size (normalized)
            ),
            reverse=True
        )
        
        sorted_parts = [normalized_parts[i] for i in sorted_indices]
        sorted_features = [features[i] for i in sorted_indices]
        
        if self.verbose:
            print(f"   Difficulty range: {min(f.packing_difficulty for f in features):.3f} - {max(f.packing_difficulty for f in features):.3f}")
            print(f"   Area range: {min(p.area for p in normalized_parts):.0f} - {max(p.area for p in normalized_parts):.0f} mm²")
        
        # Clear detector
        self.detector.clear()
        
        # Place parts with adaptive strategy
        placed_count = 0
        
        for i, (part, feat) in enumerate(zip(sorted_parts, sorted_features)):
            if self.verbose and i % 10 == 0:
                print(f"  Progress: {i}/{len(sorted_parts)}... (placed {placed_count})")
            
            # Adaptive grid based on part size
            grid_step = self._get_adaptive_grid(part, feat)
            
            # Adaptive max positions (fewer checks for later parts)
            max_pos = max(10, 30 - i // 10)  # Reduce as we place more parts
            
            # Find and place
            best_pos = self._find_best_position(part, grid_step, max_pos)
            
            if best_pos:
                x, y, rot = best_pos
                if self.detector.add_part(part, x, y, rot):
                    placed_count += 1
        
        elapsed = time.time() - start_time
        
        if self.verbose:
            print(f"\n   Completed in {elapsed:.2f}s")
            print(f"   Placed: {placed_count}/{len(sorted_parts)} ({placed_count/len(sorted_parts)*100:.0f}%)")
            print(f"   Utilization: {self.detector.get_utilization():.2f}%")
            print(f"   Speed: {elapsed/len(sorted_parts)*1000:.0f}ms per part")
        
        return self._to_solution(elapsed)
    
    def _get_adaptive_grid(self, part: Polygon, features: ShapeFeatures) -> float:
        """
        Get adaptive grid step based on part characteristics
        
        Small parts: Fine grid (3mm)
        Medium parts: Medium grid (6mm)  
        Large parts: Coarse grid (10mm)
        """
        area = features.area
        
        if area < 500:
            return 3.0  # Very fine for tiny parts
        elif area < 2000:
            return 5.0  # Fine for small parts
        elif area < 5000:
            return 7.0  # Medium for medium parts
        else:
            return 10.0  # Coarse for large parts
    
    def _find_best_position(
        self,
        part: Polygon,
        grid_step: float,
        max_positions: int
    ) -> Optional[Tuple[float, float, float]]:
        """Find best position with adaptive search"""
        best_position = None
        best_score = -float('inf')
        
        # Try rotations (0° and 90° only for speed)
        rotations = [0, 90] if 90 in self.config.get_allowed_rotations(part) else [0]
        
        for rot in rotations:
            bounds = part.bounds
            
            # Search space
            x_min = self.config.margin_left
            x_max = self.config.sheet_width - self.config.margin_right - bounds.width * 1.5
            y_min = self.config.margin_bottom
            y_max = self.config.sheet_height - self.config.margin_top - bounds.height * 1.5
            
            if x_max < x_min or y_max < y_min:
                continue
            
            # Adaptive sampling
            x_steps = min(max_positions, int((x_max - x_min) / grid_step) + 1)
            y_steps = min(max_positions, int((y_max - y_min) / grid_step) + 1)
            
            # Prioritize bottom-left (check those first)
            positions_to_check = []
            for y_idx in range(y_steps):
                for x_idx in range(x_steps):
                    x = x_min + x_idx * grid_step
                    y = y_min + y_idx * grid_step
                    positions_to_check.append((x, y))
            
            # Check positions
            for x, y in positions_to_check[:max_positions * max_positions]:
                test_part = PlacedPart(part, x, y, rot)
                
                if self.detector.check_placement(test_part):
                    score = self._score_position(x, y, rot)
                    
                    if score > best_score:
                        best_score = score
                        best_position = (x, y, rot)
                    
                    # EARLY EXIT if found excellent position
                    if best_score > 6000:
                        return best_position  # Good enough!
            
            # If found good position for this rotation, use it
            if best_position and best_score > 3000:
                return best_position
        
        return best_position
    
    def _score_position(self, x: float, y: float, rotation: float) -> float:
        """Score position (optimized for compactness)"""
        score = 0.0
        
        # Strong bottom-left bias
        max_x = self.config.sheet_width
        max_y = self.config.sheet_height
        
        x_score = (max_x - x) / max_x
        y_score = (max_y - y) / max_y
        bl_score = (x_score ** 2.5 + y_score ** 2.5) * 300  # AGGRESSIVE
        score += bl_score
        
        # VERY strong compactness
        if self.detector.placed_parts:
            min_dist = float('inf')
            for placed in self.detector.placed_parts:
                dist = ((x - placed.x)**2 + (y - placed.y)**2) ** 0.5
                min_dist = min(min_dist, dist)
            
            # HUGE bonus for proximity
            compactness = 10000 / (min_dist + 1)
            score += compactness
        else:
            # First part: corner preference
            corner_dist = (x**2 + y**2) ** 0.5
            score += 5000 / (corner_dist + 1)
        
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


def fast_nest(
    parts: List[Polygon], 
    config: NestingConfig, 
    verbose: bool = False,
    use_minkowski: bool = False
) -> NestingSolution:
    """
    Fast optimal nesting - best balance of speed and quality
    
    Example:
        parts = import_dxf_file("parts.dxf")
        config = load_config("config.json")
        solution = fast_nest(parts, config, verbose=True)
        print(f"Utilization: {solution.utilization:.1f}%")
    """
    nester = FastOptimalNester(config, verbose=verbose, use_minkowski=use_minkowski)
    return nester.nest(parts)

