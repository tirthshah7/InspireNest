"""
Generate Realistic Test Files

Creates test files with PROPER part-to-sheet ratios
for meaningful utilization testing

Target: 60-80% theoretical maximum utilization
"""

import ezdxf
import numpy as np
from pathlib import Path
from math import pi, cos, sin


def create_realistic_directory():
    """Create realistic test directory"""
    test_dir = Path("Test files/05_realistic")
    test_dir.mkdir(parents=True, exist_ok=True)
    return test_dir


def generate_production_rectangles(doc, msp, sheet_width=600, sheet_height=400):
    """
    Generate realistic rectangle mix for small sheet
    
    Target: 50-60% theoretical utilization
    Mix of different sizes that might come from a real job
    """
    print("Generating production rectangles...")
    
    # Mix of sizes (mm)
    rectangles = [
        (80, 50),   # Large
        (80, 50),   # Large (duplicate)
        (60, 40),   # Medium
        (60, 40),   # Medium (duplicate)
        (60, 40),   # Medium (triplicate)
        (50, 30),   # Small
        (50, 30),   # Small (duplicate)
        (40, 25),   # Small
        (40, 25),   # Small
        (30, 20),   # Tiny
        (30, 20),   # Tiny
        (30, 20),   # Tiny
    ]
    
    total_area = sum(w * h for w, h in rectangles)
    sheet_area = sheet_width * sheet_height
    theoretical_util = (total_area / sheet_area) * 100
    
    print(f"  Rectangles: {len(rectangles)}")
    print(f"  Total area: {total_area} mm² ({total_area/100:.1f} cm²)")
    print(f"  Sheet area: {sheet_area} mm² ({sheet_area/100:.1f} cm²)")
    print(f"  Theoretical max utilization: {theoretical_util:.1f}%")
    
    # Add to DXF
    y_offset = 0
    for w, h in rectangles:
        msp.add_lwpolyline([
            (0, y_offset),
            (w, y_offset),
            (w, y_offset + h),
            (0, y_offset + h),
            (0, y_offset)
        ])
        y_offset += h + 10  # Spacing for visibility
    
    return len(rectangles), theoretical_util


