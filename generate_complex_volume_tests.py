"""
Generate High-Volume Complex Test Files

This creates CHALLENGING test files with:
- 50+ parts per file
- 100+ parts per file  
- 200+ parts per file
- Mixed complexity (simple + complex shapes)
- Realistic part/sheet ratios for meaningful utilization

Purpose: PROVE the system scales and handles production volumes
"""

import ezdxf
import numpy as np
from pathlib import Path
from math import pi, cos, sin, sqrt
import random


def create_volume_test_directory():
    """Create directory for volume tests"""
    test_dir = Path("Test files/06_volume_tests")
    test_dir.mkdir(parents=True, exist_ok=True)
    return test_dir


def generate_50_mixed_parts(doc, msp, sheet_width=1220, sheet_height=2440):
    """
    Generate 50 mixed parts for standard sheet
    
    Mix includes:
    - 20 rectangles (various sizes)
    - 15 circles (various radii)
    - 10 L-shapes (brackets)
    - 5 complex shapes (multi-sided)
    
    Target: ~50% theoretical utilization
    """
    print("Generating 50 mixed parts...")
    
    parts_added = 0
    total_area = 0
    
    # 20 Rectangles (common production parts)
    print("  Adding rectangles...")
    rect_sizes = [
        (100, 80), (120, 60), (80, 80), (150, 100), (90, 70),
        (110, 85), (95, 75), (130, 90), (85, 65), (105, 95),
        (100, 80), (120, 60), (80, 80), (150, 100), (90, 70),  # Duplicates (realistic)
        (110, 85), (95, 75), (130, 90), (85, 65), (105, 95)
    ]
    
    for i, (w, h) in enumerate(rect_sizes):
        x = (i % 10) * 200
        y = (i // 10) * 200
        msp.add_lwpolyline([
            (x, y),
            (x + w, y),
            (x + w, y + h),
            (x, y + h),
            (x, y)
        ])
        parts_added += 1
        total_area += w * h
    
    # 15 Circles (holes, pins, etc.)
    print("  Adding circles...")
    circle_radii = [40, 35, 30, 25, 20] * 3
    for i, r in enumerate(circle_radii):
        x = 200 + (i % 5) * 120
        y = 500 + (i // 5) * 120
        msp.add_circle((x, y), radius=r)
        parts_added += 1
        total_area += pi * r * r
    
    # 10 L-shapes (brackets)
    print("  Adding L-shapes...")
    for i in range(10):
        x = 1000 + (i % 5) * 120
        y = 500 + (i // 5) * 200
        w, h = 80, 80
        leg = 30
        
        msp.add_lwpolyline([
            (x, y),
            (x + w, y),
            (x + w, y + leg),
            (x + leg, y + leg),
            (x + leg, y + h),
            (x, y + h),
            (x, y)
        ])
        parts_added += 1
        total_area += (w * leg) + (leg * (h - leg))
    
    # 5 Complex shapes (pentagons, hexagons)
    print("  Adding complex shapes...")
    for i in range(5):
        cx = 1500 + (i % 3) * 150
        cy = 1000 + (i // 3) * 150
        radius = 50
        sides = 6
        
        points = []
        for j in range(sides):
            angle = 2 * pi * j / sides
            x = cx + radius * cos(angle)
            y = cy + radius * sin(angle)
            points.append((x, y))
        points.append(points[0])
        
        msp.add_lwpolyline(points)
        parts_added += 1
        # Approximate area of regular polygon
        total_area += 0.5 * sides * radius * radius * sin(2 * pi / sides)
    
    sheet_area = sheet_width * sheet_height
    theoretical_util = (total_area / sheet_area) * 100
    
    print(f"  Parts: {parts_added}")
    print(f"  Total area: {total_area/100:.1f} cm²")
    print(f"  Theoretical utilization: {theoretical_util:.1f}%")
    
    return parts_added, theoretical_util


def generate_100_production_parts(doc, msp, sheet_width=1500, sheet_height=3000):
    """
    Generate 100 realistic production parts
    
    Simulates a real production batch with variety
    Target: ~60% theoretical utilization
    """
    print("Generating 100 production parts...")
    
    parts_added = 0
    total_area = 0
    random.seed(42)  # Reproducible
    
    # 60 Rectangles (most common)
    print("  Adding 60 rectangles...")
    for i in range(60):
        w = random.randint(50, 150)
        h = random.randint(40, 120)
        x = (i % 10) * 180
        y = (i // 10) * 180
        
        msp.add_lwpolyline([
            (x, y), (x + w, y), (x + w, y + h), (x, y + h), (x, y)
        ])
        parts_added += 1
        total_area += w * h
    
    # 25 Circles
    print("  Adding 25 circles...")
    for i in range(25):
        r = random.randint(15, 45)
        x = 300 + (i % 5) * 150
        y = 1500 + (i // 5) * 150
        msp.add_circle((x, y), radius=r)
        parts_added += 1
        total_area += pi * r * r
    
    # 15 L/T shapes
    print("  Adding 15 brackets...")
    for i in range(15):
        x = 1200 + (i % 5) * 150
        y = 1500 + (i // 5) * 200
        w = random.randint(60, 100)
        h = random.randint(60, 100)
        leg = random.randint(20, 40)
        
        if i % 2 == 0:  # L-shape
            msp.add_lwpolyline([
                (x, y), (x + w, y), (x + w, y + leg),
                (x + leg, y + leg), (x + leg, y + h), (x, y + h), (x, y)
            ])
            total_area += (w * leg) + (leg * (h - leg))
        else:  # T-shape
            msp.add_lwpolyline([
                (x, y), (x + w, y), (x + w, y + leg),
                (x + w - leg, y + leg), (x + w - leg, y + h),
                (x + leg, y + h), (x + leg, y + leg), (x, y + leg), (x, y)
            ])
            total_area += (w * leg) + (leg * (h - leg))
        
        parts_added += 1
    
    sheet_area = sheet_width * sheet_height
    theoretical_util = (total_area / sheet_area) * 100
    
    print(f"  Parts: {parts_added}")
    print(f"  Total area: {total_area/100:.1f} cm²")
    print(f"  Theoretical utilization: {theoretical_util:.1f}%")
    
    return parts_added, theoretical_util


def generate_200_small_parts(doc, msp, sheet_width=2000, sheet_height=3000):
    """
    Generate 200 small parts (realistic for batch production)
    
    Small parts: 20-60mm typical dimension
    Target: ~55% theoretical utilization
    """
    print("Generating 200 small parts...")
    
    parts_added = 0
    total_area = 0
    random.seed(123)
    
    print("  Adding 200 mixed small parts...")
    for i in range(200):
        part_type = i % 4
        
        x = (i % 20) * 120
        y = (i // 20) * 350
        
        if part_type == 0:  # Small rectangle
            w = random.randint(20, 50)
            h = random.randint(15, 40)
            msp.add_lwpolyline([
                (x, y), (x + w, y), (x + w, y + h), (x, y + h), (x, y)
            ])
            total_area += w * h
        
        elif part_type == 1:  # Small circle
            r = random.randint(10, 25)
            msp.add_circle((x + 25, y + 25), radius=r)
            total_area += pi * r * r
        
        elif part_type == 2:  # Small L-shape
            size = random.randint(30, 50)
            leg = random.randint(10, 20)
            msp.add_lwpolyline([
                (x, y), (x + size, y), (x + size, y + leg),
                (x + leg, y + leg), (x + leg, y + size), (x, y + size), (x, y)
            ])
            total_area += (size * leg) + (leg * (size - leg))
        
        else:  # Triangle
            size = random.randint(25, 45)
            msp.add_lwpolyline([
                (x, y), (x + size, y), (x + size/2, y + size * 0.866), (x, y)
            ])
            total_area += (size * size * sqrt(3) / 4)
        
        parts_added += 1
    
    sheet_area = sheet_width * sheet_height
    theoretical_util = (total_area / sheet_area) * 100
    
    print(f"  Parts: {parts_added}")
    print(f"  Total area: {total_area/100:.1f} cm²")
    print(f"  Theoretical utilization: {theoretical_util:.1f}%")
    
    return parts_added, theoretical_util


def generate_complex_irregular_50(doc, msp, sheet_width=1500, sheet_height=2000):
    """
    Generate 50 complex irregular shapes
    
    Focus on challenging geometry:
    - Concave shapes
    - Many vertices
    - Irregular outlines
    
    Target: ~45% theoretical utilization
    """
    print("Generating 50 complex irregular shapes...")
    
    parts_added = 0
    total_area = 0
    random.seed(456)
    
    shape_types = [
        'L', 'T', 'U', 'plus', 'star', 'gear', 'irregular_polygon'
    ]
    
    for i in range(50):
        shape_type = shape_types[i % len(shape_types)]
        x_base = (i % 10) * 180
        y_base = (i // 10) * 450
        
        if shape_type == 'L':
            w, h = random.randint(60, 100), random.randint(60, 100)
            leg = random.randint(25, 40)
            msp.add_lwpolyline([
                (x_base, y_base), (x_base + w, y_base), (x_base + w, y_base + leg),
                (x_base + leg, y_base + leg), (x_base + leg, y_base + h),
                (x_base, y_base + h), (x_base, y_base)
            ])
            total_area += (w * leg) + (leg * (h - leg))
        
        elif shape_type == 'T':
            w, h = random.randint(70, 110), random.randint(60, 90)
            leg = random.randint(25, 35)
            msp.add_lwpolyline([
                (x_base, y_base), (x_base + w, y_base), (x_base + w, y_base + leg),
                (x_base + w - leg, y_base + leg), (x_base + w - leg, y_base + h),
                (x_base + leg, y_base + h), (x_base + leg, y_base + leg),
                (x_base, y_base + leg), (x_base, y_base)
            ])
            total_area += (w * leg) + (leg * (h - leg))
        
        elif shape_type == 'U':
            w, h = random.randint(60, 90), random.randint(70, 100)
            thickness = random.randint(15, 25)
            msp.add_lwpolyline([
                (x_base, y_base), (x_base + w, y_base), (x_base + w, y_base + h),
                (x_base + w - thickness, y_base + h),
                (x_base + w - thickness, y_base + thickness),
                (x_base + thickness, y_base + thickness),
                (x_base + thickness, y_base + h),
                (x_base, y_base + h), (x_base, y_base)
            ])
            total_area += (w * h) - ((w - 2*thickness) * (h - thickness))
        
        elif shape_type == 'plus':
            size = random.randint(50, 80)
            arm = random.randint(15, 25)
            points = [
                (x_base + size/2 - arm/2, y_base),
                (x_base + size/2 + arm/2, y_base),
                (x_base + size/2 + arm/2, y_base + size/2 - arm/2),
                (x_base + size, y_base + size/2 - arm/2),
                (x_base + size, y_base + size/2 + arm/2),
                (x_base + size/2 + arm/2, y_base + size/2 + arm/2),
                (x_base + size/2 + arm/2, y_base + size),
                (x_base + size/2 - arm/2, y_base + size),
                (x_base + size/2 - arm/2, y_base + size/2 + arm/2),
                (x_base, y_base + size/2 + arm/2),
                (x_base, y_base + size/2 - arm/2),
                (x_base + size/2 - arm/2, y_base + size/2 - arm/2),
                (x_base + size/2 - arm/2, y_base)
            ]
            msp.add_lwpolyline(points)
            total_area += size * size - (size - arm) * (size - arm)
        
        elif shape_type == 'star':
            # 5-pointed star
            radius = random.randint(30, 50)
            cx = x_base + 60
            cy = y_base + 60
            points = []
            for j in range(10):
                angle = 2 * pi * j / 10 - pi/2
                r = radius if j % 2 == 0 else radius * 0.4
                points.append((cx + r * cos(angle), cy + r * sin(angle)))
            points.append(points[0])
            msp.add_lwpolyline(points)
            total_area += radius * radius * 0.5  # Approximate
        
        elif shape_type == 'gear':
            # Simple gear shape
            radius = random.randint(25, 40)
            cx = x_base + 60
            cy = y_base + 60
            teeth = 8
            points = []
            for j in range(teeth * 2):
                angle = 2 * pi * j / (teeth * 2)
                r = radius if j % 2 == 0 else radius * 0.85
                points.append((cx + r * cos(angle), cy + r * sin(angle)))
            points.append(points[0])
            msp.add_lwpolyline(points)
            total_area += pi * radius * radius * 0.9
        
        else:  # irregular_polygon
            # Random irregular shape
            cx = x_base + 60
            cy = y_base + 60
            num_sides = random.randint(5, 8)
            points = []
            for j in range(num_sides):
                angle = 2 * pi * j / num_sides
                r = random.randint(30, 50)
                points.append((cx + r * cos(angle), cy + r * sin(angle)))
            points.append(points[0])
            msp.add_lwpolyline(points)
            total_area += 2000  # Rough estimate
        
        parts_added += 1
    
    sheet_area = sheet_width * sheet_height
    theoretical_util = (total_area / sheet_area) * 100
    
    return parts_added, theoretical_util


def generate_100_rectangles_optimized(doc, msp, sheet_width=1500, sheet_height=3000):
    """
    Generate 100 rectangles optimized for packing
    
    Focus on testing pure packing efficiency
    Target: ~70% theoretical utilization
    """
    print("Generating 100 rectangles (optimized for packing)...")
    
    parts_added = 0
    total_area = 0
    random.seed(789)
    
    # Generate rectangles with sizes that pack well
    for i in range(100):
        # Vary sizes but keep them reasonable
        w = random.choice([50, 60, 70, 80, 90, 100, 110, 120])
        h = random.choice([40, 50, 60, 70, 80, 90])
        
        x = (i % 15) * 120
        y = (i // 15) * 120
        
        msp.add_lwpolyline([
            (x, y), (x + w, y), (x + w, y + h), (x, y + h), (x, y)
        ])
        parts_added += 1
        total_area += w * h
    
    sheet_area = sheet_width * sheet_height
    theoretical_util = (total_area / sheet_area) * 100
    
    print(f"  Parts: {parts_added}")
    print(f"  Total area: {total_area/100:.1f} cm²")
    print(f"  Theoretical utilization: {theoretical_util:.1f}%")
    
    return parts_added, theoretical_util


def generate_200_tiny_parts_grid(doc, msp, sheet_width=1000, sheet_height=1000):
    """
    Generate 200 tiny parts in grid
    
    Tests: Can system handle many small parts?
    Target: ~40% theoretical utilization
    """
    print("Generating 200 tiny parts...")
    
    parts_added = 0
    total_area = 0
    
    for i in range(200):
        size = 15 + (i % 10)  # 15-25mm
        x = (i % 20) * 60
        y = (i // 20) * 120
        
        # Alternate rectangles and circles
        if i % 2 == 0:
            msp.add_lwpolyline([
                (x, y), (x + size, y), (x + size, y + size),
                (x, y + size), (x, y)
            ])
            total_area += size * size
        else:
            msp.add_circle((x + size/2, y + size/2), radius=size/2)
            total_area += pi * (size/2) ** 2
        
        parts_added += 1
    
    sheet_area = sheet_width * sheet_height
    theoretical_util = (total_area / sheet_area) * 100
    
    print(f"  Parts: {parts_added}")
    print(f"  Theoretical utilization: {theoretical_util:.1f}%")
    
    return parts_added, theoretical_util


def main():
    """Generate all high-volume test files"""
    print("\n" + "="*70)
    print("  🔥 GENERATING HIGH-VOLUME COMPLEX TEST FILES")
    print("  (Testing system scalability and performance)")
    print("="*70 + "\n")
    
    test_dir = create_volume_test_directory()
    
    test_cases = [
        ("01_mixed_50_parts_1220x2440.dxf",
         lambda d, m: generate_50_mixed_parts(d, m, 1220, 2440),
         "50 mixed parts (rectangles, circles, L-shapes, complex)"),
        
        ("02_production_100_parts_1500x3000.dxf",
         lambda d, m: generate_100_production_parts(d, m, 1500, 3000),
         "100 realistic production parts (varied complexity)"),
        
        ("03_rectangles_100_optimized_1500x3000.dxf",
         lambda d, m: generate_100_rectangles_optimized(d, m, 1500, 3000),
         "100 rectangles (optimal packing test)"),
        
        ("04_tiny_200_parts_1000x1000.dxf",
         lambda d, m: generate_200_tiny_parts_grid(d, m, 1000, 1000),
         "200 tiny parts (scalability stress test)"),
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
        
        # Generate
        count, theoretical_util = generator(doc, msp)
        
        # Save
        filepath = test_dir / filename
        doc.saveas(filepath)
        
        print(f"✅ Saved: {filepath}")
        
        results.append({
            'filename': filename,
            'parts': count,
            'theoretical_util': theoretical_util,
            'description': description
        })
    
    # Summary
    print(f"\n{'='*70}")
    print("  📊 HIGH-VOLUME TEST FILES CREATED")
    print('='*70)
    
    total_parts = sum(r['parts'] for r in results)
    
    print(f"\nGenerated {len(results)} high-volume test files:")
    print(f"Total parts across all files: {total_parts}\n")
    
    for r in results:
        print(f"  ✅ {r['filename']}")
        print(f"     Parts: {r['parts']}, Theoretical: {r['theoretical_util']:.1f}%")
        print(f"     {r['description']}\n")
    
    print(f"💾 Files saved to: {test_dir}")
    print(f"\n🎯 These files will PROVE system scalability!")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()

