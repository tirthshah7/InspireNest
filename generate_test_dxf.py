"""
Generate Challenging Test DXF Files

This creates stress-test cases for robust validation:
1. Tiny parts (precision test)
2. Large parts (scale test)
3. Many vertices (complexity test)
4. Complex curves (approximation test)
5. Holes (topology test)
6. Irregular concave shapes (NFP test)
7. Very thin parts (constraint test)
"""

import ezdxf
from ezdxf import colors
import numpy as np
from math import pi, cos, sin
from pathlib import Path

def create_test_directory():
    """Create test directory"""
    test_dir = Path("Test files/04_stress_test")
    test_dir.mkdir(parents=True, exist_ok=True)
    return test_dir

def generate_tiny_parts(doc, msp):
    """Generate very small parts (5mm - 10mm) to test precision"""
    print("Generating tiny parts...")
    
    # Tiny rectangle: 5mm x 3mm
    msp.add_lwpolyline([
        (10, 10),
        (15, 10),
        (15, 13),
        (10, 13),
        (10, 10)
    ])
    
    # Tiny circle: 2mm radius
    msp.add_circle((25, 11.5), radius=2)
    
    # Tiny triangle: 4mm sides
    msp.add_lwpolyline([
        (35, 10),
        (39, 10),
        (37, 13.46),
        (35, 10)
    ])
    
    return 3

def generate_large_parts(doc, msp):
    """Generate large parts (500mm+) to test scale"""
    print("Generating large parts...")
    
    # Large rectangle: 600mm x 400mm
    msp.add_lwpolyline([
        (0, 0),
        (600, 0),
        (600, 400),
        (0, 400),
        (0, 0)
    ])
    
    # Large circle: 150mm radius
    msp.add_circle((800, 200), radius=150)
    
    return 2

def generate_high_vertex_count(doc, msp):
    """Generate shapes with many vertices (100+)"""
    print("Generating high vertex count shapes...")
    
    # Star with 50 points
    points = []
    outer_radius = 50
    inner_radius = 25
    for i in range(50):
        angle = 2 * pi * i / 50
        radius = outer_radius if i % 2 == 0 else inner_radius
        x = 100 + radius * cos(angle)
        y = 100 + radius * sin(angle)
        points.append((x, y))
    points.append(points[0])  # Close
    msp.add_lwpolyline(points)
    
    # Gear-like shape with many teeth
    points = []
    for i in range(72):  # 72 points = detailed gear
        angle = 2 * pi * i / 72
        radius = 40 + (5 if i % 3 == 0 else 0)  # Teeth
        x = 250 + radius * cos(angle)
        y = 100 + radius * sin(angle)
        points.append((x, y))
    points.append(points[0])
    msp.add_lwpolyline(points)
    
    return 2

def generate_complex_curves(doc, msp):
    """Generate shapes with arcs, splines, ellipses"""
    print("Generating complex curves...")
    
    # Shape with multiple arcs
    start_x, start_y = 10, 10
    
    # Arc 1
    msp.add_arc(
        center=(30, 10),
        radius=20,
        start_angle=180,
        end_angle=0
    )
    
    # Arc 2
    msp.add_arc(
        center=(50, 30),
        radius=20,
        start_angle=270,
        end_angle=90
    )
    
    # Ellipse
    msp.add_ellipse(
        center=(100, 30),
        major_axis=(30, 0),
        ratio=0.5
    )
    
    # Spline (curved shape)
    control_points = [
        (150, 10),
        (160, 30),
        (170, 15),
        (180, 40),
        (190, 10)
    ]
    msp.add_spline(control_points, degree=3)
    
    return 4

def generate_shapes_with_holes(doc, msp):
    """Generate shapes with holes (topology test)"""
    print("Generating shapes with holes...")
    
    # Rectangle with circular hole
    outer = msp.add_lwpolyline([
        (10, 10),
        (80, 10),
        (80, 60),
        (10, 60),
        (10, 10)
    ])
    
    # Hole (circle)
    msp.add_circle((45, 35), radius=10)
    
    # Washer (circle with hole)
    msp.add_circle((120, 35), radius=25)
    msp.add_circle((120, 35), radius=10)
    
    # Rectangle with rectangular hole
    msp.add_lwpolyline([
        (160, 10),
        (220, 10),
        (220, 60),
        (160, 60),
        (160, 10)
    ])
    msp.add_lwpolyline([
        (175, 25),
        (205, 25),
        (205, 45),
        (175, 45),
        (175, 25)
    ])
    
    return 6

