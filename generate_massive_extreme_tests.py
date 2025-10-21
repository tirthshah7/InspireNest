"""
Generate MASSIVE & EXTREMELY COMPLEX Test Files

This generates production-scale test files to push the system:
- 500 parts (real production batch)
- 750 parts (large batch)
- 1000 parts (stress test)
- Extreme complexity: gears, stars, brackets, irregular shapes
- Mixed sizes: 10mm to 500mm
- Realistic production scenarios

Purpose: PROVE system handles real-world scale and complexity
"""

import ezdxf
import numpy as np
from pathlib import Path
from math import pi, cos, sin, sqrt
import random


def create_massive_test_directory():
    """Create directory for massive scale tests"""
    test_dir = Path("Test files/07_massive_scale")
    test_dir.mkdir(parents=True, exist_ok=True)
    return test_dir


def generate_gear(cx, cy, outer_radius, teeth, tooth_depth=5):
    """Generate gear profile"""
    points = []
    for i in range(teeth * 2):
        angle = 2 * pi * i / (teeth * 2)
        r = outer_radius if i % 2 == 0 else outer_radius - tooth_depth
        x = cx + r * cos(angle)
        y = cy + r * sin(angle)
        points.append((x, y))
    points.append(points[0])
    return points


def generate_star(cx, cy, outer_r, inner_r, points_count=5):
    """Generate star shape"""
    pts = []
    for i in range(points_count * 2):
        angle = 2 * pi * i / (points_count * 2) - pi/2
        r = outer_r if i % 2 == 0 else inner_r
        pts.append((cx + r * cos(angle), cy + r * sin(angle)))
    pts.append(pts[0])
    return pts


