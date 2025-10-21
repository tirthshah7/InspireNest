"""
Test Beam Search vs BLF

Compare beam search against the baseline BLF algorithm
"""

import sys
sys.path.insert(0, 'src')

from file_io.dxf_importer import import_dxf_file
from engine.config import load_config
from optimization.blf_enhanced import EnhancedBLF
from optimization.beam_search import BeamSearchNester
import time


def test_beam_vs_blf():
    """Compare beam search vs BLF"""
    
    print("\n" + "="*70)
    print("  BEAM SEARCH vs BLF COMPARISON")
    print("="*70)
    
    # Load test file
    test_file = "Test files/01_simple/rectangles.dxf"
    config = load_config("Test files/01_simple/config_simple.json")
    
    print(f"\nLoading: {test_file}")
    polygons, stats = import_dxf_file(test_file)
    print(f"Loaded {len(polygons)} shapes")
    
    # Test with subset for speed
    test_parts = polygons[:15]
    print(f"Testing with {len(test_parts)} parts")
    
    print("\n" + "-"*70)
    print("  TEST 1: Enhanced BLF (Baseline)")
    print("-"*70)
    
    blf_nester = EnhancedBLF(config)
    start = time.time()
    blf_solution = blf_nester.nest(test_parts)
    blf_time = time.time() - start
    
    print(f"\nBLF Results:")
    print(f"  Time: {blf_time:.2f}s")
    print(f"  Placed: {len(blf_solution.placed_parts)}/{len(test_parts)}")
    print(f"  Utilization: {blf_solution.utilization:.1f}%")
    
    print("\n" + "-"*70)
    print("  TEST 2: Beam Search (beam_width=3)")
    print("-"*70)
    
    beam_nester = BeamSearchNester(config, beam_width=3, verbose=True)
    start = time.time()
    beam_solution = beam_nester.nest(test_parts)
    beam_time = time.time() - start
    
    print(f"\nBeam Search Results:")
    print(f"  Time: {beam_time:.2f}s")
    print(f"  Placed: {len(beam_solution.placed_parts)}/{len(test_parts)}")
    print(f"  Utilization: {beam_solution.utilization:.1f}%")
    
    # Comparison
    print("\n" + "="*70)
    print("  COMPARISON")
    print("="*70)
    
    print(f"\nPlacement Rate:")
    print(f"  BLF: {len(blf_solution.placed_parts)}/{len(test_parts)} ({len(blf_solution.placed_parts)/len(test_parts)*100:.0f}%)")
    print(f"  Beam: {len(beam_solution.placed_parts)}/{len(test_parts)} ({len(beam_solution.placed_parts)/len(test_parts)*100:.0f}%)")
    
    print(f"\nUtilization:")
    print(f"  BLF: {blf_solution.utilization:.1f}%")
    print(f"  Beam: {beam_solution.utilization:.1f}%")
    
    if beam_solution.utilization > blf_solution.utilization:
        improvement = beam_solution.utilization - blf_solution.utilization
        print(f"  ✅ Beam is {improvement:.1f}% better!")
    elif beam_solution.utilization < blf_solution.utilization:
        print(f"  ⚠️  BLF is {blf_solution.utilization - beam_solution.utilization:.1f}% better")
    else:
        print(f"  ≈ Similar performance")
    
    print(f"\nSpeed:")
    print(f"  BLF: {blf_time:.2f}s")
    print(f"  Beam: {beam_time:.2f}s ({beam_time/blf_time:.1f}x slower)")
    
    print("\n" + "="*70)
    
    if beam_solution.utilization >= blf_solution.utilization:
        print("  ✅ BEAM SEARCH WORKING!")
    else:
        print("  ⚠️  Beam search needs tuning")
    
    print("="*70 + "\n")


if __name__ == "__main__":
    test_beam_vs_blf()

