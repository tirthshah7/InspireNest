"""
Test Configuration Loading System
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'src'))

from engine.config import load_config, NestingConfig
from constraints.material import list_materials

def test_config_file(filepath: str):
    """Test loading a config file"""
    print(f"\n{'='*70}")
    print(f"Testing: {filepath}")
    print('='*70)
    
    try:
        config = load_config(filepath)
        
        print(f"\n✅ Config loaded successfully!")
        print(f"\n{config}")
        
        print(f"\nDetailed Parameters:")
        print(f"  Sheet usable area: {config.sheet.usable_area/1000:.1f} cm²")
        print(f"  Total spacing: {config.spacing.total_spacing} mm")
        print(f"  Rotation options: {len(config.rotation.allowed_angles)}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Test all config files"""
    print("\n" + "="*70)
    print("  ⚙️  CONFIGURATION SYSTEM TEST")
    print("="*70)
    
    # Show available materials
    print("\n📦 Available Materials:")
    for material_name in list_materials():
        print(f"  • {material_name}")
    
    # Test config files
    config_files = [
        "Test files/01_simple/config_simple.json",
        "Test files/02_moderate/config_moderate.json",
        "Test files/03_complex/config_complex.json",
    ]
    
    results = []
    for filepath in config_files:
        success = test_config_file(filepath)
        results.append((filepath, success))
    
    # Summary
    print(f"\n{'='*70}")
    print("  📊 SUMMARY")
    print('='*70)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    print(f"\nTests Passed: {passed}/{total}\n")
    
    for filepath, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        filename = Path(filepath).name
        print(f"  {status}  {filename}")
    
    if passed == total:
        print(f"\n🎉 ALL CONFIG FILES VALID!")
        print(f"   Configuration system is WORKING!")
    
    print("="*70 + "\n")


if __name__ == "__main__":
    main()