def generate_irregular_concave(doc, msp):
    """Generate irregular concave shapes (NFP challenge)"""
    print("Generating irregular concave shapes...")
    
    # L-shape
    msp.add_lwpolyline([
        (10, 10),
        (40, 10),
        (40, 30),
        (25, 30),
        (25, 40),
        (10, 40),
        (10, 10)
    ])
    
    # T-shape
    msp.add_lwpolyline([
        (60, 10),
        (100, 10),
        (100, 25),
        (85, 25),
        (85, 50),
        (75, 50),
        (75, 25),
        (60, 25),
        (60, 10)
    ])
    
    # U-shape
    msp.add_lwpolyline([
        (120, 10),
        (160, 10),
        (160, 50),
        (145, 50),
        (145, 25),
        (135, 25),
        (135, 50),
        (120, 50),
        (120, 10)
    ])
    
    # Plus/Cross shape
    msp.add_lwpolyline([
        (190, 25),
        (205, 25),
        (205, 10),
        (220, 10),
        (220, 25),
        (235, 25),
        (235, 40),
        (220, 40),
        (220, 55),
        (205, 55),
        (205, 40),
        (190, 40),
        (190, 25)
    ])
    
    return 4

def generate_thin_parts(doc, msp):
    """Generate very thin parts (constraint challenge)"""
    print("Generating thin parts...")
    
    # Thin strip: 50mm x 2mm
    msp.add_lwpolyline([
        (10, 10),
        (60, 10),
        (60, 12),
        (10, 12),
        (10, 10)
    ])
    
    # Thin ring
    msp.add_circle((90, 20), radius=15)
    msp.add_circle((90, 20), radius=13)
    
    # Thin web structure
    # Vertical bars
    for x in [120, 130, 140, 150]:
        msp.add_lwpolyline([
            (x, 10),
            (x+1, 10),
            (x+1, 30),
            (x, 30),
            (x, 10)
        ])
    
    # Horizontal connector
    msp.add_lwpolyline([
        (120, 19),
        (151, 19),
        (151, 21),
        (120, 21),
        (120, 19)
    ])
    
    return 7

def generate_mixed_scales(doc, msp):
    """Generate parts with wildly different scales together"""
    print("Generating mixed scale parts...")
    
    # Tiny: 3mm square
    msp.add_lwpolyline([
        (10, 10),
        (13, 10),
        (13, 13),
        (10, 13),
        (10, 10)
    ])
    
    # Small: 20mm circle
    msp.add_circle((30, 20), radius=10)
    
    # Medium: 50mm rectangle
    msp.add_lwpolyline([
        (60, 10),
        (110, 10),
        (110, 40),
        (60, 40),
        (60, 10)
    ])
    
    # Large: 150mm circle
    msp.add_circle((250, 100), radius=75)
    
    # Huge: 300mm x 200mm
    msp.add_lwpolyline([
        (400, 10),
        (700, 10),
        (700, 210),
        (400, 210),
        (400, 10)
    ])
    
    return 5

def main():
    """Generate all test files"""
    print("\n" + "="*70)
    print("  🔧 GENERATING STRESS TEST DXF FILES")
    print("="*70 + "\n")
    
    test_dir = create_test_directory()
    
    test_cases = [
        ("01_tiny_parts.dxf", generate_tiny_parts, "Precision test - very small parts"),
        ("02_large_parts.dxf", generate_large_parts, "Scale test - very large parts"),
        ("03_high_vertex_count.dxf", generate_high_vertex_count, "Complexity test - 100+ vertices"),
        ("04_complex_curves.dxf", generate_complex_curves, "Curve handling - arcs, splines, ellipses"),
        ("05_shapes_with_holes.dxf", generate_shapes_with_holes, "Topology test - holes and washers"),
        ("06_irregular_concave.dxf", generate_irregular_concave, "NFP challenge - L, T, U, + shapes"),
        ("07_thin_parts.dxf", generate_thin_parts, "Constraint challenge - thin webs"),
        ("08_mixed_scales.dxf", generate_mixed_scales, "Scale variance - 3mm to 300mm together"),
    ]
    
    results = []
    
    for filename, generator, description in test_cases:
        print(f"\nGenerating: {filename}")
        print(f"Purpose: {description}")
        
        # Create new DXF
        doc = ezdxf.new('R2010')
        msp = doc.modelspace()
        
        # Generate entities
        count = generator(doc, msp)
        
        # Save
        filepath = test_dir / filename
        doc.saveas(filepath)
        
        print(f"✅ Saved: {filepath} ({count} entities)")
        results.append((filename, count, description))
    
    # Summary
    print(f"\n{'='*70}")
    print("  📊 GENERATION COMPLETE")
    print('='*70)
    print(f"\nGenerated {len(results)} stress test files:")
    for filename, count, desc in results:
        print(f"  ✅ {filename:30s} - {desc}")
    
    print(f"\n💾 Files saved to: {test_dir}")
    print("="*70 + "\n")

if __name__ == "__main__":
    main()

