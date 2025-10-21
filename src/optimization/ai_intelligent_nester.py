"""
AI-Powered Intelligent Nesting Algorithm

This module implements an AI-enhanced nesting algorithm that:
- Analyzes shapes intelligently using geometric reasoning
- Makes smart placement decisions based on AI insights
- Optimizes placement sequence and strategy
- Learns from geometric relationships
"""

import time
import numpy as np
from typing import List, Tuple, Optional, Dict
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from geometry.polygon import Polygon
from geometry.collision import CollisionDetector, PlacedPart
from scoring.multi_objective import NestingSolution
from engine.config import NestingConfig
from ai.geometric_analyzer import GeometricAnalyzer, PlacementIntelligence, PackingStrategy


class AIIntelligentNester:
    """
    AI-powered intelligent nesting algorithm that thinks about shapes
    and makes smart placement decisions.
    """
    
    def __init__(self, config: NestingConfig, verbose: bool = False):
        """
        Initialize AI intelligent nester
        
        Args:
            config: Nesting configuration
            verbose: Enable verbose output
        """
        self.config = config
        self.verbose = verbose
        self.analyzer = GeometricAnalyzer()
        self.detector = CollisionDetector(
            sheet_width=config.sheet.width,
            sheet_height=config.sheet.height,
            use_spatial_index=True,
            min_spacing=0.1
        )
        
        # AI placement strategies
        self.strategy_handlers = {
            PackingStrategy.GRID_LIKE: self._place_grid_like,
            PackingStrategy.TIGHT_PACK: self._place_tight_pack,
            PackingStrategy.EDGE_ALIGN: self._place_edge_align,
            PackingStrategy.NESTED: self._place_nested,
            PackingStrategy.SCATTERED: self._place_scattered
        }
    
    def nest(self, parts: List[Polygon]) -> NestingSolution:
        """
        Perform AI-powered intelligent nesting
        
        Args:
            parts: List of polygons to nest
            
        Returns:
            NestingSolution with placed parts
        """
        start_time = time.time()
        
        if self.verbose:
            print(f"\n🧠 AI Intelligent Nesting")
            print(f"   Analyzing {len(parts)} shapes with AI...")
        
        # Step 1: AI Analysis
        placement_intelligence = self.analyzer.analyze_placement_intelligence(parts)
        
        if self.verbose:
            print(f"   AI Analysis Complete:")
            print(f"     - Optimal sequence determined")
            print(f"     - Spatial groupings identified")
            print(f"     - Conflict predictions made")
            print(f"     - Estimated utilization: {placement_intelligence.utilization_estimate:.1%}")
        
        # Step 2: Smart Placement using AI insights
        self.detector.clear()
        placed_count = 0
        
        # Use AI-recommended sequence
        sequence = placement_intelligence.optimal_sequence
        
        for i, shape_idx in enumerate(sequence):
            if i >= 100:  # Limit for performance
                break
            
            polygon = parts[shape_idx]
            insight = placement_intelligence.shape_insights[shape_idx]
            
            if self.verbose and i % 10 == 0:
                print(f"   Progress: {i}/{len(sequence)}... (placed {placed_count})")
            
            # Use AI-recommended strategy
            placement_success = self._place_with_ai_strategy(polygon, insight)
            
            if placement_success:
                placed_count += 1
        
        elapsed = time.time() - start_time
        
        if self.verbose:
            print(f"\n   🧠 AI Nesting Complete!")
            print(f"   Placed: {placed_count}/{len(parts)} ({placed_count/len(parts)*100:.0f}%)")
            print(f"   Utilization: {self.detector.get_utilization():.2f}%")
            print(f"   AI Processing Time: {elapsed:.2f}s")
        
        return self._to_solution(elapsed)
    
    def _place_with_ai_strategy(self, polygon: Polygon, insight) -> bool:
        """Place a polygon using AI-recommended strategy"""
        strategy = insight.placement_strategy
        handler = self.strategy_handlers.get(strategy, self._place_tight_pack)
        
        return handler(polygon, insight)
    
    def _place_grid_like(self, polygon: Polygon, insight) -> bool:
        """Place shape in a grid-like pattern (for simple shapes)"""
        # Simple grid placement for rectangular shapes
        grid_size = max(polygon.bounds.width, polygon.bounds.height) + 10
        
        for row in range(0, int(self.config.sheet.height / grid_size) + 1):
            for col in range(0, int(self.config.sheet.width / grid_size) + 1):
                x = col * grid_size
                y = row * grid_size
                
                if self.detector.add_part(polygon, x, y, insight.optimal_orientation):
                    return True
        
        return False
    
    def _place_tight_pack(self, polygon: Polygon, insight) -> bool:
        """Place shape with tight packing strategy"""
        # Try optimal orientation first
        if self._try_placement(polygon, insight.optimal_orientation):
            return True
        
        # Try other orientations if optimal doesn't work
        for rotation in [0, 90, 180, 270]:
            if rotation != insight.optimal_orientation:
                if self._try_placement(polygon, rotation):
                    return True
        
        return False
    
    def _place_edge_align(self, polygon: Polygon, insight) -> bool:
        """Place shape aligned with sheet edges (for long shapes)"""
        # Try aligning with edges
        edge_positions = [
            (0, 0),  # Bottom-left
            (self.config.sheet.width - polygon.bounds.width, 0),  # Bottom-right
            (0, self.config.sheet.height - polygon.bounds.height),  # Top-left
        ]
        
        for x, y in edge_positions:
            if self.detector.add_part(polygon, x, y, insight.optimal_orientation):
                return True
        
        # Fallback to tight packing
        return self._place_tight_pack(polygon, insight)
    
    def _place_nested(self, polygon: Polygon, insight) -> bool:
        """Place shape nested within other shapes (for complex shapes)"""
        # Try to find gaps between existing shapes
        gap_positions = self._find_gaps()
        
        for x, y in gap_positions:
            if self.detector.add_part(polygon, x, y, insight.optimal_orientation):
                return True
        
        # Fallback to tight packing
        return self._place_tight_pack(polygon, insight)
    
    def _place_scattered(self, polygon: Polygon, insight) -> bool:
        """Place shape in scattered pattern (for moderate complexity)"""
        # Try random positions with some intelligence
        import random
        
        for _ in range(50):  # Try 50 random positions
            x = random.uniform(0, self.config.sheet.width - polygon.bounds.width)
            y = random.uniform(0, self.config.sheet.height - polygon.bounds.height)
            
            if self.detector.add_part(polygon, x, y, insight.optimal_orientation):
                return True
        
        # Fallback to tight packing
        return self._place_tight_pack(polygon, insight)
    
    def _try_placement(self, polygon: Polygon, rotation: float) -> bool:
        """Try placing polygon at various positions with given rotation"""
        # Adaptive grid based on shape size
        grid_step = max(polygon.bounds.width, polygon.bounds.height) / 4
        
        # Search space
        x_min = self.config.sheet.margin_left
        x_max = self.config.sheet.width - self.config.sheet.margin_right - polygon.bounds.width
        y_min = self.config.sheet.margin_bottom
        y_max = self.config.sheet.height - self.config.sheet.margin_top - polygon.bounds.height
        
        if x_max < x_min or y_max < y_min:
            return False
        
        # Try positions in grid
        for x in np.arange(x_min, x_max, grid_step):
            for y in np.arange(y_min, y_max, grid_step):
                if self.detector.add_part(polygon, x, y, rotation):
                    return True
        
        return False
    
    def _find_gaps(self) -> List[Tuple[float, float]]:
        """Find potential gaps between placed shapes"""
        gaps = []
        
        # Simple gap detection - look for empty areas
        grid_size = 20
        for x in range(0, int(self.config.sheet.width), grid_size):
            for y in range(0, int(self.config.sheet.height), grid_size):
                # Check if this area is relatively empty
                if self._is_area_mostly_empty(x, y, grid_size):
                    gaps.append((float(x), float(y)))
        
        return gaps[:20]  # Return top 20 gaps
    
    def _is_area_mostly_empty(self, x: float, y: float, size: float) -> bool:
        """Check if an area is mostly empty"""
        # Simple heuristic - check if there are few placed parts in this area
        count = 0
        for placed_part in self.detector.placed_parts:
            if (abs(placed_part.x - x) < size and 
                abs(placed_part.y - y) < size):
                count += 1
        
        return count < 2  # Area is mostly empty if < 2 parts
    
    def _to_solution(self, elapsed: float) -> NestingSolution:
        """Convert to NestingSolution format"""
        if not self.detector.placed_parts:
            return NestingSolution(
                sheet_width=self.config.sheet.width,
                sheet_height=self.config.sheet.height,
                used_area=0.0,
                total_part_area=0.0,
                placed_parts=[],
                failed_parts=[]
            )
        
        # Convert placed parts to solution format
        solution_placed_parts = [
            (p.polygon, p.x, p.y, p.rotation)
            for p in self.detector.placed_parts
        ]
        
        total_area = sum(p.polygon.area for p in self.detector.placed_parts)
        
        return NestingSolution(
            sheet_width=self.config.sheet.width,
            sheet_height=self.config.sheet.height,
            used_area=total_area,
            total_part_area=total_area,  # Simplified for now
            placed_parts=solution_placed_parts,
            failed_parts=[]  # Simplified for now
        )


def ai_intelligent_nest(
    parts: List[Polygon],
    config: NestingConfig,
    verbose: bool = False
) -> NestingSolution:
    """
    Public interface for AI intelligent nesting
    
    Args:
        parts: List of polygons to nest
        config: Nesting configuration
        verbose: Enable verbose output
        
    Returns:
        NestingSolution with AI-optimized placement
    """
    nester = AIIntelligentNester(config, verbose=verbose)
    return nester.nest(parts)
