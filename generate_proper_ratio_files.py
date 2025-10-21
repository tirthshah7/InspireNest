"""
Generate Test Files with PROPER Part-to-Sheet Ratio

Previous files: 2-10% theoretical max (sheet too big!)
These files: 50-65% theoretical max (proper ratio for 40-55% target)

Strategy:
- Use medium sheet (800×600 = 480,000 sq mm)
- Generate LARGER parts (50-150mm base size, not 15-60mm)
- Target: 240,000-310,000 sq mm total area = 50-65% coverage
"""

import sys
import os
import math
import random

sys.path.insert(0, 'src')
import ezdxf
from ezdxf import units


class ProperRatioGenerator:
    """Generate files with proper part-to-sheet ratio"""
    
    def __init__(self, output_dir="Test files/07_proper_ratio"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        print(f"📁 Output directory: {self.output_dir}")
    
    def add_rectangle(self, msp, width, height, x=0, y=0):
        """Add rectangle"""
        points = [(x, y), (x + width, y), (x + width, y + height), (x, y + height), (x, y)]
        msp.add_lwpolyline(points, close=True)
    
    def add_circle(self, msp, radius, x=0, y=0):
        """Add circle"""
        msp.add_circle((x, y), radius)
    
    def add_l_shape(self, msp, width, height, thickness, x=0, y=0):
        """Add L-shape"""
        points = [
            (x, y), (x + width, y), (x + width, y + thickness),
            (x + thickness, y + thickness), (x + thickness, y + height),
            (x, y + height), (x, y)
        ]
        msp.add_lwpolyline(points, close=True)
    
    def generate_proper_ratio_file(self, target_coverage=0.55, filename="proper_ratio_50_parts.dxf"):
        """
        Generate file with proper part-to-sheet ratio.
        
        Args:
            target_coverage: Target area coverage (0.55 = 55% theoretical max)
            filename: Output filename
        """
        print(f"\n{'='*80}")
        print(f"Generating: {filename}")
        print(f"Target coverage: {target_coverage*100:.0f}%")
        print(f"{'='*80}")
        
        # Sheet size
        sheet_width = 800
        sheet_height = 600
        sheet_area = sheet_width * sheet_height
        
        print(f"Sheet: {sheet_width}×{sheet_height} = {sheet_area:,} sq mm")
        
        # Target total area
        target_total_area = sheet_area * target_coverage
        print(f"Target part area: {target_total_area:,.0f} sq mm ({target_coverage*100:.0f}% coverage)")
        
        # Create document
        doc = ezdxf.new('R2010', setup=True)
        doc.units = units.MM
        msp = doc.modelspace()
        
        # Part sizes - MUCH LARGER
        small_range = (40, 70)      # Small: 40-70mm (was 15-30)
        medium_range = (70, 110)    # Medium: 70-110mm (was 30-60)
        large_range = (110, 160)    # Large: 110-160mm (was 60-100)
        
        # Shapes
        shapes = ['rectangle', 'circle', 'l_shape']
        
        # Size distribution (balanced)
        size_dist = ['small'] * 40 + ['medium'] * 40 + ['large'] * 20
        
        # Generate parts until we reach target area
        x_offset = 0
        y_offset = 0
        row_height = 0
        max_width = 1000
        spacing = 10
        
        created_parts = 0
        total_area_created = 0
        
        while total_area_created < target_total_area and created_parts < 200:
            # Choose size
            size_cat = random.choice(size_dist)
            if size_cat == 'small':
                base_size = random.uniform(*small_range)
            elif size_cat == 'medium':
                base_size = random.uniform(*medium_range)
            else:
                base_size = random.uniform(*large_range)
            
            # Choose shape
            shape_type = random.choice(shapes)
            
            # Calculate approximate area for this part
            if shape_type == 'rectangle':
                aspect = random.uniform(1.5, 3.0)
                w, h = base_size * aspect, base_size
                part_area = w * h
            elif shape_type == 'circle':
                radius = base_size / 2
                part_area = math.pi * radius * radius
            elif shape_type == 'l_shape':
                thickness = base_size * 0.3
                # Approximate L-shape area
                part_area = base_size * base_size * 0.6
            
            # Check if adding this part would exceed target
            if total_area_created + part_area > target_total_area * 1.05:
                # Close to target, maybe add smaller part
                if size_cat != 'small':
                    continue
                else:
                    # Stop here
                    break
            
            # Create shape
            try:
                if shape_type == 'rectangle':
                    aspect = random.uniform(1.5, 3.0)
                    if random.random() < 0.5:
                        w, h = base_size * aspect, base_size
                    else:
                        w, h = base_size, base_size * aspect
                    self.add_rectangle(msp, w, h, x_offset, y_offset)
                    part_w, part_h = w, h
                    actual_area = w * h
                
                elif shape_type == 'circle':
                    radius = base_size / 2
                    self.add_circle(msp, radius, x_offset + radius, y_offset + radius)
                    part_w = part_h = base_size
                    actual_area = math.pi * radius * radius
                
                elif shape_type == 'l_shape':
                    thickness = base_size * 0.3
                    w, h = base_size, base_size * 1.2
                    self.add_l_shape(msp, w, h, thickness, x_offset, y_offset)
                    part_w, part_h = w, h
                    actual_area = w * h * 0.6  # Approx
                
                created_parts += 1
                total_area_created += actual_area
                
                # Update position
                x_offset += part_w + spacing
                row_height = max(row_height, part_h)
                
                if x_offset > max_width:
                    x_offset = 0
                    y_offset += row_height + spacing
                    row_height = 0
                
            except Exception as e:
                print(f"  ⚠️  Failed to create {shape_type}: {e}")
        
        actual_coverage = (total_area_created / sheet_area) * 100
        
        print(f"  ✅ Created: {created_parts} parts")
        print(f"  Total area: {total_area_created:,.0f} sq mm")
        print(f"  Actual coverage: {actual_coverage:.1f}%")
        
        if actual_coverage < 45:
            print(f"  ⚠️  Coverage < 45%, might not reach 40% target")
        elif actual_coverage > 70:
            print(f"  ⚠️  Coverage > 70%, parts might not fit!")
        else:
            print(f"  ✅ Coverage in good range (45-70%)!")
        
        # Save
        output_path = os.path.join(self.output_dir, filename)
        doc.saveas(output_path)
        print(f"  ✅ Saved: {output_path}")
        
        return output_path, created_parts, actual_coverage
    
    def generate_suite(self):
        """Generate suite of properly-sized files"""
        print("\n" + "="*80)
        print("🎯 GENERATING FILES WITH PROPER PART-TO-SHEET RATIO")
        print("="*80)
        print("\nTarget: 50-65% coverage for 40-55% achievable utilization")
        print("Sheet: 800×600mm (medium size)")
        print("Parts: LARGE (50-150mm, not 15-60mm)\n")
        
        configs = [
            (0.50, "proper_50pct_coverage.dxf"),
            (0.55, "proper_55pct_coverage.dxf"),
            (0.60, "proper_60pct_coverage.dxf"),
        ]
        
        generated = []
        
        for target_cov, filename in configs:
            try:
                path, parts, actual_cov = self.generate_proper_ratio_file(target_cov, filename)
                generated.append((path, parts, actual_cov))
            except Exception as e:
                print(f"❌ Failed: {e}")
        
        print(f"\n{'='*80}")
        print("✅ GENERATION COMPLETE")
        print(f"{'='*80}\n")
        
        print("Generated files:")
        for path, parts, cov in generated:
            print(f"  → {path.split('/')[-1]}: {parts} parts, {cov:.1f}% coverage")
        
        print(f"\n{'─'*80}")
        print("EXPECTED RESULTS on these files:")
        print("  → Fast Optimal: 35-45% utilization")
        print("  → Multi-Pass: 40-50% utilization")
        print("  → Target ACHIEVED: 40%+ is within reach!")
        print(f"{'─'*80}")
        
        return generated


def main():
    """Main"""
    print("\n" + "="*80)
    print("🎯 Proper Ratio Test File Generator")
    print("="*80)
    
    gen = ProperRatioGenerator()
    generated = gen.generate_suite()
    
    print("\n✅ Ready to test!")
    print("Run: python3 test_proper_ratio_files.py")


if __name__ == "__main__":
    main()

