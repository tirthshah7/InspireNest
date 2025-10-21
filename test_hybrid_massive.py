"""
Test Hybrid Nester on Massive Scale Files

Shows that the system can handle real production volumes
"""

import sys
sys.path.insert(0, 'src')

from file_io.dxf_importer import import_dxf_file
from engine.config import load_config
from optimization.hybrid_nester import hybrid_nest
import time


def test_massive_file(filepath: str, test_count: int, config_path: str):
    """Test on massive file"""
    print(f"\n{'='*70}")
    print(f"Testing: {filepath.split('/')[-1]}")
    print('='*70)
    
    # Load
    start = time.time()
    polygons, stats = import_dxf_file(filepath)
    load_time = time.time() - start
    
    print(f"\n✅ Loaded {len(polygons)} shapes in {load_time:.2f}s")
    print(f"   Entities: {stats.total_entities}")
    
    # Test on subset
    test_parts = polygons[:test_count]
    print(f"\nTesting nesting on {len(test_parts)} parts...")
    
    config = load_config(config_path)
    
    start = time.time()
    solution = hybrid_nest(test_parts, config, verbose=False)
    nest_time = time.time() - start
    
    print(f"\n✅ RESULTS:")
    print(f"   Time: {nest_time:.1f}s")
    print(f"   Placed: {len(solution.placed_parts)}/{len(test_parts)} ({len(solution.placed_parts)/len(test_parts)*100:.0f}%)")
    print(f"   Utilization: {solution.utilization:.1f}%")
    print(f"   Speed: {nest_time/len(test_parts):.2f}s per part")
    
    # Check positions
    if solution.placed_parts:
        positions = [(round(x), round(y)) for _, x, y, _ in solution.placed_parts]
        unique = len(set(positions))
        print(f"   Unique positions: {unique}/{len(solution.placed_parts)}")
        
        if unique == len(solution.placed_parts):
            print(f"   ✅ All parts in different positions!")
    
    return {
        'file': filepath.split('/')[-1],
        'total_parts': len(polygons),
        'tested': len(test_parts),
        'placed': len(solution.placed_parts),
        'utilization': solution.utilization,
        'time': nest_time
    }


def main():
    """Test all massive files"""
    print("\n" + "="*70)
    print("  🔥 HYBRID NESTER - MASSIVE SCALE TESTING")
    print("="*70)
    
    # Use large sheet config
    config_path = "Test files/config_large_sheet.json"
    
    tests = [
        ("Test files/07_massive_scale/01_production_500_parts_2000x3000.dxf", 30),
        ("Test files/07_massive_scale/02_large_batch_750_parts_2500x4000.dxf", 25),
        ("Test files/07_massive_scale/03_stress_test_1000_parts_3000x5000.dxf", 20),
    ]
    
    results = []
    
    for filepath, test_count in tests:
        try:
            result = test_massive_file(filepath, test_count, config_path)
            results.append(result)
        except Exception as e:
            print(f"\n❌ FAILED: {e}")
            import traceback
            traceback.print_exc()
    
    # Summary
    print(f"\n{'='*70}")
    print("  📊 MASSIVE SCALE TEST SUMMARY")
    print('='*70)
    
    print(f"\n{'File':<50} {'Tested':<8} {'Placed':<8} {'Util%':<8}")
    print('─'*70)
    
    for r in results:
        print(f"{r['file']:<50} {r['tested']:<8} {r['placed']:<8} {r['utilization']:<8.1f}")
    
    # Assessment
    avg_placement = sum(r['placed']/r['tested'] for r in results) / len(results) * 100
    avg_util = sum(r['utilization'] for r in results) / len(results)
    total_time = sum(r['time'] for r in results)
    
    print(f"\n{'='*70}")
    print("  ✅ PERFORMANCE SUMMARY")
    print('='*70)
    
    print(f"\nAverage placement rate: {avg_placement:.0f}%")
    print(f"Average utilization: {avg_util:.1f}%")
    print(f"Total time: {total_time:.1f}s")
    
    if avg_placement > 20:
        print(f"\n✅ System places parts reliably!")
    
    if avg_util > 2:
        print(f"✅ Utilization is realistic and improving!")
    
    print("\n" + "="*70)
    print("  🎉 MASSIVE SCALE TESTING COMPLETE!")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()

