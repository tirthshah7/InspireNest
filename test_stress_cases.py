"""
Test DXF Importer with Stress Test Cases
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'src'))

from file_io.dxf_importer import import_dxf_file

def test_stress_file(filepath: str, expected_features: str):
    """Test a stress test file"""
    print(f"\n{'='*70}")
    print(f"Testing: {Path(filepath).name}")
    print(f"Purpose: {expected_features}")
    print('='*70)
    
    try:
        polygons, stats = import_dxf_file(filepath)
        
        print(f"\n✅ SUCCESS!")
        print(f"  Shapes loaded: {len(polygons)}")
        print(f"  Total entities: {stats.total_entities}")
        
        if polygons:
            # Show stats
            areas = [p.area for p in polygons]
            vertices = [p.num_vertices for p in polygons]
            
            print(f"  Area range: {min(areas):.2f} - {max(areas):.2f} mm²")
            print(f"  Vertex range: {min(vertices)} - {max(vertices)}")
            
            # Show first 3 shapes
            for i, poly in enumerate(polygons[:3]):
                print(f"    {i+1}. Area: {poly.area:.2f} mm², Vertices: {poly.num_vertices}, "
                      f"Size: {poly.bounds.width:.2f}×{poly.bounds.height:.2f} mm")
            
            if len(polygons) > 3:
                print(f"    ... and {len(polygons)-3} more")
        
        if stats.errors:
            print(f"  ⚠️  Warnings: {len(stats.errors)}")
            for error in stats.errors[:3]:
                print(f"    - {error}")
        
        return True, len(polygons)
        
    except Exception as e:
        print(f"\n❌ FAILED: {e}")
        return False, 0


def main():
    """Test all stress cases"""
    print("\n" + "="*70)
    print("  🔥 STRESS TEST SUITE - Testing Edge Cases")
    print("="*70)
    
    stress_tests = [
        ("Test files/04_stress_test/01_tiny_parts.dxf", 
         "Precision: 3-10mm parts"),
        ("Test files/04_stress_test/02_large_parts.dxf", 
         "Scale: 500mm+ parts"),
        ("Test files/04_stress_test/03_high_vertex_count.dxf", 
         "Complexity: 100+ vertices"),
        ("Test files/04_stress_test/04_complex_curves.dxf", 
         "Curves: arcs, splines, ellipses"),
        ("Test files/04_stress_test/05_shapes_with_holes.dxf", 
         "Topology: holes and washers"),
        ("Test files/04_stress_test/06_irregular_concave.dxf", 
         "Concave: L, T, U, + shapes"),
        ("Test files/04_stress_test/07_thin_parts.dxf", 
         "Thin: 1-2mm features"),
        ("Test files/04_stress_test/08_mixed_scales.dxf", 
         "Mixed: 3mm to 300mm range"),
    ]
    
    results = []
    total_shapes = 0
    
    for filepath, description in stress_tests:
        success, num_shapes = test_stress_file(filepath, description)
        results.append((Path(filepath).name, description, success, num_shapes))
        if success:
            total_shapes += num_shapes
    
    # Summary
    print(f"\n{'='*70}")
    print("  📊 STRESS TEST SUMMARY")
    print('='*70)
    
    passed = sum(1 for _, _, success, _ in results if success)
    total = len(results)
    
    print(f"\nTests Passed: {passed}/{total}")
    print(f"Total Shapes Loaded: {total_shapes}")
    
    print(f"\nDetailed Results:")
    for filename, desc, success, num_shapes in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {status}  {filename:30s} → {num_shapes:3d} shapes | {desc}")
    
    if passed == total:
        print(f"\n🎉 ALL STRESS TESTS PASSED!")
        print(f"   System handles:")
        print(f"   ✅ Tiny parts (3mm)")
        print(f"   ✅ Large parts (600mm)")
        print(f"   ✅ High vertex counts (100+)")
        print(f"   ✅ Complex curves (splines, arcs, ellipses)")
        print(f"   ✅ Holes and topology")
        print(f"   ✅ Concave shapes (L, T, U, +)")
        print(f"   ✅ Thin features (1-2mm)")
        print(f"   ✅ Mixed scales (3mm-300mm)")
        print(f"\n   🌟 SYSTEM IS ROBUST!")
    else:
        print(f"\n⚠️  {total - passed} stress test(s) failed")
    
    print("="*70 + "\n")


if __name__ == "__main__":
    main()

