"""
Test DXF Importer with Real Test Files
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from file_io.dxf_importer import import_dxf_file

def test_dxf_file(filepath: str):
    """Test importing a single DXF file"""
    print(f"\n{'='*70}")
    print(f"Testing: {filepath}")
    print('='*70)
    
    try:
        polygons, stats = import_dxf_file(filepath)
        
        print(f"\n✅ SUCCESS!")
        print(f"\n{stats}")
        
        print(f"\nShapes loaded:")
        for i, poly in enumerate(polygons):
            print(f"  {i+1}. {poly}")
            print(f"      Area: {poly.area:.2f} mm²")
            print(f"      Bounds: {poly.bounds.width:.2f} × {poly.bounds.height:.2f} mm")
            print(f"      Vertices: {poly.num_vertices}")
        
        if stats.errors:
            print(f"\n⚠️  Errors encountered:")
            for error in stats.errors:
                print(f"    - {error}")
        
        return True, len(polygons)
        
    except Exception as e:
        print(f"\n❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False, 0


def main():
    """Test all DXF files"""
    print("\n" + "="*70)
    print("  🧪 DXF IMPORTER TEST SUITE")
    print("="*70)
    
    # Test files
    test_files = [
        "Test files/01_simple/rectangles.dxf",
        "Test files/01_simple/circles.dxf",
        "Test files/01_simple/mixed_simple.dxf",
        "Test files/02_moderate/gears.dxf",  # THE BIG TEST - 228 SPLINES!
        "Test files/02_moderate/plates_with_holes.dxf",
        "Test files/03_complex/irregular_shapes.dxf",
        "Test files/03_complex/nested_contours.dxf",
    ]
    
    results = []
    total_shapes = 0
    
    for filepath in test_files:
        success, num_shapes = test_dxf_file(filepath)
        results.append((filepath, success, num_shapes))
        if success:
            total_shapes += num_shapes
    
    # Summary
    print(f"\n{'='*70}")
    print("  📊 SUMMARY")
    print('='*70)
    
    passed = sum(1 for _, success, _ in results if success)
    total = len(results)
    
    print(f"\nTests Passed: {passed}/{total}")
    print(f"Total Shapes Loaded: {total_shapes}")
    
    print(f"\nDetailed Results:")
    for filepath, success, num_shapes in results:
        status = "✅ PASS" if success else "❌ FAIL"
        filename = Path(filepath).name
        print(f"  {status}  {filename:30s} → {num_shapes} shapes")
    
    if passed == total:
        print(f"\n🎉 ALL TESTS PASSED! DXF importer is WORKING!")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
    
    print("="*70 + "\n")


if __name__ == "__main__":
    main()

