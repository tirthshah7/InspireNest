"""
Test System Scalability with High-Volume Files

Tests:
1. DXF loading speed (50, 100, 200 parts)
2. Memory usage
3. Nesting performance
4. System stability (no crashes)
"""

import sys
from pathlib import Path
import time
import tracemalloc

sys.path.insert(0, 'src')

from file_io.dxf_importer import import_dxf_file
from engine.config import load_config
from optimization.blf_enhanced import EnhancedBLF


def test_loading_performance(filepath: str):
    """Test DXF loading performance"""
    print(f"\n{'─'*70}")
    print(f"Loading: {Path(filepath).name}")
    print('─'*70)
    
    tracemalloc.start()
    start = time.time()
    
    polygons, stats = import_dxf_file(filepath)
    
    load_time = time.time() - start
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    print(f"✅ Loaded {len(polygons)} shapes in {load_time:.2f}s")
    print(f"   Entities: {stats.total_entities}")
    print(f"   Memory: {peak/1024/1024:.1f} MB peak")
    print(f"   Speed: {load_time/len(polygons)*1000:.1f}ms per part")
    
    if load_time > 5:
        print(f"   ⚠️  Slow loading")
    elif load_time > 1:
        print(f"   ✅ Acceptable loading")
    else:
        print(f"   ✅ Fast loading")
    
    return {
        'file': Path(filepath).name,
        'parts': len(polygons),
        'time': load_time,
        'memory_mb': peak/1024/1024,
        'polygons': polygons
    }


def test_nesting_performance(polygons: list, config, max_parts: int = 20):
    """Test nesting performance on subset of parts"""
    print(f"\n  Testing nesting on first {max_parts} parts...")
    
    # Use subset for speed
    test_parts = polygons[:max_parts]
    
    start = time.time()
    nester = EnhancedBLF(config)
    solution = nester.nest(test_parts)
    elapsed = time.time() - start
    
    print(f"\n  Results:")
    print(f"    Time: {elapsed:.2f}s ({elapsed/len(test_parts)*1000:.0f}ms per part)")
    print(f"    Placed: {len(solution.placed_parts)}/{len(test_parts)}")
    print(f"    Utilization: {solution.utilization:.1f}%")
    
    return {
        'tested': len(test_parts),
        'placed': len(solution.placed_parts),
        'utilization': solution.utilization,
        'time': elapsed
    }


def main():
    """Test all high-volume files"""
    print("\n" + "="*70)
    print("  🔥 SCALABILITY TESTING - HIGH VOLUME FILES")
    print("="*70)
    
    test_files = [
        "Test files/06_volume_tests/01_mixed_50_parts_1220x2440.dxf",
        "Test files/06_volume_tests/02_production_100_parts_1500x3000.dxf",
        "Test files/06_volume_tests/03_rectangles_100_optimized_1500x3000.dxf",
        "Test files/06_volume_tests/04_tiny_200_parts_1000x1000.dxf",
    ]
    
    config = load_config("Test files/01_simple/config_simple.json")
    
    results = []
    
    for filepath in test_files:
        try:
            # Test loading
            load_result = test_loading_performance(filepath)
            
            # Test nesting on subset (20 parts max for speed)
            max_test = min(20, load_result['parts'])
            nest_result = test_nesting_performance(
                load_result['polygons'],
                config,
                max_parts=max_test
            )
            
            results.append({
                **load_result,
                'nest_tested': nest_result['tested'],
                'nest_placed': nest_result['placed'],
                'nest_util': nest_result['utilization'],
                'nest_time': nest_result['time']
            })
            
        except Exception as e:
            print(f"\n❌ FAILED: {e}")
            traceback.print_exc()
    
    # Summary
    print(f"\n{'='*70}")
    print("  📊 SCALABILITY TEST SUMMARY")
    print('='*70)
    
    print(f"\n{'File':<45} {'Parts':<8} {'Load(s)':<10} {'Nest(s)':<10}")
    print('─'*70)
    
    for r in results:
        print(f"{r['file']:<45} {r['parts']:<8} {r['time']:<10.2f} {r.get('nest_time', 0):<10.2f}")
    
    # Performance assessment
    print(f"\n{'='*70}")
    print("  ✅ SCALABILITY ASSESSMENT")
    print('='*70)
    
    max_parts = max(r['parts'] for r in results)
    max_load_time = max(r['time'] for r in results)
    avg_time_per_part = sum(r['time']/r['parts'] for r in results) / len(results)
    
    print(f"\nMaximum parts handled: {max_parts}")
    print(f"Maximum load time: {max_load_time:.2f}s")
    print(f"Average time per part: {avg_time_per_part*1000:.1f}ms")
    
    if max_load_time < 5:
        print(f"\n✅ EXCELLENT: System handles {max_parts} parts efficiently!")
    elif max_load_time < 10:
        print(f"\n✅ GOOD: System scales to {max_parts} parts")
    else:
        print(f"\n⚠️  SLOW: {max_load_time:.2f}s for {max_parts} parts")
    
    # Nesting performance
    avg_nest_time = sum(r.get('nest_time', 0) for r in results if 'nest_time' in r) / len(results)
    
    print(f"\nNesting performance (20 parts):")
    print(f"  Average time: {avg_nest_time:.2f}s")
    print(f"  Per part: {avg_nest_time/20*1000:.0f}ms")
    
    if avg_nest_time < 5:
        print(f"  ✅ Production-ready speed")
    
    print("\n" + "="*70)
    print("  🎉 SCALABILITY TESTING COMPLETE")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()