def generate_mixed_production_parts(doc, msp, sheet_width=1220, sheet_height=2440):
    """
    Generate realistic mix for standard 4x8 sheet
    
    Target: 65-75% theoretical utilization
    Includes rectangles, circles, and L-shapes
    """
    print("Generating mixed production parts...")
    
    parts_added = 0
    total_area = 0
    
    # Rectangles (common)
    rect_sizes = [(100, 80), (120, 60), (80, 80), (150, 100), (90, 70)] * 4
    for i, (w, h) in enumerate(rect_sizes):
        x_offset = (i % 5) * 200
        y_offset = (i // 5) * 150
        msp.add_lwpolyline([
            (x_offset, y_offset),
            (x_offset + w, y_offset),
            (x_offset + w, y_offset + h),
            (x_offset, y_offset + h),
            (x_offset, y_offset)
        ])
        parts_added += 1
        total_area += w * h
    
    # Circles (less common but important)
    circle_radii = [40, 35, 30, 25, 20, 40, 35, 30]
    for i, r in enumerate(circle_radii):
        x = 200 + (i % 4) * 100
        y = 700 + (i // 4) * 100
        msp.add_circle((x, y), radius=r)
        parts_added += 1
        total_area += pi * r * r
    
    # L-shapes (brackets - realistic production)
    l_shapes = [
        # L-shape specifications: (width, height, leg_width, leg_height)
        (80, 80, 30, 30),
        (100, 100, 35, 35),
        (70, 70, 25, 25),
        (90, 90, 30, 30),
    ]
    
    for i, (w, h, lw, lh) in enumerate(l_shapes):
        x_offset = 600 + (i % 2) * 150
        y_offset = 700 + (i // 2) * 150
        
        msp.add_lwpolyline([
            (x_offset, y_offset),
            (x_offset + w, y_offset),
            (x_offset + w, y_offset + lh),
            (x_offset + lw, y_offset + lh),
            (x_offset + lw, y_offset + h),
            (x_offset, y_offset + h),
            (x_offset, y_offset)
        ])
        parts_added += 1
        # L area = total - cutout
        total_area += (w * h) - ((w - lw) * (h - lh))
    
    sheet_area = sheet_width * sheet_height
    theoretical_util = (total_area / sheet_area) * 100
    
    print(f"  Parts: {parts_added}")
    print(f"  Total area: {total_area/100:.1f} cm²")
    print(f"  Sheet area: {sheet_area/100:.1f} cm²")
    print(f"  Theoretical max utilization: {theoretical_util:.1f}%")
    
    return parts_added, theoretical_util


def generate_high_density_circles(doc, msp, sheet_width=600, sheet_height=400):
    """
    Generate many circles for packing optimization test
    
    Target: 70%+ theoretical (circle packing is hard!)
    """
    print("Generating high density circles...")
    
    # Pack circles in grid pattern
    radius = 25  # mm
    spacing = 5  # mm between circles
    
    parts_added = 0
    total_area = 0
    
    x = radius + 10
    while x < sheet_width - radius - 10:
        y = radius + 10
        while y < sheet_height - radius - 10:
            msp.add_circle((x, y), radius=radius)
            parts_added += 1
            total_area += pi * radius * radius
            y += 2 * radius + spacing
        x += 2 * radius + spacing
    
    sheet_area = sheet_width * sheet_height
    theoretical_util = (total_area / sheet_area) * 100
    
    print(f"  Circles: {parts_added}")
    print(f"  Radius: {radius} mm")
    print(f"  Total area: {total_area/100:.1f} cm²")
    print(f"  Theoretical max utilization: {theoretical_util:.1f}%")
    
    return parts_added, theoretical_util


def generate_irregular_mix(doc, msp, sheet_width=1000, sheet_height=1000):
    """
    Generate irregular shapes for advanced nesting test
    
    Target: 60-70% theoretical (irregular shapes are challenging)
    """
    print("Generating irregular mix...")
    
    parts_added = 0
    total_area = 0
    
    # T-shapes
    for i in range(8):
        x = (i % 4) * 200 + 50
        y = (i // 4) * 400 + 50
        
        points = [
            (x, y),
            (x + 60, y),
            (x + 60, y + 20),
            (x + 40, y + 20),
            (x + 40, y + 80),
            (x + 20, y + 80),
            (x + 20, y + 20),
            (x, y + 20),
            (x, y)
        ]
        msp.add_lwpolyline(points)
        parts_added += 1
        total_area += (60 * 20) + (20 * 60)  # T-shape area
    
    # U-shapes
    for i in range(6):
        x = (i % 3) * 300 + 50
        y = (i // 3) * 400 + 250
        
        points = [
            (x, y),
            (x + 70, y),
            (x + 70, y + 70),
            (x + 55, y + 70),
            (x + 55, y + 15),
            (x + 15, y + 15),
            (x + 15, y + 70),
            (x, y + 70),
            (x, y)
        ]
        msp.add_lwpolyline(points)
        parts_added += 1
        total_area += (70 * 70) - (40 * 55)  # U-shape area
    
    sheet_area = sheet_width * sheet_height
    theoretical_util = (total_area / sheet_area) * 100
    
    print(f"  Parts: {parts_added}")
    print(f"  Total area: {total_area/100:.1f} cm²")
    print(f"  Theoretical max utilization: {theoretical_util:.1f}%")
    
    return parts_added, theoretical_util


def main():
    """Generate all realistic test files"""
    print("\n" + "="*70)
    print("  📦 GENERATING REALISTIC TEST FILES")
    print("  (Proper part/sheet ratios for meaningful utilization)")
    print("="*70 + "\n")
    
    test_dir = create_realistic_directory()
    
    test_cases = [
        ("01_production_rectangles_600x400.dxf", 
         lambda d, m: generate_production_rectangles(d, m, 600, 400),
         "Realistic rectangle mix for small sheet"),
        
        ("02_mixed_production_1220x2440.dxf",
         lambda d, m: generate_mixed_production_parts(d, m, 1220, 2440),
         "Full production mix for standard 4x8 sheet"),
        
        ("03_high_density_circles_600x400.dxf",
         lambda d, m: generate_high_density_circles(d, m, 600, 400),
         "Circle packing optimization test"),
        
        ("04_irregular_mix_1000x1000.dxf",
         lambda d, m: generate_irregular_mix(d, m, 1000, 1000),
         "Irregular T and U shapes"),
    ]
    
    results = []
    
    for filename, generator, description in test_cases:
        print(f"\n{'─'*70}")
        print(f"Generating: {filename}")
        print(f"Purpose: {description}")
        print('─'*70)
        
        # Create new DXF
        doc = ezdxf.new('R2010')
        msp = doc.modelspace()
        
        # Generate entities
        count, theoretical_util = generator(doc, msp)
        
        # Save
        filepath = test_dir / filename
        doc.saveas(filepath)
        
        print(f"✅ Saved: {filepath}")
        print(f"   Parts: {count}, Target utilization: {theoretical_util:.1f}%")
        
        results.append((filename, count, theoretical_util, description))
    
    # Summary
    print(f"\n{'='*70}")
    print("  📊 GENERATION COMPLETE")
    print('='*70)
    
    print(f"\nGenerated {len(results)} realistic test files:\n")
    for filename, count, util, desc in results:
        print(f"  ✅ {filename:45s}")
        print(f"     {desc}")
        print(f"     Parts: {count:3d}, Target: {util:.1f}% utilization\n")
    
    print(f"💾 Files saved to: {test_dir}")
    print("\nThese files have REALISTIC part/sheet ratios!")
    print("Expected utilization after optimization: 60-80%")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()

