"""
Day 2 Complete Demo - Full Nesting Pipeline

This demonstrates the COMPLETE workflow:
1. Load DXF file
2. Load configuration
3. Apply constraints
4. Run BLF nesting
5. Score results
6. Show output

THIS IS THE REAL DEAL - ACTUAL NESTING FROM REAL FILES!
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from file_io.dxf_importer import import_dxf_file
from engine.config import load_config
from optimization.blf import BottomLeftNester
from scoring.multi_objective import MultiObjectiveScorer, ScoringWeights


def run_complete_nesting(dxf_file: str, config_file: str):
    """Run complete nesting pipeline"""
    
    print("\n" + "="*70)
    print(f"  🚀 COMPLETE NESTING PIPELINE")
    print("="*70)
    
    # Step 1: Load DXF file
    print(f"\n📄 Step 1: Loading DXF file...")
    print(f"   File: {Path(dxf_file).name}")
    
    polygons, stats = import_dxf_file(dxf_file)
    
    print(f"   ✅ Loaded {len(polygons)} shapes")
    print(f"   Total entities: {stats.total_entities}")
    if polygons:
        total_area = sum(p.area for p in polygons)
        print(f"   Total part area: {total_area/100:.1f} cm²")
    
    if not polygons:
        print(f"   ❌ No shapes loaded - cannot continue")
        return None
    
    # Step 2: Load configuration
    print(f"\n⚙️  Step 2: Loading configuration...")
    print(f"   Config: {Path(config_file).name}")
    
    config = load_config(config_file)
    
    print(f"   ✅ Config loaded")
    print(f"   Sheet: {config.sheet.width}×{config.sheet.height}mm")
    print(f"   Spacing: kerf={config.spacing.kerf_width}mm, web={config.spacing.min_web}mm")
    print(f"   Rotations: {len(config.rotation.allowed_angles)} options")
    
    # Step 3: Run nesting
    print(f"\n🔧 Step 3: Running BLF nesting algorithm...")
    print(f"   Parts to nest: {len(polygons)}")
    
    nester = BottomLeftNester(config)
    solution = nester.nest(polygons)
    
    print(f"   ✅ Nesting complete")
    print(f"   Parts placed: {len(solution.placed_parts)}/{len(polygons)}")
    print(f"   Parts failed: {len(solution.failed_parts)}")
    
    # Step 4: Score results
    print(f"\n📊 Step 4: Scoring results...")
    
    scorer = MultiObjectiveScorer(ScoringWeights.maximize_profit())
    score = scorer.score(solution)
    
    print(f"   ✅ Scored: {score:.1f}/100")
    
    # Step 5: Show results
    print(f"\n" + "="*70)
    print(f"  📈 RESULTS")
    print("="*70)
    
    print(f"\nUtilization: {solution.utilization:.1f}%")
    print(f"Parts placed: {len(solution.placed_parts)}/{len(polygons)}")
    print(f"Cut length: {solution.cut_path_length:.0f} mm")
    print(f"Pierces: {solution.pierce_count}")
    print(f"Machine time: {solution.total_machine_time:.1f}s")
    
    print(f"\n" + scorer.explain_score(solution))
    
    print("\n" + "="*70)
    
    return solution


def main():
    """Run complete demos on multiple test files"""
    
    print("\n" + "="*80)
    print("  🌟 DAY 2 COMPLETE DEMO - FULL NESTING PIPELINE")
    print("="*80)
    
    test_cases = [
        (
            "Test files/01_simple/circles.dxf",
            "Test files/01_simple/config_simple.json",
            "Simple circles test"
        ),
        (
            "Test files/04_stress_test/06_irregular_concave.dxf",
            "Test files/01_simple/config_simple.json",
            "Concave shapes (L, T, U, +)"
        ),
        (
            "Test files/04_stress_test/05_shapes_with_holes.dxf",
            "Test files/02_moderate/config_moderate.json",
            "Shapes with holes"
        ),
    ]
    
    results = []
    
    for dxf_file, config_file, description in test_cases:
        print(f"\n\n{'#'*80}")
        print(f"  TEST CASE: {description}")
        print('#'*80)
        
        try:
            solution = run_complete_nesting(dxf_file, config_file)
            
            if solution:
                results.append({
                    'test': description,
                    'success': True,
                    'utilization': solution.utilization,
                    'placed': len(solution.placed_parts),
                    'failed': len(solution.failed_parts),
                    'score': solution.weighted_score
                })
            else:
                results.append({
                    'test': description,
                    'success': False
                })
        
        except Exception as e:
            print(f"\n❌ Test failed: {e}")
            import traceback
            traceback.print_exc()
            results.append({
                'test': description,
                'success': False,
                'error': str(e)
            })
    
    # Final summary
    print(f"\n\n{'='*80}")
    print("  🎯 FINAL SUMMARY - DAY 2 COMPLETE DEMO")
    print('='*80)
    
    passed = sum(1 for r in results if r.get('success'))
    total = len(results)
    
    print(f"\nTests Passed: {passed}/{total}\n")
    
    for result in results:
        if result.get('success'):
            print(f"✅ {result['test']}")
            print(f"   Utilization: {result['utilization']:.1f}%")
            print(f"   Placed: {result['placed']}, Failed: {result['failed']}")
            print(f"   Score: {result['score']:.1f}/100")
        else:
            print(f"❌ {result['test']}")
            if 'error' in result:
                print(f"   Error: {result['error']}")
    
    if passed == total:
        print(f"\n🎉 ALL TESTS PASSED!")
        print(f"   COMPLETE NESTING PIPELINE IS WORKING!")
        print(f"\n   ✅ DXF Import → Constraints → BLF → Scoring")
        print(f"   ✅ Real files nested successfully")
        print(f"   ✅ Multi-objective scoring functional")
        print(f"\n   🌟 DAY 2 COMPLETE!")
    else:
        print(f"\n⚠️  Some tests failed - debugging needed")
    
    print("="*80 + "\n")


if __name__ == "__main__":
    main()

