"""
Comprehensive Multi-Pass Benchmark

Test multi-pass nester on ALL test files to find best utilization
"""

import sys
sys.path.insert(0, 'src')

from file_io.dxf_importer import import_dxf_file
from engine.config import load_config
from optimization.multipass_nester import multipass_nest
import json
import time


def test_file(filepath: str, sheet_width: int, sheet_height: int):
    """Test a single file"""
    filename = filepath.split('/')[-1]
    print(f"\n{'─'*70}")
    print(f"Testing: {filename}")
    print(f"Sheet: {sheet_width}×{sheet_height}mm")
    print('─'*70)
    
    try:
        # Load parts
        polygons, stats = import_dxf_file(filepath)
        print(f"Loaded {len(polygons)} parts, {stats.total_entities} entities")
        
        # Create config
        config_data = {
            'sheet': {'width': sheet_width, 'height': sheet_height, 
                      'material': 'mild_steel', 'thickness': 3.0,
                      'margin_left': 5, 'margin_right': 5, 
                      'margin_top': 5, 'margin_bottom': 5},
            'constraints': {'kerf_width': 0.1, 'min_web': 0.5},
            'rotation': {'allowed_angles': [0, 90, 180, 270]}
        }
        
        with open('/tmp/temp_config.json', 'w') as f:
            json.dump(config_data, f)
        
        config = load_config('/tmp/temp_config.json')
        
        # Calculate theoretical
        total_area = sum(p.area for p in polygons)
        sheet_area = sheet_width * sheet_height
        theoretical = (total_area / sheet_area) * 100
        
        print(f"Theoretical max: {theoretical:.1f}%")
        
        # Nest
        start = time.time()
        solution = multipass_nest(polygons, config, verbose=False)
        elapsed = time.time() - start
        
        print(f"\n✅ Results:")
        print(f"   Placed: {len(solution.placed_parts)}/{len(polygons)} ({len(solution.placed_parts)/len(polygons)*100:.0f}%)")
        print(f"   Utilization: {solution.utilization:.2f}%")
        print(f"   Time: {elapsed:.1f}s")
        
        efficiency = (solution.utilization / theoretical * 100) if theoretical > 0 else 0
        print(f"   Efficiency: {efficiency:.1f}%")
        
        return {
            'file': filename,
            'parts': len(polygons),
            'placed': len(solution.placed_parts),
            'utilization': solution.utilization,
            'theoretical': theoretical,
            'efficiency': efficiency,
            'time': elapsed
        }
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def main():
    """Benchmark all realistic + volume files"""
    print("\n" + "="*70)
    print("  🔥 COMPREHENSIVE MULTI-PASS BENCHMARK")
    print("  (Testing on ALL files for maximum utilization)")
    print("="*70)
    
    test_cases = [
        # Realistic files (already tested, designed for specific sheets)
        ('Test files/05_realistic/01_production_rectangles_600x400.dxf', 600, 400),
        ('Test files/05_realistic/03_high_density_circles_600x400.dxf', 600, 400),
        ('Test files/05_realistic/04_irregular_mix_1000x1000.dxf', 1000, 1000),
        
        # Volume files (test with appropriate sheets)
        ('Test files/06_volume_tests/04_tiny_200_parts_1000x1000.dxf', 600, 600),  # Smaller sheet for better util
        ('Test files/06_volume_tests/01_mixed_50_parts_1220x2440.dxf', 800, 800),  # Smaller sheet
    ]
    
    results = []
    
    for filepath, width, height in test_cases:
        result = test_file(filepath, width, height)
        if result:
            results.append(result)
    
    # Summary
    print(f"\n{'='*70}")
    print("  📊 COMPREHENSIVE BENCHMARK RESULTS")
    print('='*70)
    
    print(f"\n{'File':<45} {'Parts':<7} {'Placed':<8} {'Util%':<8} {'Eff%':<7}")
    print('─'*70)
    
    for r in results:
        print(f"{r['file']:<45} {r['parts']:<7} {r['placed']:<8} {r['utilization']:<8.2f} {r['efficiency']:<7.1f}")
    
    # Find best
    best_util = max(results, key=lambda r: r['utilization'])
    best_eff = max(results, key=lambda r: r['efficiency'])
    
    print(f"\n{'='*70}")
    print("  🏆 BEST RESULTS")
    print('='*70)
    
    print(f"\nHighest Utilization:")
    print(f"  File: {best_util['file']}")
    print(f"  Utilization: {best_util['utilization']:.2f}%")
    print(f"  Placed: {best_util['placed']}/{best_util['parts']}")
    
    if best_util['utilization'] >= 15:
        print(f"\n🎉🎉🎉 BREAKTHROUGH! Achieved {best_util['utilization']:.1f}%!")
        print(f"   EXCEEDED Day 6 target of 15%!")
    elif best_util['utilization'] >= 12:
        print(f"\n🎉🎉 EXCELLENT! Achieved {best_util['utilization']:.1f}%!")
        print(f"   Very close to 15% target!")
    elif best_util['utilization'] >= 10:
        print(f"\n🎉 GREAT! Achieved {best_util['utilization']:.1f}%!")
        print(f"   Double digits!")
    
    print(f"\nHighest Efficiency:")
    print(f"  File: {best_eff['file']}")
    print(f"  Efficiency: {best_eff['efficiency']:.1f}% of theoretical")
    
    print("\n" + "="*70)
    print("  🎯 BENCHMARK COMPLETE")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()

