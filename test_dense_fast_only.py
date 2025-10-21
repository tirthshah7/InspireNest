"""
Quick Test - Dense Files (Fast + Multi-Pass Only)

Skip slow NFP test, only test our fastest algorithms.
Expected time: 5-10 minutes total
"""

import sys
sys.path.insert(0, 'src')

from file_io.dxf_importer import import_dxf_file
from engine.config import load_config
from optimization.fast_optimal_nester import fast_nest
from optimization.multipass_nester import MultiPassNester
import time


def quick_test():
    """Quick test of dense files"""
    
    print("=" * 80)
    print("⚡ QUICK TEST - Dense Files (Fast + Multi-Pass Only)")
    print("=" * 80)
    print("\nSkipping slow NFP test, testing fastest algorithms only")
    print("Expected time: 5-10 minutes\n")
    
    test_files = [
        "Test files/06_dense_layouts/dense_50_parts.dxf",
        "Test files/06_dense_layouts/dense_75_parts.dxf",
        "Test files/06_dense_layouts/dense_100_parts.dxf",
        "Test files/06_dense_layouts/dense_150_parts.dxf",
        "Test files/06_dense_layouts/dense_200_parts.dxf",
    ]
    
    config_path = "Test files/config_large_sheet.json"
    
    results = []
    
    for i, test_file in enumerate(test_files, 1):
        print(f"\n{'=' * 80}")
        print(f"TEST {i}/{len(test_files)}: {test_file.split('/')[-1]}")
        print(f"{'=' * 80}")
        
        try:
            polygons, _ = import_dxf_file(test_file)
            config = load_config(config_path)
            
            num_parts = len(polygons)
            total_area = sum(p.area for p in polygons)
            sheet_area = config.sheet_width * config.sheet_height
            theoretical_max = (total_area / sheet_area) * 100
            
            print(f"Parts: {num_parts}, Theoretical max: {theoretical_max:.1f}%")
            
            # Fast Optimal
            print(f"  Testing Fast Optimal... ", end="", flush=True)
            start = time.time()
            fast_sol = fast_nest(polygons, config, verbose=False)
            fast_time = time.time() - start
            print(f"{fast_sol.utilization:.2f}% ({fast_time:.1f}s)")
            
            # Multi-Pass
            print(f"  Testing Multi-Pass... ", end="", flush=True)
            start = time.time()
            mp_nester = MultiPassNester(config, verbose=False)
            mp_sol = mp_nester.nest(polygons)
            mp_time = time.time() - start
            print(f"{mp_sol.utilization:.2f}% ({mp_time:.1f}s)")
            
            best_util = max(fast_sol.utilization, mp_sol.utilization)
            best_name = "Fast" if fast_sol.utilization >= mp_sol.utilization else "Multi-Pass"
            
            print(f"  → Best: {best_util:.2f}% ({best_name})")
            
            results.append({
                'file': test_file.split('/')[-1],
                'parts': num_parts,
                'theoretical': theoretical_max,
                'fast': fast_sol.utilization,
                'multipass': mp_sol.utilization,
                'best': best_util,
                'best_name': best_name
            })
            
        except Exception as e:
            print(f"  ❌ ERROR: {e}")
    
    # Summary
    print(f"\n{'=' * 80}")
    print("📊 QUICK TEST SUMMARY")
    print(f"{'=' * 80}\n")
    
    print(f"{'File':<25} {'Parts':>6} {'Theo%':>7} {'Fast':>6} {'Multi':>6} {'Best':>6} {'Algo'}")
    print("─" * 80)
    
    for r in results:
        print(f"{r['file']:<25} {r['parts']:>6} {r['theoretical']:>6.1f}% "
              f"{r['fast']:>6.2f} {r['multipass']:>6.2f} {r['best']:>6.2f} {r['best_name']}")
    
    if results:
        max_util = max(r['best'] for r in results)
        avg_util = sum(r['best'] for r in results) / len(results)
        
        print("─" * 80)
        print(f"Best: {max_util:.2f}%  |  Average: {avg_util:.2f}%")
        
        print(f"\n{'=' * 80}")
        print("CONCLUSION:")
        print(f"{'=' * 80}")
        
        # Check if theoretical max is the problem
        max_theoretical = max(r['theoretical'] for r in results)
        if max_theoretical < 10:
            print(f"⚠️  PROBLEM: Part-to-sheet ratio is too small!")
            print(f"   Theoretical max: {max_theoretical:.1f}% (need ~50% for 40% target)")
            print(f"   Sheet is TOO BIG or parts are TOO SMALL")
            print(f"\n   SOLUTION: Regenerate with proper ratio (Option A)")
        else:
            if max_util >= 20:
                print(f"✅ Good results: {max_util:.2f}%")
            else:
                print(f"   Results: {max_util:.2f}%")
        
        print(f"{'=' * 80}")


if __name__ == '__main__':
    quick_test()

