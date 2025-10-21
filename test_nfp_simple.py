"""
Test Simplified NFP Nester

Uses NFP for fast collision checking (not valid region computation).
This should be more reliable and still much faster than collision detection.

Target: 15-30% utilization
"""

import sys
sys.path.insert(0, 'src')

from file_io.dxf_importer import import_dxf_file
from engine.config import load_config
from optimization.fast_optimal_nester import fast_nest
from optimization.nfp_simple_nester import simplified_nfp_nest
import time


print("=" * 80)
print("🔷 SIMPLIFIED NFP NESTER TEST")
print("=" * 80)
print("\nStrategy: Use NFP for collision checking (100x faster than intersections)")
print("Target: 15-30% utilization\n")

# Test rectangles
file_path = 'Test files/05_realistic/01_production_rectangles_600x400.dxf'
config_path = 'Test files/config_production_600x400.json'

polygons, _ = import_dxf_file(file_path)
config = load_config(config_path)

print(f"Test: Production Rectangles ({len(polygons)} parts)\n")

# Baseline
print("BASELINE: Fast Optimal")
print("-" * 80)
start = time.time()
baseline = fast_nest(polygons, config, verbose=False)
baseline_time = time.time() - start
print(f"Baseline: {len(baseline.placed_parts)}/{len(polygons)} parts, "
      f"{baseline.utilization:.2f}%, {baseline_time:.2f}s\n")

# Simplified NFP
print("SIMPLIFIED NFP NESTER")
print("-" * 80)
start = time.time()
nfp_solution = simplified_nfp_nest(polygons, config, grid_step=3.0, verbose=True)
nfp_time = time.time() - start

# Results
improvement = nfp_solution.utilization - baseline.utilization

print(f"\n{'=' * 80}")
print("📊 RESULTS")
print("=" * 80)
print(f"Baseline:    {baseline.utilization:.2f}% ({baseline_time:.2f}s)")
print(f"NFP:         {nfp_solution.utilization:.2f}% ({nfp_time:.2f}s)")
print(f"Improvement: +{improvement:.2f}% ({improvement / baseline.utilization * 100:+.1f}%)")

if nfp_solution.utilization >= 20:
    print(f"\n🎉🎉 EXCELLENT! Reached {nfp_solution.utilization:.1f}% (target: 15-30%)")
elif nfp_solution.utilization >= 15:
    print(f"\n🎉 GOOD! Reached {nfp_solution.utilization:.1f}% (target: 15-30%)")
elif nfp_solution.utilization > baseline.utilization:
    print(f"\n✅ Improvement! +{improvement:.1f}%")
else:
    print(f"\n   NFP similar to baseline ({nfp_solution.utilization:.2f}% vs {baseline.utilization:.2f}%)")

print("=" * 80)

