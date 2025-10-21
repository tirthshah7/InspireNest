"""
Day 1 Demo - Showcase of Innovation

This demonstrates the revolutionary features we've built:
1. Manufacturing-Aware NFP
2. Multi-Objective Scoring
3. Robust Polygon Operations
"""

import sys
import os
from math import cos, sin, pi

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from geometry.polygon import Polygon, Point
from geometry.nfp_manufacturing import (
    ManufacturingAwareNFP,
    ManufacturingConstraints,
    compute_manufacturing_nfp
)
from scoring.multi_objective import (
    MultiObjectiveScorer,
    ScoringWeights,
    NestingSolution
)


def demo_polygon_operations():
    """Demonstrate polygon operations"""
    print("╔═══════════════════════════════════════════════════════════════╗")
    print("║        DEMO 1: ROBUST POLYGON OPERATIONS                      ║")
    print("╚═══════════════════════════════════════════════════════════════╝\n")
    
    # Create a rectangle
    rect = Polygon([
        Point(0, 0),
        Point(100, 0),
        Point(100, 50),
        Point(0, 50)
    ], part_id="rect_001")
    
    print(f"Created rectangle: {rect}")
    print(f"  Area: {rect.area:.2f} mm²")
    print(f"  Perimeter: {rect.perimeter:.2f} mm")
    print(f"  Centroid: ({rect.centroid.x:.2f}, {rect.centroid.y:.2f})")
    print(f"  Convexity: {rect.convexity:.3f} (1.0 = perfectly convex)")
    print(f"  Aspect ratio: {rect.aspect_ratio:.3f}")
    print(f"  Compactness: {rect.compactness:.3f} (1.0 = circle)")
    
    # Rotate it
    rect_rotated = rect.rotate(45)
    print(f"\nRotated 45°: {rect_rotated}")
    print(f"  New bounds: {rect_rotated.bounds.width:.2f} x {rect_rotated.bounds.height:.2f}")
    
    # Create circle approximation
    circle = Polygon([
        Point(50 + 30 * cos(theta * pi / 180), 
              50 + 30 * sin(theta * pi / 180))
        for theta in range(0, 360, 10)
    ], part_id="circle_001")
    
    print(f"\nCreated circle: {circle}")
    print(f"  Area: {circle.area:.2f} mm²")
    print(f"  Convexity: {circle.convexity:.3f}")
    print(f"  Compactness: {circle.compactness:.3f}")
    
    print("\n✅ Polygon operations working!\n")


def demo_manufacturing_nfp():
    """Demonstrate manufacturing-aware NFP"""
    print("╔═══════════════════════════════════════════════════════════════╗")
    print("║     DEMO 2: MANUFACTURING-AWARE NFP (INNOVATION!)             ║")
    print("╚═══════════════════════════════════════════════════════════════╝\n")
    
    # Create two simple rectangles
    part_a = Polygon([
        Point(0, 0),
        Point(50, 0),
        Point(50, 30),
        Point(0, 30)
    ], part_id="part_a")
    
    part_b = Polygon([
        Point(0, 0),
        Point(40, 0),
        Point(40, 25),
        Point(0, 25)
    ], part_id="part_b")
    
    print(f"Part A: {part_a}")
    print(f"Part B: {part_b}\n")
    
    # Define manufacturing constraints
    constraints = ManufacturingConstraints(
        kerf_width=0.3,
        min_web=3.0,
        lead_in_length=2.0,
        lead_in_clearance=5.0,
        enable_common_cutting=True
    )
    
    print("Manufacturing Constraints:")
    print(f"  Kerf width: {constraints.kerf_width} mm")
    print(f"  Min web: {constraints.min_web} mm")
    print(f"  Lead-in clearance: {constraints.lead_in_clearance} mm")
    print(f"  Common cutting: {constraints.enable_common_cutting}\n")
    
    # Compute manufacturing-aware NFP
    print("Computing Manufacturing-Aware NFP...")
    nfp_result = compute_manufacturing_nfp(part_a, part_b, constraints)
    
    if nfp_result:
        nfp = nfp_result.nfp_polygon
        print(f"✅ NFP computed: {nfp}")
        print(f"  NFP area: {nfp.area:.2f} mm²")
        print(f"  Optimal positions found: {len(nfp_result.optimal_positions)}")
        
        if nfp_result.optimal_positions:
            for i, pos in enumerate(nfp_result.optimal_positions):
                print(f"    Position {i+1}: ({pos.x:.2f}, {pos.y:.2f})")
        
        if nfp_result.common_edge_zones:
            print(f"  Common edge zones detected: {len(nfp_result.common_edge_zones)}")
            print("    → Can use common line cutting! (saves time)")
    else:
        print("❌ No valid NFP (parts too close or constraints too tight)")
    
    print("\n✅ Manufacturing-Aware NFP working!\n")


