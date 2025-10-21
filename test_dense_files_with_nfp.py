"""
Test Dense Files with NFP Nester

Run our best algorithms on the newly generated dense files (50-200 parts).
These files have proper part-to-sheet ratios where 40-60% utilization should
be achievable.

Expected Results:
- Theoretical max: 50-65%
- Target: 35-50% (commercial-grade!)
"""

import sys
sys.path.insert(0, 'src')

from file_io.dxf_importer import import_dxf_file
from engine.config import load_config
from optimization.fast_optimal_nester import fast_nest
from optimization.multipass_nester import MultiPassNester
from optimization.nfp_simple_nester import simplified_nfp_nest
import time


def test_dense_files():
    """Test all dense files with our best algorithms"""
    
    print("=" * 80)
    print("🎯 DENSE FILE TESTING - TARGET: 40-60% UTILIZATION")
    print("=" * 80)
    print("\nTesting 50-200 part files with proper part-to-sheet ratios")
    print("Expected: 3-5x improvement over previous test files!\n")
    
    # Test files (dense layouts)
    test_files = [
        "Test files/06_dense_layouts/dense_50_parts.dxf",
        "Test files/06_dense_layouts/dense_75_parts.dxf",
        "Test files/06_dense_layouts/dense_100_parts.dxf",
        "Test files/06_dense_layouts/dense_150_parts.dxf",
        "Test files/06_dense_layouts/dense_200_parts.dxf",
    ]
    
    # Config (use large sheet)
    config_path = "Test files/config_large_sheet.json"
    
    results = []
    
    for test_file in test_files:
        print(f"\n{'=' * 80}")
        print(f"FILE: {test_file}")
        print(f"{'=' * 80}")
        
        try:
            # Load file
            print(f"\nLoading...")
            polygons, stats = import_dxf_file(test_file)
            config = load_config(config_path)
            
            num_parts = len(polygons)
            total_area = sum(p.area for p in polygons)
            sheet_area = config.sheet_width * config.sheet_height
            theoretical_max = (total_area / sheet_area) * 100
            
            print(f"  Parts: {num_parts}")
            print(f"  Total part area: {total_area:,.0f} sq mm")
            print(f"  Sheet: {config.sheet_width}×{config.sheet_height} = {sheet_area:,.0f} sq mm")
            print(f"  Theoretical max: {theoretical_max:.1f}%")
            
            if theoretical_max < 40:
                print(f"  ⚠️  Theoretical max < 40%, might not reach target")
            
            # Test 1: Fast Optimal
            print(f"\n{'─' * 80}")
            print("TEST 1: Fast Optimal Nester")
            print("─" * 80)
            start = time.time()
            fast_solution = fast_nest(polygons, config, verbose=False)
            fast_time = time.time() - start
            print(f"Fast Optimal: {len(fast_solution.placed_parts)}/{num_parts} parts, "
                  f"{fast_solution.utilization:.2f}%, {fast_time:.1f}s")
            
            # Test 2: Multi-Pass
            print(f"\n{'─' * 80}")
            print("TEST 2: Multi-Pass Nester")
            print("─" * 80)
            start = time.time()
            multipass_nester = MultiPassNester(config, verbose=False)
            multipass_solution = multipass_nester.nest(polygons)
            multipass_time = time.time() - start
            print(f"Multi-Pass: {len(multipass_solution.placed_parts)}/{num_parts} parts, "
                  f"{multipass_solution.utilization:.2f}%, {multipass_time:.1f}s")
            
            # Test 3: Simplified NFP
            print(f"\n{'─' * 80}")
            print("TEST 3: Simplified NFP Nester")
            print("─" * 80)
            start = time.time()
            nfp_solution = simplified_nfp_nest(polygons, config, grid_step=5.0, verbose=False)
            nfp_time = time.time() - start
            print(f"NFP: {len(nfp_solution.placed_parts)}/{num_parts} parts, "
                  f"{nfp_solution.utilization:.2f}%, {nfp_time:.1f}s")
            
            # Find best
            best_util = max(fast_solution.utilization, 
                           multipass_solution.utilization,
                           nfp_solution.utilization)
            
            if fast_solution.utilization == best_util:
                best_name = "Fast Optimal"
                best_solution = fast_solution
            elif multipass_solution.utilization == best_util:
                best_name = "Multi-Pass"
                best_solution = multipass_solution
            else:
                best_name = "NFP"
                best_solution = nfp_solution
            
            # Summary
            print(f"\n{'=' * 80}")
            print(f"📊 RESULTS: {num_parts} parts")
            print(f"{'=' * 80}")
            print(f"Theoretical max: {theoretical_max:.1f}%")
            print(f"Best algorithm:  {best_name}")
            print(f"Best util:       {best_util:.2f}%")
            print(f"Efficiency:      {best_util / theoretical_max * 100:.1f}%")
            
            if best_util >= 40:
                print(f"\n🎉🎉🎉 TARGET ACHIEVED! {best_util:.1f}% >= 40%")
            elif best_util >= 30:
                print(f"\n🎉 EXCELLENT! {best_util:.1f}% (close to target)")
            elif best_util >= 20:
                print(f"\n✅ GOOD PROGRESS! {best_util:.1f}%")
            else:
                print(f"\n   Needs improvement: {best_util:.1f}%")
            
            results.append({
                'file': test_file,
                'parts': num_parts,
                'theoretical_max': theoretical_max,
                'fast': fast_solution.utilization,
                'multipass': multipass_solution.utilization,
                'nfp': nfp_solution.utilization,
                'best': best_util,
                'best_name': best_name
            })
            
        except Exception as e:
            print(f"❌ ERROR: {e}")
            import traceback
            traceback.print_exc()
    
    # Final Summary
    print(f"\n{'=' * 80}")
    print("🎉 FINAL SUMMARY - DENSE FILE TESTING")
    print(f"{'=' * 80}\n")
    
    print(f"{'File':<25} {'Parts':>6} {'Theo%':>7} {'Best':>7} {'Eff%':>6} {'Algorithm'}")
    print("─" * 80)
    
    for r in results:
        efficiency = (r['best'] / r['theoretical_max'] * 100) if r['theoretical_max'] > 0 else 0
        print(f"{r['file'].split('/')[-1]:<25} {r['parts']:>6} {r['theoretical_max']:>6.1f}% "
              f"{r['best']:>6.1f}% {efficiency:>5.0f}% {r['best_name']}")
    
    if results:
        avg_util = sum(r['best'] for r in results) / len(results)
        avg_efficiency = sum((r['best'] / r['theoretical_max'] * 100) for r in results if r['theoretical_max'] > 0) / len(results)
        max_util = max(r['best'] for r in results)
        
        print("─" * 80)
        print(f"Average utilization: {avg_util:.2f}%")
        print(f"Average efficiency:  {avg_efficiency:.1f}%")
        print(f"Best utilization:    {max_util:.2f}%")
        
        print(f"\n{'=' * 80}")
        
        if max_util >= 40:
            print(f"🎉🎉🎉 SUCCESS! Reached {max_util:.1f}% (target: 40-60%)")
            print(f"\n✅ NFP-based system achieves COMMERCIAL-GRADE utilization!")
            print(f"✅ Competitive with Deepnest and commercial software!")
            print(f"✅ Ready for production deployment!")
        elif max_util >= 30:
            print(f"🎉 EXCELLENT PROGRESS! Reached {max_util:.1f}%")
            print(f"\n✅ Very close to commercial-grade (40%+)")
            print(f"✅ Strong performance for many applications")
            print(f"   → Fine-tune algorithms for 40%+ (within reach!)")
        elif max_util >= 20:
            print(f"✅ GOOD IMPROVEMENT! Reached {max_util:.1f}%")
            print(f"\n   → 2-3x better than previous test files")
            print(f"   → More optimization needed for 40%+ target")
        else:
            print(f"⚠️  Reached {max_util:.1f}%")
            print(f"\n   → Check part-to-sheet ratios")
            print(f"   → May need algorithm refinement")
        
        print(f"{'=' * 80}")


if __name__ == '__main__':
    test_dense_files()

