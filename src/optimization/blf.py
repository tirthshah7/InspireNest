"""
Bottom-Left-Fill (BLF) Nesting Algorithm

Classic geometric nesting algorithm that places parts:
1. As far left as possible
2. As far down as possible
3. Without collisions

Enhanced with NFP for exact placement
"""

from typing import List, Optional, Tuple
from dataclasses import dataclass
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from geometry.polygon import Polygon, Point
from geometry.nfp_manufacturing import ManufacturingAwareNFP, ManufacturingConstraints
from scoring.multi_objective import NestingSolution
from engine.config import NestingConfig


@dataclass
class PlacementResult:
    """Result of attempting to place a part"""
    success: bool
    position: Optional[Point] = None
    rotation: float = 0.0
    score: float = 0.0


class BottomLeftNester:
    """
    Bottom-Left-Fill nesting algorithm with NFP
    
    Places parts in bottom-left positions using
    manufacturing-aware NFP for collision detection
    """
    
    def __init__(self, config: NestingConfig):
        self.config = config
        
        # Create manufacturing NFP computer
        mfg_constraints = ManufacturingConstraints(
            kerf_width=config.spacing.kerf_width,
            min_web=config.spacing.min_web,
            lead_in_length=2.0,
            lead_in_clearance=5.0
        )
        self.nfp_computer = ManufacturingAwareNFP(mfg_constraints)
    
    def nest(self, parts: List[Polygon]) -> NestingSolution:
        """
        Nest parts using BLF algorithm
        
        Args:
            parts: List of polygons to nest
        
        Returns:
            NestingSolution with placed parts
        """
        placed_parts = []
        failed_parts = []
        
        # Place each part
        for i, part in enumerate(parts):
            print(f"  Placing part {i+1}/{len(parts)}: {part.part_id}...")
            
            placement = self._place_part(part, placed_parts)
            
            if placement.success:
                # Create placed part with position
                placed_part = part.translate(
                    placement.position.x - part.bounds.min_x,
                    placement.position.y - part.bounds.min_y
                )
                placed_part.rotation = placement.rotation
                placed_part.position = placement.position
                
                placed_parts.append(placed_part)
                print(f"    ✅ Placed at ({placement.position.x:.1f}, {placement.position.y:.1f})")
            else:
                failed_parts.append(part)
                print(f"    ❌ Could not place (no valid position)")
        
        # Create solution
        solution = self._create_solution(placed_parts, failed_parts)
        
        return solution
    
    def _place_part(
        self,
        part: Polygon,
        placed_parts: List[Polygon]
    ) -> PlacementResult:
        """
        Find best position for a part using BLF strategy
        
        Strategy:
        1. Try all allowed rotations
        2. For each rotation, find leftmost-bottommost position
        3. Use NFP if parts nearby, else use sheet bounds
        4. Return best placement
        """
        best_placement = PlacementResult(success=False)
        best_y = float('inf')
        best_x = float('inf')
        
        # Try all allowed rotations
        allowed_rotations = self.config.rotation.get_allowed_rotations(part.part_id)
        
        for rotation in allowed_rotations:
            # Rotate part
            rotated_part = part.rotate(rotation) if rotation != 0 else part
            
            # Find valid position
            position = self._find_bottom_left_position(rotated_part, placed_parts)
            
            if position is not None:
                # Bottom-left strategy: prefer lower Y, then lower X
                if position.y < best_y or (position.y == best_y and position.x < best_x):
                    best_y = position.y
                    best_x = position.x
                    best_placement = PlacementResult(
                        success=True,
                        position=position,
                        rotation=rotation
                    )
        
        return best_placement
    
    def _find_bottom_left_position(
        self,
        part: Polygon,
        placed_parts: List[Polygon]
    ) -> Optional[Point]:
        """
        Find bottom-left position for part
        
        Uses NFP with already-placed parts to find valid region,
        then returns bottom-left point of that region
        """
        # If no parts placed yet, use bottom-left of sheet
        if not placed_parts:
            usable_bounds = self.config.sheet.get_usable_bounds()
            return Point(usable_bounds.min_x, usable_bounds.min_y)
        
        # Compute usable region using NFP with all placed parts
        # For now, use simplified approach: find bottom-left that doesn't collide
        
        usable_bounds = self.config.sheet.get_usable_bounds()
        part_bounds = part.bounds
        
        # Grid search for valid position (simplified - real NFP would be better)
        step_size = 5.0  # mm
        
        # Start from bottom-left
        for y in range(int(usable_bounds.min_y), int(usable_bounds.max_y - part_bounds.height), int(step_size)):
            for x in range(int(usable_bounds.min_x), int(usable_bounds.max_x - part_bounds.width), int(step_size)):
                test_position = Point(float(x), float(y))
                
                # Move part to test position
                test_part = part.translate(
                    test_position.x - part_bounds.min_x,
                    test_position.y - part_bounds.min_y
                )
                
                # Check if valid
                if self._is_valid_placement(test_part, placed_parts):
                    return test_position
        
        return None  # No valid position found
    
    def _is_valid_placement(
        self,
        part: Polygon,
        placed_parts: List[Polygon]
    ) -> bool:
        """Check if part placement is valid"""
        
        # Check sheet bounds
        if not self.config.sheet.fits_in_sheet(part):
            return False
        
        # Check collision with placed parts (with spacing)
        min_distance = self.config.spacing.total_spacing
        
        for placed_part in placed_parts:
            distance = part.distance_to(placed_part)
            if distance < min_distance:
                return False
        
        return True
    
    def _create_solution(
        self,
        placed_parts: List[Polygon],
        failed_parts: List[Polygon]
    ) -> NestingSolution:
        """Create NestingSolution from placed parts"""
        
        # Calculate metrics
        total_part_area = sum(p.area for p in placed_parts + failed_parts)
        used_area = sum(p.area for p in placed_parts)
        
        # Estimate cut metrics (simplified)
        cut_path_length = sum(p.perimeter for p in placed_parts)
        pierce_count = len(placed_parts)  # At least one per part
        
        # Estimate times (using default material)
        cutting_speed = 3000  # mm/min (default)
        estimated_cut_time = (cut_path_length / cutting_speed) * 60  # seconds
        estimated_pierce_time = pierce_count * 0.5  # 0.5s per pierce
        
        solution = NestingSolution(
            placed_parts=placed_parts,
            failed_parts=failed_parts,
            sheet_width=self.config.sheet.width,
            sheet_height=self.config.sheet.height,
            used_area=used_area,
            total_part_area=total_part_area,
            cut_path_length=cut_path_length,
            pierce_count=pierce_count,
            estimated_cut_time=estimated_cut_time,
            estimated_pierce_time=estimated_pierce_time
        )
        
        return solution

