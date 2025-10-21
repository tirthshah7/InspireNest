"""
Generate Dense Test DXF Files using ezdxf

This script generates test files with 50-200 parts of varying sizes and shapes
using ezdxf (no FreeCAD needed!). These files will have proper part-to-sheet ratios
where 40-60% utilization is theoretically achievable.

Usage:
    python3 generate_dense_dxf_files.py
"""

import sys
import os
import math
import random

sys.path.insert(0, 'src')

import ezdxf
from ezdxf import units


class DenseTestGenerator:
    """Generate test DXF files with dense part layouts"""
    
    def __init__(self, output_dir="Test files/06_dense_layouts"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        print(f"📁 Output directory: {self.output_dir}")
    
    def add_rectangle(self, msp, width, height, x=0, y=0):
        """Add a rectangle to modelspace"""
        points = [
            (x, y),
            (x + width, y),
            (x + width, y + height),
            (x, y + height),
            (x, y)  # Close
        ]
        msp.add_lwpolyline(points, close=True)
    
    def add_circle(self, msp, radius, x=0, y=0):
        """Add a circle to modelspace"""
        msp.add_circle((x, y), radius)
    
    def add_l_shape(self, msp, width, height, thickness, x=0, y=0):
        """Add an L-shape to modelspace"""
        points = [
            (x, y),
            (x + width, y),
            (x + width, y + thickness),
            (x + thickness, y + thickness),
            (x + thickness, y + height),
            (x, y + height),
            (x, y)  # Close
        ]
        msp.add_lwpolyline(points, close=True)
    
    def add_t_shape(self, msp, width, height, thickness, x=0, y=0):
        """Add a T-shape to modelspace"""
        points = [
            (x, y),
            (x + width, y),
            (x + width, y + thickness),
            (x + width/2 + thickness/2, y + thickness),
            (x + width/2 + thickness/2, y + height),
            (x + width/2 - thickness/2, y + height),
            (x + width/2 - thickness/2, y + thickness),
            (x, y + thickness),
            (x, y)  # Close
        ]
        msp.add_lwpolyline(points, close=True)
    
    def add_u_shape(self, msp, width, height, thickness, x=0, y=0):
        """Add a U-shape to modelspace"""
        points = [
            (x, y),
            (x + thickness, y),
            (x + thickness, y + height - thickness),
            (x + width - thickness, y + height - thickness),
            (x + width - thickness, y),
            (x + width, y),
            (x + width, y + height),
            (x, y + height),
            (x, y)  # Close
        ]
        msp.add_lwpolyline(points, close=True)
    
    def add_hexagon(self, msp, radius, x=0, y=0):
        """Add a hexagon to modelspace"""
        points = []
        for i in range(6):
            angle = math.pi / 3 * i
            px = x + radius * math.cos(angle)
            py = y + radius * math.sin(angle)
            points.append((px, py))
        msp.add_lwpolyline(points, close=True)
    
    def add_triangle(self, msp, size, x=0, y=0):
        """Add an equilateral triangle to modelspace"""
        h = size * math.sqrt(3) / 2
        points = [
            (x, y),
            (x + size, y),
            (x + size/2, y + h),
        ]
        msp.add_lwpolyline(points, close=True)
    
    def add_slot(self, msp, width, height, radius, x=0, y=0):
        """Add a slotted rectangle (rounded ends)"""
        # This creates a rectangle with circular ends
        # Simplified as rectangle + circles for now
        points = [
            (x + radius, y),
            (x + width - radius, y),
            (x + width - radius, y + height),
            (x + radius, y + height),
        ]
        msp.add_lwpolyline(points, close=True)
        # Add rounded ends
        msp.add_arc((x + radius, y + height/2), radius, 90, 270)
        msp.add_arc((x + width - radius, y + height/2), radius, 270, 90)
    
    def generate_dense_mixed_file(self, num_parts=100, filename="dense_100_parts.dxf"):
        """
        Generate a DXF file with many mixed parts.
        
        Parts are sized for ~50-60% sheet coverage (target: 40-55% utilization).
        """
        print(f"\n{'='*80}")
        print(f"Generating: {filename}")
        print(f"Target: {num_parts} parts")
        print(f"{'='*80}")
        
        # Create new DXF document
        doc = ezdxf.new('R2010', setup=True)
        doc.units = units.MM
        msp = doc.modelspace()
        
        # Part size ranges
        small_range = (15, 30)      # Small: 15-30mm
        medium_range = (30, 60)     # Medium: 30-60mm
        large_range = (60, 100)     # Large: 60-100mm
        
        # Shape types
        shapes = ['rectangle', 'circle', 'l_shape', 't_shape', 'u_shape', 
                 'hexagon', 'triangle', 'slot']
        
        # Size distribution (more variety)
        size_distribution = ['small'] * 50 + ['medium'] * 40 + ['large'] * 10
        
        # Layout parameters (simple grid for generation - will be scattered by nester)
        x_offset = 0
        y_offset = 0
        row_height = 0
        max_width = 800
        spacing = 5
        
        created_parts = 0
        
        for i in range(num_parts):
            # Choose size
            size_cat = random.choice(size_distribution)
            if size_cat == 'small':
                base_size = random.uniform(*small_range)
            elif size_cat == 'medium':
                base_size = random.uniform(*medium_range)
            else:
                base_size = random.uniform(*large_range)
            
            # Choose shape
            shape_type = random.choice(shapes)
            
            # Create shape
            try:
                if shape_type == 'rectangle':
                    aspect = random.uniform(1.2, 3.5)
                    if random.random() < 0.5:
                        w, h = base_size * aspect, base_size
                    else:
                        w, h = base_size, base_size * aspect
                    self.add_rectangle(msp, w, h, x_offset, y_offset)
                    part_w, part_h = w, h
                
                elif shape_type == 'circle':
                    radius = base_size / 2
                    self.add_circle(msp, radius, x_offset + radius, y_offset + radius)
                    part_w = part_h = base_size
                
                elif shape_type == 'l_shape':
                    thickness = base_size * random.uniform(0.25, 0.35)
                    w, h = base_size, base_size * random.uniform(1.1, 1.4)
                    self.add_l_shape(msp, w, h, thickness, x_offset, y_offset)
                    part_w, part_h = w, h
                
                elif shape_type == 't_shape':
                    thickness = base_size * random.uniform(0.25, 0.35)
                    w, h = base_size * random.uniform(1.2, 1.5), base_size
                    self.add_t_shape(msp, w, h, thickness, x_offset, y_offset)
                    part_w, part_h = w, h
                
                elif shape_type == 'u_shape':
                    thickness = base_size * random.uniform(0.2, 0.3)
                    w, h = base_size, base_size * random.uniform(0.8, 1.0)
                    self.add_u_shape(msp, w, h, thickness, x_offset, y_offset)
                    part_w, part_h = w, h
                
                elif shape_type == 'hexagon':
                    radius = base_size / 2
                    self.add_hexagon(msp, radius, x_offset + radius, y_offset + radius)
                    part_w = part_h = base_size
                
                elif shape_type == 'triangle':
                    self.add_triangle(msp, base_size, x_offset, y_offset)
                    part_w = base_size
                    part_h = base_size * 0.866
                
                elif shape_type == 'slot':
                    w = base_size * random.uniform(2.0, 3.5)
                    h = base_size * 0.6
                    radius = h / 2
                    self.add_slot(msp, w, h, radius, x_offset, y_offset)
                    part_w, part_h = w, h
                
                created_parts += 1
                
                # Update position
                x_offset += part_w + spacing
                row_height = max(row_height, part_h)
                
                if x_offset > max_width:
                    x_offset = 0
                    y_offset += row_height + spacing
                    row_height = 0
                
            except Exception as e:
                print(f"  ⚠️  Failed to create {shape_type}: {e}")
        
        print(f"  ✅ Created: {created_parts} parts")
        
        # Save DXF
        output_path = os.path.join(self.output_dir, filename)
        doc.saveas(output_path)
        print(f"  ✅ Saved: {output_path}")
        
        return output_path, created_parts
    
    def generate_test_suite(self):
        """Generate complete suite of dense test files"""
        print("\n" + "="*80)
        print("🔷 GENERATING DENSE TEST FILES (using ezdxf)")
        print("="*80)
        print("\nTarget: 50-200 parts per file for 40-60% utilization testing\n")
        
        test_configs = [
            (50, "dense_50_parts.dxf"),
            (75, "dense_75_parts.dxf"),
            (100, "dense_100_parts.dxf"),
            (150, "dense_150_parts.dxf"),
            (200, "dense_200_parts.dxf"),
        ]
        
        generated_files = []
        total_parts = 0
        
        for num_parts, filename in test_configs:
            try:
                output_path, created = self.generate_dense_mixed_file(num_parts, filename)
                generated_files.append((output_path, created))
                total_parts += created
            except Exception as e:
                print(f"❌ Failed to generate {filename}: {e}")
                import traceback
                traceback.print_exc()
        
        print(f"\n{'='*80}")
        print("✅ GENERATION COMPLETE")
        print(f"{'='*80}")
        print(f"\nGenerated {len(generated_files)} test files with {total_parts} total parts:")
        for path, count in generated_files:
            print(f"  → {path} ({count} parts)")
        
        print(f"\n{'─'*80}")
        print("EXPECTED RESULTS:")
        print("  → Theoretical max: 50-65% (proper part-to-sheet ratio)")
        print("  → NFP nester target: 35-50% (commercial-grade!)")
        print("  → Multi-Pass target: 30-45%")
        print(f"{'─'*80}")
        
        print(f"\nNEXT STEP: Test these files!")
        print("  python3 test_dense_files_with_nfp.py")
        
        return generated_files


def main():
    """Main execution"""
    print("\n" + "="*80)
    print("🔷 Dense DXF Test File Generator")
    print("="*80)
    print(f"\nUsing: ezdxf (no FreeCAD needed!)")
    print(f"Python: {sys.version.split()[0]}")
    
    generator = DenseTestGenerator()
    generated_files = generator.generate_test_suite()
    
    print("\n✅ All done!")
    print(f"\nGenerated {len(generated_files)} dense test files.")
    print("These files should enable 40-60% utilization testing! 🎉")


if __name__ == "__main__":
    main()

