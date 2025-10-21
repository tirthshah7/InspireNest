"""
IMMEDIATE Utilization Optimization

Quick improvements to boost utilization from 2.6% to 10-15%:
1. Better part-to-sheet ratio
2. Tighter spacing (0.1mm instead of 0.3mm)
3. More parts (50 instead of 20)
4. Finer grid where it helps
"""

import sys
sys.path.insert(0, 'src')

from file_io.dxf_importer import import_dxf_file
from engine.config import load_config
from optimization.hybrid_nester import HybridNester
from geometry.collision import CollisionDetector
import time


def test_optimization(name: str, parts, config, grid_step, spacing):
    """Test a specific optimization"""
    print(f"\n{'─'*70}")
    print(f"Test: {name}")
    print(f"  Grid: {grid_step}mm, Spacing: {spacing}mm")
    print('─'*70)
    
    # Create optimized nester
    nester = HybridNester(config, grid_step=grid_step, verbose=False)
    nester.detector = CollisionDetector(
        config.sheet_width,
        config.sheet_height,
        use_spatial_index=True,
        min_spacing=spacing
    )
    
    start = time.time()
    solution = nester.nest(parts)
    elapsed = time.time() - start
    
    print(f"\n✅ Results:")
    print(f"   Placed: {len(solution.placed_parts)}/{len(parts)} ({len(solution.placed_parts)/len(parts)*100:.0f}%)")
    print(f"   Utilization: {solution.utilization:.2f}%")
    print(f"   Time: {elapsed:.1f}s ({elapsed/len(parts):.2f}s per part)")
    
    return {
        'name': name,
        'placed': len(solution.placed_parts),
        'total': len(parts),
        'placement_rate': len(solution.placed_parts)/len(parts)*100,
        'utilization': solution.utilization,
        'time': elapsed
    }


def main():
    """Test multiple optimizations"""
    print("\n" + "="*70)
    print("  🚀 IMMEDIATE UTILIZATION OPTIMIZATION")
    print("  (Quick improvements to boost utilization NOW)")
    print("="*70)
    
    # Load parts
    print("\nLoading parts...")
    polygons, _ = import_dxf_file('Test files/06_volume_tests/01_mixed_50_parts_1220x2440.dxf')
    config = load_config('Test files/config_large_sheet.json')
    
    print(f"Loaded {len(polygons)} parts")
    print(f"Sheet: {config.sheet_width} x {config.sheet_height} mm")
    
    results = []
    
    # Test 1: Current baseline (for comparison)
    print("\n" + "="*70)
    print("  BASELINE (Current Settings)")
    print("="*70)
    result = test_optimization(
        "Baseline (20 parts, 8mm grid, 0.3mm spacing)",
        polygons[:20],
        config,
        grid_step=8.0,
        spacing=0.3
    )
    results.append(result)
    
    # Test 2: TIGHTER SPACING
    print("\n" + "="*70)
    print("  OPTIMIZATION 1: Tighter Spacing")
    print("="*70)
    result = test_optimization(
        "Tighter spacing (20 parts, 8mm grid, 0.1mm spacing)",
        polygons[:20],
        config,
        grid_step=8.0,
        spacing=0.1  # 3x tighter!
    )
    results.append(result)
    
    # Test 3: MORE PARTS
    print("\n" + "="*70)
    print("  OPTIMIZATION 2: More Parts on Sheet")
    print("="*70)
    result = test_optimization(
        "More parts (40 parts, 8mm grid, 0.1mm spacing)",
        polygons[:40],
        config,
        grid_step=8.0,
        spacing=0.1
    )
    results.append(result)
    
    # Test 4: FINER GRID + TIGHTER SPACING
    print("\n" + "="*70)
    print("  OPTIMIZATION 3: Finer Grid + Tight Spacing")
    print("="*70)
    result = test_optimization(
        "Fine grid (30 parts, 5mm grid, 0.1mm spacing)",
        polygons[:30],
        config,
        grid_step=5.0,
        spacing=0.1
    )
    results.append(result)
    
    # Summary
    print("\n" + "="*70)
    print("  📊 OPTIMIZATION COMPARISON")
    print("="*70)
    
    print(f"\n{'Test':<50} {'Placed':<10} {'Util%':<10} {'Time':<10}")
    print('─'*70)
    
    for r in results:
        print(f"{r['name']:<50} {r['placed']}/{r['total']:<8} {r['utilization']:<10.2f} {r['time']:<10.1f}s")
    
    # Find best
    best = max(results, key=lambda r: r['utilization'])
    
    print(f"\n{'='*70}")
    print("  🏆 BEST RESULT")
    print('='*70)
    
    print(f"\nConfiguration: {best['name']}")
    print(f"Placement: {best['placed']}/{best['total']} ({best['placement_rate']:.0f}%)")
    print(f"Utilization: {best['utilization']:.2f}%")
    print(f"Time: {best['time']:.1f}s")
    
    if best['utilization'] > 5:
        print(f"\n🎉 EXCELLENT! Achieved {best['utilization']:.1f}% utilization!")
    elif best['utilization'] > 3:
        print(f"\n✅ GOOD! Improved to {best['utilization']:.1f}% utilization!")
    else:
        print(f"\n⏳ More work needed, currently {best['utilization']:.1f}%")
    
    # Improvement over baseline
    baseline_util = results[0]['utilization']
    improvement = ((best['utilization'] - baseline_util) / baseline_util) * 100
    
    print(f"\nImprovement: {improvement:.0f}% better than baseline")
    print(f"  Baseline: {baseline_util:.2f}%")
    print(f"  Best: {best['utilization']:.2f}%")
    
    print("\n" + "="*70)
    print("  🎯 OPTIMIZATION COMPLETE")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()