def generate_complex_bracket(x, y, size, complexity='medium'):
    """Generate complex bracket shapes"""
    points = []
    
    if complexity == 'simple':
        # L-bracket
        w, h = size, size
        leg = size // 3
        points = [
            (x, y), (x + w, y), (x + w, y + leg),
            (x + leg, y + leg), (x + leg, y + h), (x, y + h), (x, y)
        ]
    
    elif complexity == 'medium':
        # T-bracket with holes
        w, h = size, int(size * 0.8)
        leg = size // 4
        points = [
            (x, y), (x + w, y), (x + w, y + leg),
            (x + w - leg, y + leg), (x + w - leg, y + h),
            (x + leg, y + h), (x + leg, y + leg), (x, y + leg), (x, y)
        ]
    
    else:  # complex
        # Multi-step bracket
        w = size
        points = [
            (x, y), (x + w, y), (x + w, y + w//4),
            (x + w*0.7, y + w//4), (x + w*0.7, y + w//2),
            (x + w*0.4, y + w//2), (x + w*0.4, y + w*0.75),
            (x + w*0.2, y + w*0.75), (x + w*0.2, y + w),
            (x, y + w), (x, y)
        ]
    
    return points


def generate_irregular_polygon(cx, cy, avg_radius, sides, irregularity=0.3):
    """Generate irregular polygon"""
    points = []
    for i in range(sides):
        angle = 2 * pi * i / sides
        r = avg_radius * (1 + random.uniform(-irregularity, irregularity))
        points.append((cx + r * cos(angle), cy + r * sin(angle)))
    points.append(points[0])
    return points


def generate_500_production_batch(doc, msp, sheet_width=2000, sheet_height=3000):
    """
    500 parts - Real production batch
    
    Mix:
    - 200 simple parts (rectangles, circles)
    - 150 brackets (L, T, U shapes)
    - 100 complex parts (gears, stars)
    - 50 irregular shapes
    
    Size range: 20mm - 300mm
    Target: ~45% theoretical utilization
    """
    print("Generating 500-part PRODUCTION batch...")
    
    parts_added = 0
    total_area = 0
    random.seed(500)
    
    # 200 Simple parts (rectangles and circles)
    print("  Adding 200 simple parts...")
    for i in range(200):
        x = (i % 25) * 100
        y = (i // 25) * 500
        
        if i % 2 == 0:  # Rectangle
            w = random.randint(30, 150)
            h = random.randint(25, 100)
            msp.add_lwpolyline([
                (x, y), (x + w, y), (x + w, y + h), (x, y + h), (x, y)
            ])
            total_area += w * h
        else:  # Circle
            r = random.randint(15, 60)
            msp.add_circle((x + 40, y + 40), radius=r)
            total_area += pi * r * r
        
        parts_added += 1
    
    # 150 Brackets (varied complexity)
    print("  Adding 150 brackets...")
    for i in range(150):
        x = 2600 + (i % 20) * 130
        y = (i // 20) * 500
        size = random.randint(50, 120)
        complexity = random.choice(['simple', 'medium', 'complex'])
        
        points = generate_complex_bracket(x, y, size, complexity)
        msp.add_lwpolyline(points)
        
        # Approximate area
        total_area += size * size * 0.6
        parts_added += 1
    
    # 100 Complex parts (gears and stars)
    print("  Adding 100 complex parts...")
    for i in range(100):
        x = 5200 + (i % 15) * 150
        y = (i // 15) * 600
        
        if i % 2 == 0:  # Gear
            teeth = random.randint(8, 16)
            radius = random.randint(25, 60)
            points = generate_gear(x + 70, y + 70, radius, teeth)
            msp.add_lwpolyline(points)
            total_area += pi * radius * radius * 0.85
        else:  # Star
            outer = random.randint(30, 70)
            inner = outer * random.uniform(0.4, 0.6)
            points = generate_star(x + 70, y + 70, outer, inner, 5)
            msp.add_lwpolyline(points)
            total_area += outer * outer * 1.5
        
        parts_added += 1
    
    # 50 Irregular shapes
    print("  Adding 50 irregular shapes...")
    for i in range(50):
        x = 7500 + (i % 8) * 180
        y = (i // 8) * 650
        sides = random.randint(5, 12)
        radius = random.randint(30, 80)
        
        points = generate_irregular_polygon(x + 90, y + 90, radius, sides, 0.4)
        msp.add_lwpolyline(points)
        total_area += radius * radius * 2.5
        parts_added += 1
    
    sheet_area = sheet_width * sheet_height
    theoretical_util = (total_area / sheet_area) * 100
    
    print(f"  Total parts: {parts_added}")
    print(f"  Total area: {total_area/100:.1f} cm²")
    print(f"  Theoretical utilization: {theoretical_util:.1f}%")
    
    return parts_added, theoretical_util


def generate_750_mixed_complexity(doc, msp, sheet_width=2500, sheet_height=4000):
    """
    750 parts - Large batch with mixed complexity
    
    Extreme variety to test all algorithms
    """
    print("Generating 750-part MIXED COMPLEXITY batch...")
    
    parts_added = 0
    total_area = 0
    random.seed(750)
    
    shape_types = [
        'rect', 'circle', 'L_bracket', 'T_bracket', 'U_bracket',
        'gear', 'star', 'hexagon', 'irregular', 'complex_bracket'
    ]
    
    print("  Adding 750 mixed parts...")
    for i in range(750):
        shape_type = random.choice(shape_types)
        
        x = (i % 35) * 120
        y = (i // 35) * 250
        
        if shape_type == 'rect':
            w, h = random.randint(20, 100), random.randint(15, 80)
            msp.add_lwpolyline([
                (x, y), (x + w, y), (x + w, y + h), (x, y + h), (x, y)
            ])
            total_area += w * h
        
        elif shape_type == 'circle':
            r = random.randint(10, 50)
            msp.add_circle((x + 30, y + 30), radius=r)
            total_area += pi * r * r
        
        elif 'bracket' in shape_type:
            size = random.randint(40, 100)
            complexity = random.choice(['simple', 'medium', 'complex'])
            points = generate_complex_bracket(x, y, size, complexity)
            msp.add_lwpolyline(points)
            total_area += size * size * 0.6
        
        elif shape_type == 'gear':
            teeth = random.randint(6, 14)
            radius = random.randint(20, 50)
            points = generate_gear(x + 50, y + 50, radius, teeth, tooth_depth=4)
            msp.add_lwpolyline(points)
            total_area += pi * radius * radius * 0.85
        
        elif shape_type == 'star':
            outer = random.randint(25, 60)
            inner = outer * random.uniform(0.3, 0.5)
            pts_count = random.choice([5, 6, 7, 8])
            points = generate_star(x + 50, y + 50, outer, inner, pts_count)
            msp.add_lwpolyline(points)
            total_area += outer * outer * 1.2
        
        elif shape_type == 'hexagon':
            radius = random.randint(20, 60)
            points = []
            for j in range(6):
                angle = 2 * pi * j / 6
                points.append((x + 50 + radius * cos(angle), y + 50 + radius * sin(angle)))
            points.append(points[0])
            msp.add_lwpolyline(points)
            total_area += radius * radius * 2.6
        
        else:  # irregular
            sides = random.randint(5, 10)
            radius = random.randint(25, 60)
            points = generate_irregular_polygon(x + 50, y + 50, radius, sides, 0.5)
            msp.add_lwpolyline(points)
            total_area += radius * radius * 2.0
        
        parts_added += 1
    
    sheet_area = sheet_width * sheet_height
    theoretical_util = (total_area / sheet_area) * 100
    
    print(f"  Total parts: {parts_added}")
    print(f"  Total area: {total_area/100:.1f} cm²")
    print(f"  Theoretical utilization: {theoretical_util:.1f}%")
    
    return parts_added, theoretical_util


def generate_1000_stress_test(doc, msp, sheet_width=3000, sheet_height=5000):
    """
    1000 parts - STRESS TEST
    
    Maximum scale test - can the system handle it?
    """
    print("Generating 1000-part STRESS TEST batch...")
    
    parts_added = 0
    total_area = 0
    random.seed(1000)
    
    print("  Adding 1000 parts (this will take a moment)...")
    for i in range(1000):
        # Progress indicator
        if i % 100 == 0 and i > 0:
            print(f"    Progress: {i}/1000 parts...")
        
        x = (i % 40) * 100
        y = (i // 40) * 250
        
        # Varied sizes and shapes
        part_type = i % 5
        
        if part_type == 0:  # Small rectangle
            w, h = random.randint(15, 60), random.randint(12, 50)
            msp.add_lwpolyline([
                (x, y), (x + w, y), (x + w, y + h), (x, y + h), (x, y)
            ])
            total_area += w * h
        
        elif part_type == 1:  # Circle
            r = random.randint(8, 40)
            msp.add_circle((x + 30, y + 30), radius=r)
            total_area += pi * r * r
        
        elif part_type == 2:  # Bracket
            size = random.randint(30, 80)
            points = generate_complex_bracket(x, y, size, 'simple')
            msp.add_lwpolyline(points)
            total_area += size * size * 0.6
        
        elif part_type == 3:  # Gear
            teeth = random.randint(6, 12)
            radius = random.randint(15, 45)
            points = generate_gear(x + 40, y + 40, radius, teeth, tooth_depth=3)
            msp.add_lwpolyline(points)
            total_area += pi * radius * radius * 0.85
        
        else:  # Irregular
            sides = random.randint(5, 8)
            radius = random.randint(20, 50)
            points = generate_irregular_polygon(x + 40, y + 40, radius, sides, 0.4)
            msp.add_lwpolyline(points)
            total_area += radius * radius * 2.0
        
        parts_added += 1
    
    sheet_area = sheet_width * sheet_height
    theoretical_util = (total_area / sheet_area) * 100
    
    print(f"  Total parts: {parts_added}")
    print(f"  Total area: {total_area/100:.1f} cm²")
    print(f"  Theoretical utilization: {theoretical_util:.1f}%")
    
    return parts_added, theoretical_util


def main():
    """Generate all massive scale test files"""
    print("\n" + "="*70)
    print("  🔥 GENERATING MASSIVE EXTREME COMPLEXITY TEST FILES")
    print("  (STRESS TESTING - Production Scale)")
    print("="*70 + "\n")
    
    test_dir = create_massive_test_directory()
    
    test_cases = [
        ("01_production_500_parts_2000x3000.dxf",
         lambda d, m: generate_500_production_batch(d, m, 2000, 3000),
         "500 parts - Real production batch (mixed complexity)"),
        
        ("02_large_batch_750_parts_2500x4000.dxf",
         lambda d, m: generate_750_mixed_complexity(d, m, 2500, 4000),
         "750 parts - Large batch (extreme variety)"),
        
        ("03_stress_test_1000_parts_3000x5000.dxf",
         lambda d, m: generate_1000_stress_test(d, m, 3000, 5000),
         "1000 parts - STRESS TEST (maximum scale)"),
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
    print("  📊 MASSIVE SCALE TEST FILES CREATED")
    print('='*70)
    
    total_parts = sum(r['parts'] for r in results)
    
    print(f"\nGenerated {len(results)} massive test files:")
    print(f"Total parts across all files: {total_parts}\n")
    
    for r in results:
        print(f"  ✅ {r['filename']}")
        print(f"     Parts: {r['parts']}, Theoretical: {r['theoretical_util']:.1f}%")
        print(f"     {r['description']}\n")
    
    print(f"💾 Files saved to: {test_dir}")
    print(f"\n🔥 READY TO STRESS TEST THE SYSTEM!")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()