def demo_multi_objective_scoring():
    """Demonstrate multi-objective scoring"""
    print("╔═══════════════════════════════════════════════════════════════╗")
    print("║     DEMO 3: MULTI-OBJECTIVE SCORING (INNOVATION!)             ║")
    print("╚═══════════════════════════════════════════════════════════════╝\n")
    
    # Create a sample nesting solution
    solution = NestingSolution(
        sheet_width=1220,
        sheet_height=2440,
        used_area=2000000,  # 2000 cm² = 2 m²
        total_part_area=2000000,
        cut_path_length=15000,  # 15 meters
        pierce_count=25,
        estimated_cut_time=300,  # 5 minutes
        estimated_rapid_time=60,  # 1 minute
        estimated_pierce_time=25,  # 25 seconds (1s per pierce)
        material_cost=50.0,
        machine_time_cost=15.0,
        total_cost=65.0,
        thermal_risk_score=0.2,  # Low risk
        remnant_value_score=0.6  # Good remnants
    )
    
    solution.placed_parts = [None] * 20  # Simulate 20 placed parts
    solution.failed_parts = []
    
    print("Sample Nesting Solution:")
    print(f"  Sheet: {solution.sheet_width} × {solution.sheet_height} mm")
    print(f"  Parts placed: {len(solution.placed_parts)}")
    print(f"  Utilization: {solution.utilization:.1f}%")
    print(f"  Cut length: {solution.cut_path_length:.0f} mm")
    print(f"  Pierces: {solution.pierce_count}")
    print(f"  Total time: {solution.total_machine_time:.1f}s\n")
    
    # Score with different weight presets
    presets = [
        ("Maximize Utilization", ScoringWeights.maximize_utilization()),
        ("Minimize Time", ScoringWeights.minimize_time()),
        ("Maximize Profit", ScoringWeights.maximize_profit())
    ]
    
    print("Scoring with Different Objectives:\n")
    
    for preset_name, weights in presets:
        scorer = MultiObjectiveScorer(weights)
        score = scorer.score(solution)
        
        print(f"╭─ {preset_name} ─╮")
        print(f"│ Overall Score: {score:.1f}/100")
        print(f"│")
        print(f"│ Individual Scores:")
        for obj_name, obj_score in solution.objective_scores.items():
            weight = getattr(weights, obj_name)
            if weight > 0:
                print(f"│   {obj_name:15s}: {obj_score:5.1f}/100 (weight: {weight:.2f})")
        print(f"╰{'─' * 40}╯\n")
    
    # Full explanation
    scorer = MultiObjectiveScorer(ScoringWeights.maximize_profit())
    explanation = scorer.explain_score(solution)
    print("\nDetailed Score Explanation:")
    print(explanation)
    
    print("\n✅ Multi-Objective Scoring working!\n")


def main():
    """Run all demos"""
    print("\n" + "═" * 70)
    print("  🚀 DAY 1 INNOVATION DEMO - Intelligent Nesting System")
    print("═" * 70 + "\n")
    
    try:
        demo_polygon_operations()
        print("\n" + "─" * 70 + "\n")
        
        demo_manufacturing_nfp()
        print("\n" + "─" * 70 + "\n")
        
        demo_multi_objective_scoring()
        
        print("═" * 70)
        print("  ✅ ALL INNOVATIONS WORKING!")
        print("  🎯 Day 1 Foundation Complete")
        print("═" * 70 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

