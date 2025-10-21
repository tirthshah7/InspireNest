"""
Test Enhanced BLF - Compare with Basic BLF

Test improved utilization on realistic test files
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from file_io.dxf_importer import import_dxf_file
from engine.config import load_config
from optimization.blf import BottomLeftNester
from optimization.blf_enhanced import EnhancedBLF
from scoring.multi_objective import MultiObjectiveScorer, ScoringWeights


def compare_algorithms(dxf_file: str, config_file: str):
    """Compare basic vs enhanced BLF"""
    
    print(f"\n{'='*70}")
    print(f"Comparing: {Path(dxf_file).name}")
    print('='*70)
    
    # Load parts
    polygons, stats = import_dxf_file(dxf_file)
    config = load_config(config_file)
    
    print(f"\nParts loaded: {len(polygons)}")
    total_area = sum(p.area for p in polygons) / 100
    print(f"Total part area: {total_area:.1f} cm²")
    print(f"Sheet: {config.sheet.width}×{config.sheet.height}mm")
    
    if not polygons:
        print("No parts to nest")
        return
    
    # Test 1: Basic BLF
    print(f"\n{'─'*70}")
    print("Test 1: BASIC BLF")
    print('─'*70)
    
    basic_nester = BottomLeftNester(config)
    basic_solution = basic_nester.nest(polygons)
    
    # Test 2: Enhanced BLF
    print(f"\n{'─'*70}")
    print("Test 2: ENHANCED BLF")
    print('─'*70)
    
    enhanced_nester = EnhancedBLF(config)
    enhanced_solution = enhanced_nester.nest(polygons)
    
    # Compare
    print(f"\n{'='*70}")
    print("COMPARISON")
    print('='*70)
    
    print(f"\n{'Algorithm':<20} {'Placed':<12} {'Util%':<12} {'Score':<12}")
    print('─'*70)
    
    scorer = MultiObjectiveScorer(ScoringWeights.maximize_profit())
    
    basic_score = scorer.score(basic_solution)
    enhanced_score = scorer.score(enhanced_solution)
    
    print(f"{'Basic BLF':<20} {len(basic_solution.placed_parts):<12} "
          f"{basic_solution.utilization:<12.1f} {basic_score:<12.1f}")
    
    print(f"{'Enhanced BLF':<20} {len(enhanced_solution.placed_parts):<12} "
          f"{enhanced_solution.utilization:<12.1f} {enhanced_score:<12.1f}")
    
    # Improvement
    util_improvement = enhanced_solution.utilization / max(basic_solution.utilization, 0.001)
    score_improvement = enhanced_score - basic_score
    
    print(f"\n{'Improvement':<20} {'':<12} "
          f"{util_improvement:<12.1f}x {score_improvement:<12.1f}")
    
    return {
        'file': Path(dxf_file).name,
        'parts': len(polygons),
        'basic_util': basic_solution.utilization,
        'enhanced_util': enhanced_solution.utilization,
        'improvement': util_improvement
    }


def main():
    """Test enhanced BLF on multiple files"""
    
    print("\n" + "="*70)
    print("  📊 ENHANCED BLF VALIDATION")
    print("="*70)
    
    test_cases = [
        ("Test files/01_simple/circles.dxf", "Test files/01_simple/config_simple.json"),
        ("Test files/04_stress_test/06_irregular_concave.dxf", "Test files/01_simple/config_simple.json"),
        ("Test files/05_realistic/03_high_density_circles_600x400.dxf", "Test files/01_simple/config_simple.json"),
    ]
    
    results = []
    
    for dxf_file, config_file in test_cases:
        result = compare_algorithms(dxf_file, config_file)
        if result:
            results.append(result)
    
    # Summary
    print(f"\n{'='*70}")
    print("  🎯 SUMMARY")
    print('='*70)
    
    print(f"\n{'File':<35} {'Parts':<8} {'Basic%':<10} {'Enhanced%':<12} {'Improve':<10}")
    print('─'*70)
    
    for r in results:
        print(f"{r['file']:<35} {r['parts']:<8} {r['basic_util']:<10.1f} "
              f"{r['enhanced_util']:<12.1f} {r['improvement']:<10.1f}x")
    
    avg_improvement = sum(r['improvement'] for r in results) / len(results)
    
    print(f"\n{'Average Improvement:':<45} {avg_improvement:.1f}x")
    
    if avg_improvement > 5:
        print(f"\n🎉 ENHANCED BLF IS SIGNIFICANTLY BETTER!")
    elif avg_improvement > 2:
        print(f"\n✅ Enhanced BLF shows good improvement")
    else:
        print(f"\n⚠️  Improvement lower than expected")
    
    print("="*70 + "\n")


if __name__ == "__main__":
    main()

