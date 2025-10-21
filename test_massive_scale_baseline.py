"""
Test Current System at MASSIVE Scale

Tests loading and feature extraction on:
- 500 parts
- 750 parts  
- 1000 parts

Establishes baseline performance BEFORE collision detection
"""

import sys
import time
import tracemalloc
sys.path.insert(0, 'src')

from file_io.dxf_importer import import_dxf_file
from ai.features import ShapeFeatureExtractor
from engine.config import load_config
from optimization.beam_search import BeamSearchNester


def test_load_and_features(filepath: str, max_parts: int = None):
    """Test loading and feature extraction"""
    print(f"\n{'─'*70}")
    print(f"Testing: {filepath.split('/')[-1]}")
    print('─'*70)
    
    # Load
    tracemalloc.start()
    start = time.time()
    
    polygons, stats = import_dxf_file(filepath)
    
    load_time = time.time() - start
    current, peak_load = tracemalloc.get_traced_memory()
    
    print(f"✅ Loaded {len(polygons)} shapes in {load_time:.2f}s")
    print(f"   Entities: {stats.total_entities}")
    print(f"   Memory: {peak_load/1024/1024:.1f} MB")
    print(f"   Speed: {load_time/len(polygons)*1000:.1f}ms per part")
    
    # Feature extraction
    print(f"\n  Extracting AI features...")
    start = time.time()
    
    extractor = ShapeFeatureExtractor()
    features = extractor.extract_batch(polygons)
    
    feature_time = time.time() - start
    current, peak_total = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    print(f"  ✅ Extracted features in {feature_time:.2f}s")
    print(f"     Per shape: {feature_time/len(polygons)*1000:.1f}ms")
    print(f"     Total memory: {peak_total/1024/1024:.1f} MB")
    
    # Feature statistics
    difficulties = [f.packing_difficulty for f in features]
    convexities = [f.convexity for f in features]
    
    print(f"\n  Feature Statistics:")
    print(f"     Difficulty: {min(difficulties):.3f} - {max(difficulties):.3f}")
    print(f"     Avg difficulty: {sum(difficulties)/len(difficulties):.3f}")
    print(f"     Convexity: {min(convexities):.3f} - {max(convexities):.3f}")
    
    # Test nesting on small subset
    if max_parts and len(polygons) > max_parts:
        print(f"\n  Testing beam search on first {max_parts} parts...")
        test_parts = polygons[:max_parts]
        
        config = load_config("Test files/01_simple/config_simple.json")
        nester = BeamSearchNester(config, beam_width=3, verbose=False)
        
        start = time.time()
        solution = nester.nest(test_parts)
        nest_time = time.time() - start
        
        print(f"  ✅ Nested {len(test_parts)} parts in {nest_time:.2f}s")
        print(f"     Placed: {len(solution.placed_parts)}/{len(test_parts)}")
        print(f"     Utilization: {solution.utilization:.1f}%")
        print(f"     Speed: {nest_time/len(test_parts)*1000:.0f}ms per part")
    
    return {
        'file': filepath.split('/')[-1],
        'parts': len(polygons),
        'load_time': load_time,
        'feature_time': feature_time,
        'memory_mb': peak_total/1024/1024,
        'avg_difficulty': sum(difficulties)/len(difficulties)
    }


def main():
    """Test all massive scale files"""
    print("\n" + "="*70)
    print("  🔥 MASSIVE SCALE BASELINE TESTING")
    print("  (Before collision detection)")
    print("="*70)
    
    test_files = [
        ("Test files/07_massive_scale/01_production_500_parts_2000x3000.dxf", 20),
        ("Test files/07_massive_scale/02_large_batch_750_parts_2500x4000.dxf", 20),
        ("Test files/07_massive_scale/03_stress_test_1000_parts_3000x5000.dxf", 15),
    ]
    
    results = []
    
    for filepath, max_nest in test_files:
        try:
            result = test_load_and_features(filepath, max_nest)
            results.append(result)
        except Exception as e:
            print(f"\n❌ FAILED: {e}")
            import traceback
            traceback.print_exc()
    
    # Summary
    print(f"\n{'='*70}")
    print("  📊 MASSIVE SCALE BASELINE SUMMARY")
    print('='*70)
    
    print(f"\n{'File':<50} {'Parts':<8} {'Load(s)':<10} {'Features(s)':<12}")
    print('─'*70)
    
    for r in results:
        print(f"{r['file']:<50} {r['parts']:<8} {r['load_time']:<10.2f} {r['feature_time']:<12.2f}")
    
    # Performance assessment
    max_parts = max(r['parts'] for r in results)
    max_load = max(r['load_time'] for r in results)
    max_feature = max(r['feature_time'] for r in results)
    total_memory = max(r['memory_mb'] for r in results)
    
    print(f"\n{'='*70}")
    print("  ✅ SCALABILITY ASSESSMENT")
    print('='*70)
    
    print(f"\nMaximum scale tested: {max_parts} parts")
    print(f"Maximum load time: {max_load:.2f}s")
    print(f"Maximum feature time: {max_feature:.2f}s")
    print(f"Maximum memory: {total_memory:.1f} MB")
    
    if max_load < 10:
        print(f"\n✅ EXCELLENT: System loads {max_parts} parts in <10s!")
    else:
        print(f"\n⚠️  Slow: {max_load:.2f}s for {max_parts} parts")
    
    if max_feature < 5:
        print(f"✅ EXCELLENT: Feature extraction <5s for {max_parts} parts!")
    else:
        print(f"⚠️  Feature extraction: {max_feature:.2f}s")
    
    if total_memory < 50:
        print(f"✅ EXCELLENT: Memory usage <50 MB for {max_parts} parts!")
    
    print("\n" + "="*70)
    print("  🎉 BASELINE ESTABLISHED - READY FOR COLLISION DETECTION!")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()

